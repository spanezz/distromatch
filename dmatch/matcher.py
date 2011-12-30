# distromatch - Match binary package names across distributions
#
# Copyright (C) 2011  Enrico Zini <enrico@enricozini.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import sys
import xapian
import os
import os.path
from gzip import GzipFile
import logging
from rules import *

log = logging.getLogger(__name__)

class Method(object):
    """
    Implementation of one match method
    """
    def prepare(self, name, d_from):
        """
        Prepare a query to match a name from d_from to multiple distros.

        The result is an opaque thing to pass to the prepared parameter of
        match.
        """
        return None

    def match(self, name, d_from, d_to, prepared=None):
        """
        Return the matches for 'name' from d_from to d_to.

        Set prepared to the result of the prepare method to speed up matching
        the same package for multiple distros
        """
        return []

class ByName(Method):
    """
    Match packages if the name is the same
    """
    name = "byname"

    def match(self, name, d_from, d_to, prepared=None):
        doc = d_to.document_for(name)
        if doc is not None:
            return [name]
        return []

    def get_doc(self):
        return "match packages by name"

class ByStemmer(Method):
    """
    Match packages by stemming their names
    """
    def __init__(self, pfx):
        self.name = "stem_" + pfx
        self.pfx = pfx

    def get_doc(self):
        return "match stemmed form of %s" % PREFIX_DOC[self.pfx]

    def prepare(self, name, d_from):
        return [self.pfx + s for s in d_from.stem(name, self.pfx)]

    def match(self, name, d_from, d_to, stemmed=None):
        if stemmed is None:
            stemmed = self.prepare(name, d_from)

        # Query the stemmed form in each distro
        enq = xapian.Enquire(d_to.db)
        enq.set_query(xapian.Query(xapian.Query.OP_OR, stemmed))
        mset = enq.get_mset(0, 10)
        names = []
        for m in mset:
            names.append(m.document.get_data())
        return names

class ByContents(Method):
    """
    Match packages by content
    """
    def __init__(self, kind):
        """
        Kind is the kind of content file that is matched
        """
        self.name = "file_" + kind
        self.kind = kind

    def get_doc(self):
        return "match packages by %s in contents" % CONTENT_INFO[self.kind].desc

    def prepare(self, name, d_from):
        # Get the package info in the starting distro
        srcdoc = d_from.document_for(name)
        if srcdoc is None:
            raise KeyError("Package %s not found in %s" % (name, d_from.name))

        # Get the file terms in the document
        pfx = CONTENT_INFO[self.kind].pfx
        files = []
        for t in srcdoc.termlist():
            if t.term.startswith(pfx):
                files.append(t.term)
        return files

    def match(self, name, d_from, d_to, files=None):
        if files is None:
            files = self.prepare(name, d_from)

        # Query each distro for what packages have those files
        enq = xapian.Enquire(d_to.db)
        enq.set_query(xapian.Query(xapian.Query.OP_OR, files))
        mset = enq.get_mset(0, 20)
        names = []
        for m in mset:
            names.append(m.document.get_data())
        return names


# TODO:
#  - remove for d in distro loop in all matchers (to allow efficient one-to-one
#    matching if not all distro matches are needed)
#  - turn matcher methods from methods to classes, to add a second match
#    methods to match source packages

class Matcher(object):
    "Match packages across distros"
    def __init__(self, distros, pivot):
        self.distros = [d for d in distros if d is not pivot]
        self.pivot = pivot
        self.count_all = 0
        self.count_matchcounts = dict([(x, 0) for x in range(len(self.distros)+1)])
        self.counts = dict()
        self.methods = []
        self.methods.append(ByName())
        self.methods.append(ByContents("desktop"))
        self.methods.append(ByContents("pc"))
        self.methods.append(ByStemmer("ZDL"))
        self.methods.append(ByStemmer("ZSL"))
        self.methods.append(ByStemmer("ZPL"))
        self.methods.append(ByStemmer("ZPY"))
        self.fuzzy_methods = []
        self.fuzzy_methods.append(ByContents("bin"))
        self.fuzzy_methods.append(ByContents("shlib"))
        self.fuzzy_methods.append(ByContents("devlib"))
        self.fuzzy_methods.append(ByContents("man"))
        self.fuzzy_methods.append(ByContents("py"))

        for meth in self.methods + self.fuzzy_methods:
            self.counts[meth.name] = 0

    def stats(self, out=sys.stderr):
        "Print stats for all available distributions"
        self.pivot.stats(out)
        for d in self.distros:
            d.stats(out)

    def do_method(self, name, meth, res):
        found = False
        for d in self.distros:
            data = meth.prepare(name, self.pivot)
            matches = meth.match(name, self.pivot, d, data)
            if matches:
                found = True
                res.setdefault(d.name, set()).update(matches)
        if found:
            self.counts[meth.name] += 1
        return found

    def match(self, name):
        "If some match is possible, return a dict(distro=set(names))"
        self.count_all += 1

        res = dict()
        found = False

        # Try with exact methods
        for meth in self.methods:
            if self.do_method(name, meth, res):
                found = True;

        # Try with fuzzy methods
        for meth in self.fuzzy_methods:
            if self.do_method(name, meth, res):
                found = True

        if not found:
            if 0:
                print "Not matched:", name
            self.count_matchcounts[0] += 1
            return None

        self.count_matchcounts[len(res)] += 1
        return res

    def match_stats(self, out=sys.stderr):
        "Print statistics about the matching operations so far"
        print >>out, "%d packages tested" % self.count_all
        print >>out, "Founds by method:"
        for meth in self.methods:
            print >>out, "%d matched by %s" % (self.counts[meth.name], meth.get_doc())
        for i in range(len(self.distros)+1):
            print >>out, "%d matched %d distro%s" % (self.count_matchcounts[i], i, 's' if i != 1 else '')
