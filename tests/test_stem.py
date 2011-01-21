# -*- coding: utf-8 -*-
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
