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
                     REStemmer('^(.+?)-libs$'),
                     REStemmer('^(.+?)[.0-9_-]*-libs$'),
                   ],
            'ZPL': [ CPANStemmer('^perl-(.+)$'), ],
            'ZPY': [ REStemmer('^python-(.+)$'), ],
        },
}

class ContentMatch(object):
    def __init__(self, pfx, regexp):
        self.pfx = pfx
        self.regexp = regexp

    def match(self, fname):
        mo = self.regexp.match(fname)
        if mo: return mo.group(1)
        return None

# What we consider interesting in package contents lists
CONTENT_INFO = {
        # .desktop files
        'desktop': ContentMatch('XFD', re.compile(r"^[./]*usr/share/applications/(.+\.desktop)$")),
        # executable commands
        'bin': ContentMatch('XFB', re.compile(r"^[./]*(?:usr/)bin/(.+)$")),
        # pkg-config metadata
        'pc': ContentMatch('XFPC', re.compile(r"^.+/pkgconfig/(.+)\.pc$")),
        # shared library info
        'shlib': ContentMatch('XFSL', re.compile(r"^[./]*(?:usr/)?lib\d*/(lib.+\.so\.\d+).*$")),
        # devel library info
        'devlib': ContentMatch('XFDL', re.compile(r"^[./]*usr/lib\d*/(.+)\.a$")),
        # manpages
        'man': ContentMatch('XFMAN', re.compile(r"[./]*usr/share/man/(.+)$")),
        # python modules
        'py': ContentMatch('XFPY', re.compile(r"[./]*usr/(?:share|lib\d*)/python[0-9.]*/site-packages/(.+\.py)$")),
}

PREFIX_DOC = {
    "XP": "package name",
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

