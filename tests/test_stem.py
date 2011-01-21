# -*- coding: utf-8 -*-
import unittest
import sys, os.path
import dmatch

class TestStemmer(unittest.TestCase):
    def testDebian(self):
        d = dmatch.Distro("debian")
        self.assertEqual(sorted(d.stem('libdebtags0', 'ZSL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('libdebtags0-d0', 'ZSL')), ["debtags", "debtags0-d0"])

        self.assertEqual(sorted(d.stem('libdebtags-dev', 'ZDL')), ["debtags"])
        self.assertEqual(sorted(d.stem('libdebtags0-dev', 'ZDL')), ["debtags", "debtags0"])
        self.assertEqual(sorted(d.stem('libdebtags0.3-dev', 'ZDL')), ["debtags", "debtags0.3"])


if __name__ == '__main__':
    unittest.main()
