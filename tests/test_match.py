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
        self.assertEqual(sorted(res["suse"]), ["gribc"])

        res = self.matcher.match("openssl")
        self.assertEqual(sorted(res["debian"]), ["openssl"])
        self.assertEqual(sorted(res["mandriva"]), ["openssl"])
        self.assertEqual(sorted(res["suse"]), ["openssl"])

if __name__ == '__main__':
    unittest.main()
