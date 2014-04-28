# -*- coding: utf-8 -*-
import fnmatch
import os
import datetime
from django.conf import settings
import django.core.management
from django.test import TestCase
from counter.models import Filename
from counter.parser import LoglineParser, LoglineError


def setup_geoip():
    if not os.path.isfile(os.path.join(settings.GEOIP_PATH, 'GeoIP.dat')):
        django.core.management.call_command('geoip_update')


class GeoIPTestCase(TestCase):
    def setUp(self):
        setup_geoip()
        super(GeoIPTestCase, self).setUp()


class CommandTestCase(GeoIPTestCase):
    def setUp(self):
        super(CommandTestCase, self).setUp()
        self.logdir = os.path.join(os.path.dirname(__file__), "test/logs")
        self.valid_logs = os.path.join(self.logdir, "valid/")
        self.invalid_logs = os.path.join(self.logdir, "invalid/")

    def test_parse_valid_log(self):
        """Test the parse_log command."""

        for f in os.listdir(self.valid_logs):
            if not fnmatch.fnmatch(f, '*.log'):
                continue
            args = (os.path.join(self.valid_logs, f), )
            opts = {}
            print("Parsing log: {}".format(args[0]))
            django.core.management.call_command('parse_log', *args, **opts)


class LoglineParserTestCase(GeoIPTestCase):
    def test_parse_valid_log(self):
        line = '127.0.0.1 - - [01/Apr/2014:00:00:00 +0000] "GET /libreoffice/stable/4.2.2/win/x86/LibreOffice_4.2.2_Win_x86_helppack_en-US.msi HTTP/1.1" 302 1974 "http://documentfoundation.org/" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0"'
        p = LoglineParser(line)
        p.match()
        self.assertEqual(p.parse(), True)
        self.assertEqual(p.agent, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0')
        self.assertEqual(p.referrer, 'http://documentfoundation.org/')
        self.assertEqual(p.ip, '127.0.0.1')
        self.assertEqual(p.ident, '-')
        self.assertEqual(p.authuser, '-')
        self.assertEqual(p.method, 'GET')
        self.assertEqual(p.status, '302')
        self.assertEqual(p.size, '1974')
        self.assertEqual(p.datetime, '01/Apr/2014:00:00:00 +0000')
        self.assertIsInstance(p.get_date(), datetime.datetime)
        self.assertEqual(p.filename, 'LibreOffice_4.2.2_Win_x86_helppack_en-US.msi')
        self.assertIsNone(p.get_country())
        self.assertEqual(p.protocol, 'HTTP/1.1')

    def test_parse_invalid_log(self):
        line = ''
        p = LoglineParser(line)
        self.assertRaises(LoglineError, p.match)

    def test_working_extensions(self):
        line = '- - - [01/Apr/2014:00:00:00 +0000] "GET /folder/LibreOffice_4.2.2_Win_x86_helppack_en-US.{} HTTP/1.1" 301 1000 "" ""'
        working_extensions = ('gz', 'dmg', 'msi', 'exe', 'xz')
        for l in [line.format(ext) for ext in working_extensions]:
            p = LoglineParser(l)
            p.match()
            self.assertEqual(p.parse(), True)

    def test_invalid_extensions(self):
        line = '- - - [01/Apr/2014:00:00:00 +0000] "GET /folder/LibreOffice_4.2.2_Win_x86_helppack_en-US.{} HTTP/1.1" 301 1000 "" ""'
        working_extensions = ('asc', 'torrent', 'magnet', 'meta4', 'metalink', 'zsync', 'sha256', 'md5', 'sha1', 'btih')
        for l in [line.format(ext) for ext in working_extensions]:
            p = LoglineParser(l)
            p.match()
            self.assertEqual(p.parse(), False)



class FilenameParserTestCase(TestCase):
    def test_valid_filenames(self):
        filenames = {
            'LibreOffice_4.2.3_Linux_x86_deb.tar.gz': {
                'product': 'LibreOffice',
                'version': '4.2.3',
                'OS': 'Linux',
                'arch': 'x86',
                'language': None,
            },
            'LibreOffice_4.2.3_Linux_x86_deb_helppack_pt-BR.tar.gz': {
                'product': 'LibreOffice helppack',
                'version': '4.2.3',
                'OS': 'Linux',
                'arch': 'x86',
                'language': 'pt-BR',
            },
            'LibreOffice_4.2.3_Linux_x86_deb_langpack_zh-CN.tar.gz': {
                'product': 'LibreOffice langpack',
                'version': '4.2.3',
                'OS': 'Linux',
                'arch': 'x86',
                'language': 'zh-CN',
            },

        }
        for filename, info in filenames.iteritems():
            f, created = Filename.objects.get_or_create(name=filename)
            self.assertEqual(created, True)
            f.save()
            self.assertEqual(f.product.name, info['product'])
            self.assertEqual(f.version.name, info['version'])
            self.assertEqual(f.os.name, info['OS'])
            self.assertEqual(f.arch.name, info['arch'])
            if info['language']:
                self.assertEqual(f.language.name, info['language'])
            else:
                self.assertIsNone(f.language)



