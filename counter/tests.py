# -*- coding: utf-8 -*-
import fnmatch
import os
import datetime
from django.conf import settings
import django.core.management
from django.test import TestCase
from counter.parser import LoglineParser, LoglineError


def setup_geoip():
    if not os.path.isfile(os.path.join(settings.GEOIP_PATH, 'GeoIP.dat')):
        django.core.management.call_command('geoip_update')


class CommandTestCase(TestCase):
    def setUp(self):
        setup_geoip()
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


class LoglineParserTestCase(TestCase):
    def setUp(self):
        setup_geoip()

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
        self.assertEqual(p.get_country(), None)
        self.assertEqual(p.protocol, 'HTTP/1.1')

    def test_parse_invalid_log(self):
        line = ''
        p = LoglineParser(line)
        self.assertRaises(LoglineError, p.match)
