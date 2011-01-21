import re
import sys
import xapian
import os
import os.path
from gzip import GzipFile
import logging

log = logging.getLogger(__name__)

# Stemming prefixes:
# ZDL: development libraries
# ZSL: shared libraries
STEMMERS = {
        "debian": {
            'ZDL': [
                     re.compile('^lib(.+?)-dev$'),
                     re.compile('^lib(.+?)[.0-9-]*-dev$'),
                   ],
            'ZSL': [
                     re.compile('^lib(.+?\d)$'),
                     re.compile('^lib(.+?)[.0-9-]*$'),
                   ],
        },
        "fedora": {
            'ZDL': [
                     re.compile('^(?:lib)?(.+?)-devel$'),
                     re.compile('^(?:lib)?(.+?)[.0-9-]*-devel$'),
                   ],
            'ZSL': [
                     re.compile('^(.+?)-libs$'),
                     re.compile('^(.+?)[.0-9-]*-libs$'),
                   ],
        },
        "mandriva": {
            'ZDL': [
                     re.compile('^lib(?:64)?(.+?)-devel$'),
                     re.compile('^lib(?:64)?(.+?)\d.+-devel$'),
                   ],
            'ZSL': [
                     re.compile('^lib(?:64)?(.+?\d)$'), 
                     re.compile('^lib(?:64)?(.+?)\d(.+\d)?$'), 
                   ],
        },
        "suse": {
            'ZDL': [ re.compile('^lib(?:64)?(.+?)-devel$'), ],
            'ZSL': [ re.compile('^lib(?:64)?(.+?\d)$'), ],
        },
}

class UserError(Exception):
    """
    Exception that does not cause a backtrace, but shows as an error message to
    the user
    """
    pass

def read_filelist(src):
    "Read a compressed package->file content list"
    fd = GzipFile(src, "r")
    for line in fd:
        name, path = line.strip().split(None, 1)
        name = name.lower()
        yield name, path

class ContentMatch(object):
    def __init__(self, pfx, regexp):
        self.pfx = pfx
        self.regexp = regexp

    def match(self, fname):
        mo = self.regexp.match(fname)
        if mo: return mo.group(1)
        return None

