import re
import sys
import xapian
import os
import os.path
from gzip import GzipFile
import logging
from rules import *

log = logging.getLogger(__name__)

class Matcher(object):
    "Match packages across distros"
    def __init__(self, distros, pivot):
        self.distros = [d for d in distros if d is not pivot]
        self.pivot = pivot
        self.count_all = 0
        self.count_matchcounts = dict([(x, 0) for x in range(len(self.distros)+1)])
        self.counts = dict()
        self.methods = []
        for m in ["byname", "bydesktop", "bypc", "bystem_libdevel", "bystem_shlib", "bystem_perl", "bystem_python"]:
            self.methods.append((m, getattr(self, "match_"+m)))
        self.fuzzy_methods = []
        for m in ["bybin", "byshlib", "bydevlib", "byman", "bypymod"]:
            self.fuzzy_methods.append((m, getattr(self, "match_"+m)))
        for mname, meth in self.methods + self.fuzzy_methods:
            self.counts[mname] = 0

    def stats(self, out=sys.stderr):
        "Print stats for all available distributions"
        self.pivot.stats(out)
        for d in self.distros:
            d.stats(out)

    def match_byname(self, name):
        "Match packages by name"
        res = dict()
        for d in self.distros:
            doc = d.document_for(name)
            if doc is not None:
                res[d.name] = [doc.get_data()]
        if not res: return None
        return res

    def match_bycontents(self, name, kind):
        # Get the package info in the starting distro
        srcdoc = self.pivot.document_for(name)
        if srcdoc is None:
            raise KeyError("Package %s not found" % name)

        # Get the file terms in the document
        pfx = CONTENT_INFO[kind].pfx
        files = []
        for t in srcdoc.termlist():
            if t.term.startswith(pfx):
                files.append(t.term)

        # Query each distro for what packages have those files
        res = dict()
        for d in self.distros:
            enq = xapian.Enquire(d.db)
            enq.set_query(xapian.Query(xapian.Query.OP_OR, files))
            mset = enq.get_mset(0, 20)
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

    def match_byman(self, name):
        "Match packages by man pages contained within"
        return self.match_bycontents(name, 'man')

    def match_bypymod(self, name):
        "Match packages by python module files contained within"
        return self.match_bycontents(name, 'py')

    def match_bystemmer(self, name, pfx):
        stemmed = self.pivot.stem(name, pfx)
        if not stemmed: return None
        term = [pfx + s for s in stemmed]

        # Query the stemmed form in each distro
        res = dict()
        for d in self.distros:
            enq = xapian.Enquire(d.db)
            enq.set_query(xapian.Query(xapian.Query.OP_OR, term))
            mset = enq.get_mset(0, 10)
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

    def match_bystem_perl(self, name):
        "Match stemmed form of perl library package names"
        return self.match_bystemmer(name, 'ZPL')

    def match_bystem_python(self, name):
        "Match stemmed form of python library package names"
        return self.match_bystemmer(name, 'ZPY')

    def match(self, name):
        "If some match is possible, return a dict(distro=set(names))"
        self.count_all += 1
        # Try with exact methods
        attempts = []
        for mname, meth in self.methods:
            res = meth(name)
            if res:
                self.counts[mname] += 1
                attempts.append(res)
        # Try with fuzzy methods
        #attempts_fuzzy = []
        for mname, meth in self.fuzzy_methods:
            res = meth(name)
            if res:
                self.counts[mname] += 1
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
        for m, meth in self.methods:
            doc = getattr(self, "match_" + m).__doc__
            print >>out, "%d matched by %s" % (self.counts[m], doc)
        for i in range(len(self.distros)+1):
            print >>out, "%d matched %d distro%s" % (self.count_matchcounts[i], i, 's' if i != 1 else '')
