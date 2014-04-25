# -*- coding: utf-8 -*-
import os
import re
import urlparse
import dateutil.parser
from django.contrib.gis.geoip import GeoIP
from counter.models import Filename, LogEntry, Country


class LoglineError(Exception):
    pass


class LoglineParser(object):
    line_regexp = r'(?P<ip>.+?) (?P<ident>.+?) (?P<authuser>.+?) \[(?P<datetime>.+?)\] "(?P<method>.+?) (?P<path>.+?) (?P<protocol>.+?)" (?P<status>.+?) (?P<size>.+?) "(?P<referrer>.*?)" "(?P<agent>.*)"'
    filename_regexp = r'^.*\.(gz|dmg|msi|exe|xz)$'
    status_regexp = r'(2|3)[0-9]{2}'
    gi = GeoIP()

    def __init__(self, logstring):
        self.logstring = logstring
        self.ip = None
        self.ident = None
        self.authuser = None
        self.datetime = None
        self.method = None
        self.path = None
        self.protocol = None
        self.status = None
        self.size = None
        self.referrer = None
        self.agent = None
        self.filename = None

    def match(self):
        try:
            groups = re.match(self.line_regexp, self.logstring).groupdict()
        except AttributeError:
            raise LoglineError("Invalid logline: {}".format(self.logstring))
        self.ip = groups['ip']
        self.ident = groups['ident']
        self.authuser = groups['authuser']
        self.datetime = groups['datetime']
        self.method = groups['method']
        self.path = groups['path']
        self.filename = os.path.basename(urlparse.urlparse(self.path).path)
        self.protocol = groups['protocol']
        self.status = groups['status']
        self.size = groups['size']
        self.referrer = groups['referrer']
        self.agent = groups['agent']

    def get_date(self):
        return dateutil.parser.parse(self.datetime, fuzzy=True)

    def get_country(self):
        return self.gi.country_code(self.ip)

    def parse(self):
        if not re.match(self.status_regexp, self.status):
            return False
        if not self.filename:
            return False
        if not re.match(self.filename_regexp, self.filename):
            return False
        f, created = Filename.objects.get_or_create(name=self.filename)
        if created:
            f.save()
        if not f.id:
            return False
        country = self.get_country()
        c = None
        if country:
            c, created = Country.objects.get_or_create(name=country)
            if created:
                c.save()
        l, created = LogEntry.objects.get_or_create(date=self.get_date(), filename=f, country=c)
        l.count += 1
        l.save()
        return True