class Distro(object):
    "Package information from one distro"

    # What we consider interesting in package contents lists
    CONTENT_INFO = {
            # .desktop files
            'desktop': ContentMatch('XFD', re.compile(r"^.+/(.+\.desktop)$")),
            # executable commands
            'bin': ContentMatch('XFB', re.compile(r"^(?:[./]*)usr/bin/(.+)$")),
            # pkg-config metadata
            'pc': ContentMatch('XFPC', re.compile(r"^.+/pkgconfig/(.+)\.pc$")),
            # shared library info
            'shlib': ContentMatch('XFSL', re.compile(r"(?:[./]*)/usr/lib/(.+)\.so\.\d.+$")),
            # devel library info
            'devlib': ContentMatch('XFDL', re.compile(r"(?:[./]*)/usr/lib/(.+)\.a$")),
    }

    def __init__(self, name, reindex=False):
        self.name = name
        self.root = os.path.abspath("dist-" + name)
        self.dbpath = os.path.join(self.root, "db")
        self.stemmers = STEMMERS[name]
        if reindex or not os.path.exists(self.dbpath):
            self.index()
        self.db = xapian.Database(self.dbpath)

    def all_packages(self):
        "Return the set of all binary packages in this distro"
        return set([x.lower().strip().split()[0] for x in open(os.path.join(self.root, "binsrc"))])

    def filter_filelist(self):
        "Trim file lists extracting only 'interesting' files"
        log.info("%s: filtering file list", self.name)
        def do_filter():
            for name, fname in read_filelist(os.path.join(self.root, "files.gz")):
                for kind, matcher in self.CONTENT_INFO.iteritems():
                    m = matcher.match(fname)
                    if m:
                        yield name, kind, m
                        break

        # Read dist content information
        contents = dict()
        out = open(os.path.join(self.root, "interesting-files"), "w")
        for pkg, kind, fname in do_filter():
            print >>out, pkg, kind, fname
        out.close()

    def index(self):
        "Rebuild the Xapian index for this distro"
        log.info("%s: indexing data", self.name)
        pkgs = self.all_packages()
        log.info("%s: %d packages", self.name, len(pkgs))

        if not os.path.exists(os.path.join(os.path.join(self.root, "interesting-files"))):
            self.filter_filelist()

        # Read package contents information
        contents = dict()
        contents_stats = dict()
        for line in open(os.path.join(self.root, "interesting-files")):
            pkg, kind, fname = line.strip().lower().split(None, 2)
            if kind == 'desktop' and fname.startswith("fedora-"):
                fname = fname[7:]
            pkginfo = contents.setdefault(pkg, dict())
            pkginfo.setdefault(kind, set()).add(fname)
            if kind in contents_stats:
                contents_stats[kind] += 1
            else:
                contents_stats[kind] = 1
        for k, v in contents_stats.iteritems():
            log.info("%s: %d %s files", self.name, v, k)

        # Create a new database
        db = xapian.WritableDatabase(self.dbpath, xapian.DB_CREATE_OR_OVERWRITE)

        stem_stats = dict([(x, 0) for x in self.stemmers])
        for name in pkgs:
            doc = xapian.Document()
            doc.set_data(name)
            # Package name term
            doc.add_term("XP"+name)

            # Add stemmed forms of the package name
            for pfx in self.stemmers:
                for t in self.stem(name, pfx):
                    doc.add_term(pfx + t)
                    stem_stats[pfx] += 1

            # Add package contents
            pkginfo = contents.get(name, dict())
            for kind, fnames in pkginfo.iteritems():
                pfx = self.CONTENT_INFO[kind].pfx
                for fn in fnames:
                    doc.add_term(pfx+fn)

            db.add_document(doc)

        for k, v in sorted(stem_stats.iteritems(), key=lambda x:x[0]):
            log.info("%s: stemmer %s matched %d names", self.name, k, v)

        db.flush()

    def stats(self, out=sys.stderr):
        "Print stats about the contents of this distro"
        print >>out, "%s: %d packages" % (self.name, len(self.all_packages()))
        def count_pfx(pfx):
            count = 0
            for t in self.db.allterms(v.pfx):
                count += 1
            return count
        info = [(k, count_pfx(v.pfx)) for k, v in self.CONTENT_INFO.iteritems()]
        print >>out, "%s: %s files" % (self.name, ", ".join(["%d %s" % (c, n) for n, c in info]))

    def document_for(self, name):
        "Retrieve the Xapian document given the binary package name"
        enq = xapian.Enquire(self.db)
        enq.set_query(xapian.Query("XP"+name))
        mset = enq.get_mset(0, 1)
        for m in mset:
            return m.document
        return None

    def stem(self, name, pfx):
        """
        'stem' a package name according to the rules associated with the given
        prefix
        """
        res = set()
        for regex in self.stemmers[pfx]:
            mo = regex.match(name)
            if mo: res.add(mo.group(1))
        return res

