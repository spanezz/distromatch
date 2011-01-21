# -*- coding: utf-8 -*-
import unittest
import sys, os.path
import dmatch

class TestStemmer(unittest.TestCase):
    def testDebian(self):
        d = dmatch.Distro("debian")
        self.assertEqual(sorted(d.stem('libdebtags0', 'ZSL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('libdebtags0-0', 'ZSL')), ["debtags", "debtags0-0"])

        self.assertEqual(sorted(d.stem('libdebtags-dev', 'ZDL')), ["debtags"])
        self.assertEqual(sorted(d.stem('libdebtags0-dev', 'ZDL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('libdebtags0.3-dev', 'ZDL')), ["debtags", "debtags0.3"])

    def testFedora(self):
        d = dmatch.Distro("fedora")
        self.assertEqual(sorted(d.stem('debtags-libs', 'ZSL')), ["debtags"])
        self.assertEqual(sorted(d.stem('debtags0-libs', 'ZSL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('debtags0.3-libs', 'ZSL')), ["debtags", "debtags0.3"])

        self.assertEqual(sorted(d.stem('debtags-devel', 'ZDL')), ["debtags"])
        self.assertEqual(sorted(d.stem('libdebtags-devel', 'ZDL')), ["debtags"])
        self.assertEqual(sorted(d.stem('debtags0-devel', 'ZDL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('libdebtags0-devel', 'ZDL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('debtags0.3-devel', 'ZDL')), ["debtags", "debtags0.3"])
        self.assertEqual(sorted(d.stem('libdebtags0.3-devel', 'ZDL')), ["debtags", "debtags0.3"])


if __name__ == '__main__':
    unittest.main()
