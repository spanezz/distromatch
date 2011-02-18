import re
import sys
import xapian
import os
import os.path
from gzip import GzipFile
import logging
from rules import *
import matcher

log = logging.getLogger(__name__)

def read_filelist(src):
    "Read a compressed package->file content list"
    fd = GzipFile(src, "r")
    for line in fd:
        name, path = line.strip().split(None, 1)
        name = name.lower()
        yield name, path

class Distro(object):
    "Package information from one distro"

    def __init__(self, name, style=None, reindex=False, root="."):
        if style is None:
            style_fname = os.path.join(root, "dist-"+name, "style")
            try:
                style = open(style_fname).read().strip()
            except Exception, e:
                if name in STEMMERS:
                    log.info("cannot read style file in %s: %s. Defaulting to %s", style_fname, str(e), name)
                    style = name
                else:
                    raise RuntimeError("cannot read style file in %s: %s" % (style_fname, str(e)))
        self.name = name
        self.style = style
        self.root = os.path.abspath(os.path.join(root, "dist-" + name))
        self.dbpath = os.path.join(self.root, "db")
        self.stemmers = STEMMERS[self.style]
        if reindex or not os.path.exists(self.dbpath):
            self.index()
        self.db = xapian.Database(self.dbpath)

    def has_package(self, name):
        "Check if this distribution has a package with the given name"
        enq = xapian.Enquire(self.db)
        enq.set_query(xapian.Query("XP"+name.lower()))
        mset = enq.get_mset(0, 1)
        for m in mset:
            return True
        return False

    def open_possibly_compressed(self, fname):
        if os.path.exists(fname):
            return open(fname)
        elif os.path.exists(fname + ".gz"):
            return GzipFile(fname + ".gz", "r")
        else:
            raise ValueError("%s: not found" % fname)

    def all_packages(self):
        "Return the set of all binary packages in this distro"
        fname = os.path.join(self.root, "binsrc")
        return set([x.strip().split()[0] for x in self.open_possibly_compressed(fname)])

    #def filter_filelist(self):
    #    "Trim file lists extracting only 'interesting' files"
    #    log.info("%s: filtering file list", self.name)
    #    def do_filter():
    #        for name, fname in read_filelist(os.path.join(self.root, "files.gz")):
    #            for kind, matcher in CONTENT_INFO.iteritems():
    #                m = matcher.match(fname)
    #                if m:
    #                    yield name, kind, m
    #                    break

    #    # Read dist content information
    #    contents = dict()
    #    out = open(os.path.join(self.root, "interesting-files"), "w")
    #    for pkg, kind, fname in do_filter():
    #        print >>out, pkg, kind, fname
    #    out.close()

    def index(self):
        "Rebuild the Xapian index for this distro"
        log.info("%s: indexing data", self.name)
        pkgs = self.all_packages()
        log.info("%s: %d packages", self.name, len(pkgs))

        #if not os.path.exists(os.path.join(os.path.join(self.root, "interesting-files"))):
        #    self.filter_filelist()

        # Read package contents information
        contents = dict()
        contents_stats = dict()
        fname = os.path.join(self.root, "interesting-files")
        for line in self.open_possibly_compressed(fname):
            pkg, kind, fname = line.strip().split(None, 2)
            if kind == 'desktop' and fname.lower().startswith("fedora-"):
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
            lname = name.lower()
            # Package name term
            doc.add_term("XP"+lname)

            # Add stemmed forms of the package name
            for pfx in self.stemmers:
                for t in self.stem(lname, pfx):
                    doc.add_term(pfx + t)
                    stem_stats[pfx] += 1

            # Add package contents
            pkginfo = contents.get(name, dict())
            for kind, fnames in pkginfo.iteritems():
                pfx = CONTENT_INFO[kind].pfx
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
        info = [(k, count_pfx(v.pfx)) for k, v in CONTENT_INFO.iteritems()]
        print >>out, "%s: %s files" % (self.name, ", ".join(["%d %s" % (c, n) for n, c in info]))

    def document_for(self, name):
        "Retrieve the Xapian document given the binary package name"
        enq = xapian.Enquire(self.db)
        enq.set_query(xapian.Query("XP"+name.lower()))
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
        for stemmer in self.stemmers[pfx]:
            stemmed = stemmer.stem(name)
            if stemmed: res.add(stemmed)
        return res

    def dump_info(self, name, out):
        """
        Dump all available information about the given package
        """
        re_pfx = re.compile("^([A-Z]+)(.+)$")
        doc = self.document_for(name)
        groups = {}
        for t in doc.termlist():
            mo = re_pfx.match(t.term)
            if mo:
                groups.setdefault(mo.group(1), []).append(mo.group(2))
            else:
                groups.setdefault(None, []).append(t.term)
        for group, terms in sorted(groups.iteritems(), key=lambda x:x[0]):
            if group is None:
                print >>out, "Other data:"
            else:
                title = PREFIX_DOC.get(group, group)
                print >>out, "%s:" % title
            for term in sorted(terms):
                print >>out, "\t%s" % term

class Distros(object):
    def __init__(self, reindex=False, root="."):
        # Definition of all the distros we know
        self.distros = []
        for d in os.listdir(root):
            if not d.startswith("dist-"): continue
            name = d[5:]
            try:
                self.distros.append(Distro(name, reindex=reindex, root=root))
            except Exception, e:
                log.info("cannot access distribution in %s: %s. skipping %s", d, str(e), name)
        self.distro_map = dict([(x.name, x) for x in self.distros])

    def make_matcher(self, start):
        # Pick the start distribution
        pivot = self.distro_map.get(start, None)
        if pivot is None:
            log.error("Distribution %s not found", start)
            return None

        # Instantiate the matcher engine
        return matcher.Matcher(self.distros, pivot)