class Matcher(object):
    "Match packages across distros"
    def __init__(self, distros, pivot):
        self.distros = [d for d in distros if d is not pivot]
        self.pivot = pivot
        self.count_all = 0
        self.count_matchcounts = dict([(x, 0) for x in range(len(self.distros)+1)])
        self.counts = dict()
        self.methods = ["byname", "bydesktop", "bypc", "bybin", "byshlib", "bydevlib", "bystem_libdevel", "bystem_shlib"]
        for m in self.methods:
            self.counts[m] = 0

    def stats(self, out=sys.stderr):
        "Print stats for all available distributions"
        self.pivot.stats(out)
        for d in self.distros:
            d.stats(out)

    def match_byname(self, name):
        "Match packages by name"
        res = dict()
        for d in self.distros:
            if d.db.get_termfreq('XP'+name) > 0:
                res[d.name] = [name]
        if not res: return None
        return res

    def match_bycontents(self, name, kind):
        # Get the package info in the starting distro
        srcdoc = self.pivot.document_for(name)
        if srcdoc is None:
            raise UserError("Package %s not found" % name)

        # Get the file terms in the document
        pfx = Distro.CONTENT_INFO[kind].pfx
        files = []
        for t in srcdoc.termlist():
            if t.term.startswith(pfx):
                files.append(t.term)

        # Query each distro for what packages have those files
        res = dict()
        for d in self.distros:
            enq = xapian.Enquire(d.db)
            enq.set_query(xapian.Query(xapian.Query.OP_OR, files))
            mset = enq.get_mset(0, 10)
            names = []
            for m in mset:
                names.append(m.document.get_data())
            if names:
                res[d.name] = names

        if 0:
            # If we don't find the .desktop file in all distros, print debugging
            # details
            if len(res) != len(self.distros):
                for d in desktops:
                    distros = [x.name for x in self.distros if d in x.desktop2pkg]
                    print kind, "file", d, "is only found in:", ",".join(distros)

        if not res: return None
        return res

    def match_bydesktop(self, name):
        "Match packages by desktop files contained within"
        return self.match_bycontents(name, 'desktop')

    def match_bypc(self, name):
        "Match packages by pkg-config metadata files contained within"
        return self.match_bycontents(name, 'pc')

    def match_bybin(self, name):
        "Match packages by [/usr]/bin files contained within"
        return self.match_bycontents(name, 'bin')

    def match_byshlib(self, name):
        "Match packages by shared library files contained within"
        return self.match_bycontents(name, 'shlib')

    def match_bydevlib(self, name):
        "Match packages by devel library files contained within"
        return self.match_bycontents(name, 'devlib')

    def match_bystemmer(self, name, pfx):
        stemmed = self.pivot.stem(name, pfx)
        if not stemmed: return None
        term = [pfx + s for s in stemmed]

        # Query the stemmed form in each distro
        res = dict()
        for d in self.distros:
            enq = xapian.Enquire(d.db)
            enq.set_query(xapian.Query(term))
            mset = enq.get_mset(0, 100)
            names = []
            for m in mset:
                names.append(m.document.get_data())
            if names:
                res[d.name] = names

        if not res: return None
        return res

    def match_bystem_libdevel(self, name):
        "Match stemmed form of development library package names"
        return self.match_bystemmer(name, 'ZDL')

    def match_bystem_shlib(self, name):
        "Match stemmed form of shared library package names"
        return self.match_bystemmer(name, 'ZSL')

    def match(self, name):
        "If some match is possible, return a dict(distro=set(names))"
        self.count_all += 1
        attempts = []
        for m in self.methods:
            res = getattr(self, "match_" + m)(name)
            if res:
                self.counts[m] += 1
                attempts.append(res)
        if not attempts:
            if 0:
                print "Not matched:", name
            self.count_matchcounts[0] += 1
            return None
        res = dict()
        for a in attempts:
            for k, v in a.iteritems():
                res.setdefault(k, set()).update(v)
        self.count_matchcounts[len(res)] += 1
        return res

    def match_stats(self, out=sys.stderr):
        "Print statistics about the matching operations so far"
        print >>out, "%d packages tested" % self.count_all
        print >>out, "Founds by method:"
        for m in self.methods:
            doc = getattr(self, "match_" + m).__doc__
            print >>out, "%d matched by %s" % (self.counts[m], doc)
        for i in range(len(self.distros)+1):
            print >>out, "%d matched %d distro%s" % (self.count_matchcounts[i], i, 's' if i != 1 else '')

class Distros(object):
    def __init__(self, reindex=False):
        # Definition of all the distros we know
        self.distros = [
            Distro("debian", reindex=reindex),
            Distro("fedora", reindex=reindex),
            Distro("mandriva", reindex=reindex),
            Distro("suse", reindex=reindex),
        ]
        self.distro_map = dict([(x.name, x) for x in self.distros])
