from django.contrib import admin

# Register your models here.
from counter.models import Filename, Product, Country, OS, Arch, Version, Language, LogEntry, Query


class ProductAdmin(admin.ModelAdmin):
    pass


class CountryAdmin(admin.ModelAdmin):
    pass


class OSAdmin(admin.ModelAdmin):
    pass


class ArchAdmin(admin.ModelAdmin):
    pass


class VersionAdmin(admin.ModelAdmin):
    pass


class LanguageAdmin(admin.ModelAdmin):
    pass


class FilenameAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'os', 'arch', 'version', 'language')
    list_filter = ('product', 'os', 'arch', 'version', 'language')


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'filename', 'country', 'count')
    date_hierarchy = "date"
    readonly_fields = list_display


class QueryAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'count')


admin.site.register(Filename, FilenameAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(OS, OSAdmin)
admin.site.register(Arch, ArchAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(Query, QueryAdmin)
