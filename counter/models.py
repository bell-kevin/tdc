from django.core.exceptions import ObjectDoesNotExist
from django.db import models

# Create your models here.
import re
from django.db.models import Sum


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"


class OS(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Operating System"
        verbose_name_plural = "Operating Systems"


class Arch(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Arch"
        verbose_name_plural = "Archs"


class Version(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Version"
        verbose_name_plural = "Versions"


class Language(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"


class Filename(models.Model):
    name = models.CharField(max_length=255, unique=True)
    product = models.ForeignKey(Product)
    os = models.ForeignKey(OS)
    arch = models.ForeignKey(Arch)
    version = models.ForeignKey(Version)
    language = models.ForeignKey(Language, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Filename"
        verbose_name_plural = "Filenames"

    def parse_name(self):
        regexp = r'(?P<product>.+?)_(?P<version>.+?)_(?P<os>.+?)_(?P<arch>.+?)(_(deb|rpm))?(_(?P<tail>[^\.]+))?\.(?P<extension>.+)'
        tail_regexp = r'(?P<subproduct>[^_]+)(_(?P<language>.+))?'
        try:
            matches = re.match(regexp, self.name).groupdict()
        except AttributeError:
            return None
        if matches['extension'] == 'asc':
            return None
        if matches['tail']:
            try:
                matches.update(re.match(tail_regexp, matches['tail']).groupdict())
            except AttributeError:
                return None
        if 'subproduct' in matches:
            matches['product'] += " {}".format(matches['subproduct'])
        return matches

    def save(self, *args, **kwargs):
        try:
            if self.product and self.os and self.arch and self.version:
                return super(Filename, self).save(*args, **kwargs)
        except ObjectDoesNotExist:
            pass
        matches = self.parse_name()
        if not matches:
            return
        product, created = Product.objects.get_or_create(name=matches['product'])
        version, created = Version.objects.get_or_create(name=matches['version'])
        os, created = OS.objects.get_or_create(name=matches['os'])
        arch, created = Arch.objects.get_or_create(name=matches['arch'])
        if 'language' in matches and matches['language']:
            language, created = Language.objects.get_or_create(name=matches['language'])
            self.language = language
        self.product = product
        self.version = version
        self.os = os
        self.arch = arch
        return super(Filename, self).save(*args, **kwargs)


class LogEntry(models.Model):
    date = models.DateField()
    country = models.ForeignKey(Country, null=True, blank=True)
    filename = models.ForeignKey(Filename)
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('date', 'country', 'filename')
        verbose_name = "Log Entry"
        verbose_name_plural = "Log Entries"


class Query(models.Model):
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    name = models.CharField(max_length=255)
    countries = models.ManyToManyField(Country, null=True, blank=True)
    languages = models.ManyToManyField(Language, null=True, blank=True)
    os = models.ManyToManyField(OS, null=True, blank=True)
    products = models.ManyToManyField(Product, null=True, blank=True)
    versions = models.ManyToManyField(Version, null=True, blank=True)
    archs = models.ManyToManyField(Arch, null=True, blank=True)

    class Meta:
        verbose_name = "Query"
        verbose_name_plural = "Queries"

    @property
    def count(self):
        le = LogEntry.objects.all()
        if self.start_date:
            le = le.filter(date__gte=self.start_date)
        if self.end_date:
            le = le.filter(date__lte=self.end_date)
        if self.countries.all().count():
            le = le.filter(country__in=self.countries.all())
        if self.languages.all().count():
            le = le.filter(filename__language__in=self.languages.all())
        if self.os.all().count():
            le = le.filter(filename__os__in=self.os.all())
        if self.products.all().count():
            le = le.filter(filename__product__in=self.products.all())
        if self.versions.all().count():
            le = le.filter(filename__version__in=self.versions.all())
        if self.archs.all().count():
            le = le.filter(filename__arch__in=self.archs.all())
        return le.aggregate(total=Sum('count'))['total']

