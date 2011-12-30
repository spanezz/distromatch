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

class TestStemmer(unittest.TestCase):
    def testDebian(self):
        d = dmatch.Distro("debian")
        self.assertEqual(sorted(d.stem('libdebtags0', 'ZSL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('libdebtags0-0', 'ZSL')), ["debtags", "debtags0-0"])
        self.assertEqual(sorted(d.stem('libdebtags-0_0', 'ZSL')), ["debtags", "debtags-0_0"])
        self.assertEqual(sorted(d.stem('libfoo2bar0', 'ZSL')), ["foo2bar", "foo2bar0"])

        self.assertEqual(sorted(d.stem('libdebtags-dev', 'ZDL')), ["debtags"])
        self.assertEqual(sorted(d.stem('libdebtags0-dev', 'ZDL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('libdebtags0.3-dev', 'ZDL')), ["debtags", "debtags0.3"])
        self.assertEqual(sorted(d.stem('libdebtags-0_0-dev', 'ZDL')), ["debtags", "debtags-0_0"])
        self.assertEqual(sorted(d.stem('libfoo2bar0-dev', 'ZDL')), ["foo2bar", "foo2bar0"])

        self.assertEqual(sorted(d.stem('libfoo-bar-perl', 'ZPL')), ["foo-bar"]);
        self.assertEqual(sorted(d.stem('python-debtags', 'ZPY')), ["debtags"]);

    def testFedora(self):
        d = dmatch.Distro("fedora")
        self.assertEqual(sorted(d.stem('debtags-libs', 'ZSL')), ["debtags"])
        self.assertEqual(sorted(d.stem('debtags0-libs', 'ZSL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('debtags0.3-libs', 'ZSL')), ["debtags", "debtags0.3"])
        self.assertEqual(sorted(d.stem('debtags-0_0-libs', 'ZSL')), ["debtags", "debtags-0_0"])
        self.assertEqual(sorted(d.stem('foo2bar0-libs', 'ZSL')), ["foo2bar", "foo2bar0"])

        self.assertEqual(sorted(d.stem('debtags-devel', 'ZDL')), ["debtags"])
        self.assertEqual(sorted(d.stem('libdebtags-devel', 'ZDL')), ["debtags"])
        self.assertEqual(sorted(d.stem('debtags0-devel', 'ZDL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('libdebtags0-devel', 'ZDL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('debtags0.3-devel', 'ZDL')), ["debtags", "debtags0.3"])
        self.assertEqual(sorted(d.stem('libdebtags0.3-devel', 'ZDL')), ["debtags", "debtags0.3"])
        self.assertEqual(sorted(d.stem('debtags-0_0-devel', 'ZDL')), ["debtags", "debtags-0_0"])
        self.assertEqual(sorted(d.stem('libdebtags-0_0-devel', 'ZDL')), ["debtags", "debtags-0_0"])
        self.assertEqual(sorted(d.stem('foo2bar0-devel', 'ZDL')), ["foo2bar", "foo2bar0"])
        self.assertEqual(sorted(d.stem('libfoo2bar0-devel', 'ZDL')), ["foo2bar", "foo2bar0"])

        self.assertEqual(sorted(d.stem('perl-Foo-Bar', 'ZPL')), ["foo-bar"]);
        self.assertEqual(sorted(d.stem('debtags-python', 'ZPY')), ["debtags"]);
        self.assertEqual(sorted(d.stem('debtags-python2', 'ZPY')), ["debtags"]);

    def testMandriva(self):
        d = dmatch.Distro("mandriva")
        self.assertEqual(sorted(d.stem('libdebtags0', 'ZSL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('libdebtags0.3', 'ZSL')), ["debtags", "debtags0.3"])
        self.assertEqual(sorted(d.stem('libdebtags-0_0', 'ZSL')), ["debtags", "debtags-0_0"])
        self.assertEqual(sorted(d.stem('libfoo2bar0', 'ZSL')), ["foo2bar", "foo2bar0"])
        self.assertEqual(sorted(d.stem('lib64debtags0', 'ZSL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('lib64debtags0.3', 'ZSL')), ["debtags", "debtags0.3"])
        self.assertEqual(sorted(d.stem('lib64debtags-0_0', 'ZSL')), ["debtags", "debtags-0_0"])
        self.assertEqual(sorted(d.stem('lib64foo2bar0', 'ZSL')), ["foo2bar", "foo2bar0"])

        self.assertEqual(sorted(d.stem('libdebtags-devel', 'ZDL')), ["debtags"])
        self.assertEqual(sorted(d.stem('libdebtags0-devel', 'ZDL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('libdebtags0.3-devel', 'ZDL')), ["debtags", "debtags0.3"])
        self.assertEqual(sorted(d.stem('libdebtags-0_0-devel', 'ZDL')), ["debtags", "debtags-0_0"])
        self.assertEqual(sorted(d.stem('libfoo2bar0-devel', 'ZDL')), ["foo2bar", "foo2bar0"])
        self.assertEqual(sorted(d.stem('lib64debtags-devel', 'ZDL')), ["debtags"])
        self.assertEqual(sorted(d.stem('lib64debtags0-devel', 'ZDL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('lib64debtags0.3-devel', 'ZDL')), ["debtags", "debtags0.3"])
        self.assertEqual(sorted(d.stem('lib64debtags-0_0-devel', 'ZDL')), ["debtags", "debtags-0_0"])
        self.assertEqual(sorted(d.stem('lib64foo2bar0-devel', 'ZDL')), ["foo2bar", "foo2bar0"])

        self.assertEqual(sorted(d.stem('perl-Foo-Bar', 'ZPL')), ["foo-bar"]);
        self.assertEqual(sorted(d.stem('python-debtags', 'ZPY')), ["debtags"]);

    def testSuse(self):
        d = dmatch.Distro("suse")
        self.assertEqual(sorted(d.stem('debtags-libs', 'ZSL')), ["debtags"])
        self.assertEqual(sorted(d.stem('debtags0-libs', 'ZSL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('debtags0.3-libs', 'ZSL')), ["debtags", "debtags0.3"])
        self.assertEqual(sorted(d.stem('debtags-0_0-libs', 'ZSL')), ["debtags", "debtags-0_0"])
        self.assertEqual(sorted(d.stem('foo2bar0-libs', 'ZSL')), ["foo2bar", "foo2bar0"])

        self.assertEqual(sorted(d.stem('debtags-devel', 'ZDL')), ["debtags"])
        self.assertEqual(sorted(d.stem('libdebtags-devel', 'ZDL')), ["debtags"])
        self.assertEqual(sorted(d.stem('debtags0-devel', 'ZDL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('libdebtags0-devel', 'ZDL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('debtags0.3-devel', 'ZDL')), ["debtags", "debtags0.3"])
        self.assertEqual(sorted(d.stem('libdebtags0.3-devel', 'ZDL')), ["debtags", "debtags0.3"])
        self.assertEqual(sorted(d.stem('debtags-0_0-devel', 'ZDL')), ["debtags", "debtags-0_0"])
        self.assertEqual(sorted(d.stem('libdebtags-0_0-devel', 'ZDL')), ["debtags", "debtags-0_0"])
        self.assertEqual(sorted(d.stem('foo2bar0-devel', 'ZDL')), ["foo2bar", "foo2bar0"])
        self.assertEqual(sorted(d.stem('libfoo2bar0-devel', 'ZDL')), ["foo2bar", "foo2bar0"])

        self.assertEqual(sorted(d.stem('perl-Foo-Bar', 'ZPL')), ["foo-bar"]);
        self.assertEqual(sorted(d.stem('python-debtags', 'ZPY')), ["debtags"]);

if __name__ == '__main__':
    unittest.main()
