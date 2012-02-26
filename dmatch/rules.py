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

class REStemmer(object):
    def __init__(self, regex):
        self.re = re.compile(regex)
    def stem(self, word):
        mo = self.re.match(word)
        if mo: return mo.group(1)
        return None

class CPANStemmer(object):
    def __init__(self, regex):
        self.re = re.compile(regex)
    def cpan_norm(self, word):
        return re.sub(r"[:-]+", "-", word.lower())
    def stem(self, word):
        mo = self.re.match(word)
        if mo: return self.cpan_norm(mo.group(1))
        return None

# Stemming prefixes:
# ZDL: development libraries
# ZSL: shared libraries
# ZPL: perl modules
# ZPY: python modules
STEMMERS = {
        "debian": {
            'ZDL': [
                     REStemmer('^lib(.+?)-dev$'),
                     REStemmer('^lib(.+?)[.0-9_-]*-dev$'),
                   ],
            'ZSL': [
                     REStemmer('^lib(.+?\d)$'),
                     REStemmer('^lib(.+?)[.0-9_-]+$'),
                   ],
            'ZPL': [ CPANStemmer('^lib(.+)-perl$'), ],
            'ZPY': [ REStemmer('^python\d?-(.+)$'), ],
        },
        "fedora": {
            'ZDL': [
                     REStemmer('^(?:lib)?(.+?)-devel$'),
                     REStemmer('^(?:lib)?(.+?)[.0-9_-]*-devel$'),
                   ],
            'ZSL': [
                     REStemmer('^(.+?)-libs$'),
                     REStemmer('^(.+?)[.0-9_-]*-libs$'),
                   ],
            'ZPL': [ CPANStemmer('^perl-(.+)$'), ],
            'ZPY': [ REStemmer('^(.+)-python\d?$'), ],
        },
        "mandriva": {
            'ZDL': [
                     REStemmer('^lib(?:64)?(.+?)-devel$'),
                     REStemmer('^lib(?:64)?(.+?)[.0-9_-]*-devel$'),
                   ],
            'ZSL': [
                     REStemmer('^lib(?:64)?(.+?\d)$'), 
                     REStemmer('^lib(?:64)?(.+?)[.0-9_-]*?$'), 
                   ],
            'ZPL': [ CPANStemmer('^perl-(.+)$'), ],
            'ZPY': [ REStemmer('^python-(.+)$'), ],
        },
        "suse": {
            'ZDL': [
                     REStemmer('^(?:lib)?(.+?)-devel$'),
                     REStemmer('^(?:lib)?(.+?)[.0-9_-]*-devel$'),
                   ],
            'ZSL': [
                     REStemmer('^lib(.+?\d)$'),
                     REStemmer('^lib(.+?)[.0-9_-]+$'),
                   ],
            'ZPL': [ CPANStemmer('^perl-(.+)$'), ],
            'ZPY': [ REStemmer('^python-(.+)$'), ],
        },
}

class ContentMatch(object):
    def __init__(self, pfx, desc=None, match=None, sophie=None, rpm_md=None):
        self.pfx = pfx
        self.regexp = match
        self.desc = desc
        # SQL directory filter(s) (ORed togheter) to use when querying file
        # names from Sophie. BEWARE: they will not be SQL-escaped and will be
        # used as is
        self.sophie = sophie
        self.rpm_md = rpm_md

    def match(self, fname):
        mo = self.regexp.match(fname)
        if mo: return mo.group(1)
        return None

# What we consider interesting in package contents lists
CONTENT_INFO = {
        'desktop': ContentMatch('XFD', desc=".desktop files",
            match=re.compile(r"^[./]*usr/share/applications/(.+\.desktop)$"),
            sophie=dict(like=["/usr/share/applications/%"])),
        'bin': ContentMatch('XFB', desc="executable commands",
            match=re.compile(r"^[./]*(?:usr/)bin/(.+)$"),
            sophie=dict(eq=["/usr/bin/", "/bin/"])),
        'pc': ContentMatch('XFPC', desc="pkg-config metadata",
            match=re.compile(r"^.+/pkgconfig/(.+)\.pc$"),
            sophie=dict(eq=["/usr/share/pkgconfig/", "/usr/lib/pkgconfig/", "/usr/lib32/pkgconfig/", "/usr/lib64/pkgconfig/"]),
            rpm_md=re.compile(r"^pkgconfig\((.+)\)$")),
        'shlib': ContentMatch('XFSL', desc="shared library info",
            match=re.compile(r"^[./]*(?:usr/)?lib\d*/(lib.+\.so\.\d+).*$"),
            sophie=dict(eq=["/usr/lib/", "/usr/lib32/", "/usr/lib64/", "/lib/", "/lib32/", "/lib64/"]),
            rpm_md=re.compile(r"^(lib.+\.so\.\d+)$")),
        'devlib': ContentMatch('XFDL', desc="devel library info",
            match=re.compile(r"^[./]*usr/lib\d*/(.+)\.a$"),
            sophie=dict(eq=["/usr/lib/", "/usr/lib64/"])),
        'man': ContentMatch('XFMAN', desc="manpages",
            match=re.compile(r"[./]*usr/share/man/(.+)$"),
            sophie=dict(like=["/usr/share/man/%"])),
        'py': ContentMatch('XFPY', desc="python modules",
            match=re.compile(r"[./]*usr/(?:share|lib\d*)/python[0-9.]*/(?:site|dist)-packages/(.+\.py)$"),
            sophie=dict(like=["/usr/%/python%/site-packages/%"])),
}

PREFIX_DOC = {
    "XP": "package name",
    "XPS": "source package name",
    "ZDL": "development library name",
    "ZSL": "shared library name",
    "ZPL": "perl module name",
    "ZPY": "python module name",
    "XFD": ".desktop file",
    "XFB": "executable file",
    "XFPC": "pkg-config file",
    "XFSL": "shared library",
    "XFDL": "development library",
    "XFMAN": "man page",
    "XFPY": "python module",
}

