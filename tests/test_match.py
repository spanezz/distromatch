# -*- coding: utf-8 -*-
#
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

import unittest
import sys, os.path
import dmatch

class TestMatcherFromDebian(unittest.TestCase):
    def setUp(self):
        self.distros = dmatch.Distros()
        self.matcher = self.distros.make_matcher(start="debian")

    def testLibs(self):
        res = self.matcher.match("libgtkmm-dev")
        self.assertEqual(sorted(res["fedora"]), ["gtkmm24-devel"])
        self.assertEqual(sorted(res["mandriva"]), ["lib64gtkmm2.4-devel", "libgtkmm2.4-devel"])
        self.assertEqual(sorted(res["suse"]), ["gtkmm2-devel"])

        res = self.matcher.match("libdigest-sha1-perl")
        self.assertEqual(sorted(res["fedora"]), ["perl-Digest-SHA1"])
        self.assertEqual(sorted(res["mandriva"]), ["perl-Digest-SHA1"])
        self.assertEqual(sorted(res["suse"]), ["perl-Digest-SHA1"])

class TestMatcherFromFedora(unittest.TestCase):
    def setUp(self):
        self.distros = dmatch.Distros()
        self.matcher = self.distros.make_matcher(start="fedora")

    def testApps(self):
        res = self.matcher.match("openoffice.org-calc")
        self.assertEqual(sorted(res["debian"]), ["openoffice.org-calc"])
        self.assertEqual(sorted(res["mandriva"]), ["openoffice.org-calc"])
        self.assertEqual(sorted(res["suse"]), ["libreoffice-calc"])

        res = self.matcher.match("xpaint")
        self.assertEqual(sorted(res["debian"]), ["xpaint"])
        self.assertEqual(sorted(res["mandriva"]), ["xpaint"])
        self.assertEqual(sorted(res["suse"]), [])

    def testPython(self):
        res = self.matcher.match("xapian-bindings-python")
        self.assertEqual(sorted(res["debian"]), ["python-xapian"])
        self.assertEqual(sorted(res["mandriva"]), ["xapian-bindings-python"])
        self.assert_("suse" not in res)

    def testLibs(self):
        res = self.matcher.match("glibc")
        self.assert_("libc6" in res["debian"])
        self.assertEqual(sorted(res["mandriva"]), ["glibc"])
        self.assertEqual(sorted(res["suse"]), ["glibc"])

        # openssl in Fedora contains shared libraries, so it is correct to
        # match several shlib packages on other distros
        res = self.matcher.match("openssl")
        self.assertEqual(sorted(res["debian"]), ['libssl1.0.0', "openssl"])
        self.assertEqual(sorted(res["mandriva"]), ['lib64openssl1.0.0', 'libopenssl1.0.0', "openssl"])
        self.assertEqual(sorted(res["suse"]), ['libopenssl1_0_0', 'openssl', 'openssl-doc'])

if __name__ == '__main__':
    unittest.main()
