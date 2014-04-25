# -*- coding: utf-8 -*-
import gzip
import os
from tempfile import mkdtemp
import urllib
from django.conf import settings
from django.core.management.base import NoArgsCommand
from shutil import rmtree


class Command(NoArgsCommand):
    help = "Update the GeoIP-Database"
    url = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz"
    tmpdir = mkdtemp()

    def handle_noargs(self, **options):
        try:
            os.mkdir(settings.GEOIP_PATH)
        except OSError:
            pass
        self.stdout.write("Using temporary directory {}".format(self.tmpdir))
        self.stdout.write("Downloading {}".format(self.url))
        gzfilename = os.path.join(self.tmpdir, "GeoIP.dat.gz")
        urllib.urlretrieve(self.url, gzfilename)
        self.stdout.write("Extracting {}".format(gzfilename))
        gzfile = gzip.open(gzfilename, 'rb')
        dbfile = open(os.path.join(settings.GEOIP_PATH, 'GeoIP.dat'), 'wb')
        dbfile.writelines(gzfile)
        gzfile.close()
        dbfile.close()
        self.stdout.write("Deleting {}".format(self.tmpdir))
        rmtree(self.tmpdir)



