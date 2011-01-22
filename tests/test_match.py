# -*- coding: utf-8 -*-
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

if __name__ == '__main__':
    unittest.main()
