# -*- coding: utf-8 -*-
import fileinput
from django import db
from django.core.management.base import BaseCommand
from counter.parser import LoglineParser, LoglineError


class Command(BaseCommand):
    filename_regexp = r'^.*\.(gz|dmg|msi|exe|xz)$'
    args = '<file ...>'

    def handle(self, *args, **options):
        if not args:
            args = '-'
        counter = 0
        for line in fileinput.input(args):
            try:
                p = LoglineParser(line)
                p.match()
                p.parse()
            except LoglineError as e:
                self.stderr.write(e.message)
            if counter == 1000:
                db.reset_queries()
                counter = 0
            counter += 1

