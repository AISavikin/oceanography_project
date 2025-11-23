from django.contrib import admin
from .models import Expedition

@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('platform', 'start_date', 'end_date', 'area', 'stations_count')
    list_filter = ('platform', 'start_date', 'area')
    search_fields = ('platform', 'area')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('platform', 'area')
        }),
        ('Временные параметры', {
            'fields': ('start_date', 'end_date')
        }),
    )
    
    def stations_count(self, obj):
        return obj.stations.count()
    stations_count.short_description = 'Кол-во станций'
# Register your models here.
