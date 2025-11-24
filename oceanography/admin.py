from django.contrib import admin
from .models import (
    Expedition, Station, Sample, MeteoData, CarbonData, 
    IonicCompositionData, PigmentsData, OxymetrData, 
    NutrientsData, PHMeasurement, Probe, CTDData, 
    CTDProfile, CTDMeasurement
)

class StationInline(admin.TabularInline):
    model = Station
    extra = 0
    fields = ('station_name', 'datetime', 'latitude', 'longitude')
    readonly_fields = ('station_name', 'datetime', 'latitude', 'longitude')
    show_change_link = True

class SampleInline(admin.TabularInline):
    model = Sample
    extra = 0
    fields = ('datetime', 'sampling_depth')
    readonly_fields = ('datetime', 'sampling_depth')
    show_change_link = True

@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('platform', 'start_date', 'end_date', 'area', 'stations_count')
    list_filter = ('platform', 'start_date', 'area')
    search_fields = ('platform', 'area')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)
    inlines = [StationInline]
    
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

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('station_name', 'expedition', 'datetime', 'latitude', 'longitude', 'samples_count')
    list_filter = ('expedition', 'datetime')
    search_fields = ('station_name', 'expedition__platform')
    date_hierarchy = 'datetime'
    raw_id_fields = ('expedition',)
    inlines = [SampleInline]
    
    def samples_count(self, obj):
        return obj.samples.count()
    samples_count.short_description = 'Кол-во проб'

class MeteoDataInline(admin.TabularInline):
    model = MeteoData
    extra = 0
    fields = ('t_air_c', 'humidity_percent', 'wind_speed_m_s', 'wind_direction', 'pressure_hpa')

class CarbonDataInline(admin.TabularInline):
    model = CarbonData
    extra = 0
    fields = ('dtc_mg_c_l', 'dic_mg_c_l', 'doc_mg_c_l', 'tss_mg_l', 'poc_mg_c_m3')

class IonicCompositionDataInline(admin.TabularInline):
    model = IonicCompositionData
    extra = 0
    fields = ('cl_mg_l', 'hco3_mg_l', 'so4_mg_l', 'mineralization_mg_l')

class PigmentsDataInline(admin.TabularInline):
    model = PigmentsData
    extra = 0
    fields = ('chl_a_mg_m3', 'chl_a_pheo_mg_m3', 'total_chl_mg_m3')

class OxymetrDataInline(admin.TabularInline):
    model = OxymetrData
    extra = 0
    fields = ('do_mg_l_oxy', 'do_sat_percent_oxy', 'turbidity_ntu_oxy')

class NutrientsDataInline(admin.TabularInline):
    model = NutrientsData
    extra = 0
    fields = ('no3_mg_n_l', 'nh4_mg_n_l', 'po4_mg_p_l', 'si_mg_si_l')

class PHMeasurementInline(admin.TabularInline):
    model = PHMeasurement
    extra = 0
    fields = ('ph_meter', 'ph_value')

class CTDDataInline(admin.TabularInline):
    model = CTDData
    extra = 0
    fields = ('probe', 'temp_c', 'salinity_psu', 'do_mg_l')

@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('sample_id', 'station', 'datetime', 'sampling_depth')
    list_filter = ('station__expedition', 'datetime')
    search_fields = ('station__station_name', 'sampling_depth')
    date_hierarchy = 'datetime'
    raw_id_fields = ('station',)
    inlines = [
        MeteoDataInline,
        CarbonDataInline,
        IonicCompositionDataInline,
        PigmentsDataInline,
        OxymetrDataInline,
        NutrientsDataInline,
        PHMeasurementInline,
        CTDDataInline,
    ]

class CTDMeasurementInline(admin.TabularInline):
    model = CTDMeasurement
    extra = 0
    fields = ('depth_m', 'temp_c', 'salinity_psu', 'do_mg_l')
    readonly_fields = fields

@admin.register(CTDProfile)
class CTDProfileAdmin(admin.ModelAdmin):
    list_display = ('profile_id', 'station', 'probe', 'start_datetime', 'max_depth')
    list_filter = ('station__expedition', 'probe', 'start_datetime')
    search_fields = ('station__station_name', 'probe__probe_name')
    date_hierarchy = 'start_datetime'
    raw_id_fields = ('station', 'probe')
    inlines = [CTDMeasurementInline]

# Базовые модели данных с простой регистрацией
@admin.register(MeteoData)
class MeteoDataAdmin(admin.ModelAdmin):
    list_display = ('meteo_data_id', 'sample', 't_air_c', 'wind_speed_m_s')
    list_filter = ('sample__station__expedition',)
    raw_id_fields = ('sample',)

@admin.register(CarbonData)
class CarbonDataAdmin(admin.ModelAdmin):
    list_display = ('carbon_data_id', 'sample', 'dtc_mg_c_l', 'doc_mg_c_l')
    list_filter = ('sample__station__expedition',)
    raw_id_fields = ('sample',)

@admin.register(IonicCompositionData)
class IonicCompositionDataAdmin(admin.ModelAdmin):
    list_display = ('ionic_data_id', 'sample', 'cl_mg_l', 'ca_mg_l')
    list_filter = ('sample__station__expedition',)
    raw_id_fields = ('sample',)

@admin.register(PigmentsData)
class PigmentsDataAdmin(admin.ModelAdmin):
    list_display = ('pigments_data_id', 'sample', 'chl_a_mg_m3', 'total_chl_mg_m3')
    list_filter = ('sample__station__expedition',)
    raw_id_fields = ('sample',)

@admin.register(OxymetrData)
class OxymetrDataAdmin(admin.ModelAdmin):
    list_display = ('oxymetr_data_id', 'sample', 'do_mg_l_oxy', 'do_sat_percent_oxy')
    list_filter = ('sample__station__expedition',)
    raw_id_fields = ('sample',)

@admin.register(NutrientsData)
class NutrientsDataAdmin(admin.ModelAdmin):
    list_display = ('nutrients_data_id', 'sample', 'no3_mg_n_l', 'nh4_mg_n_l', 'po4_mg_p_l')
    list_filter = ('sample__station__expedition',)
    raw_id_fields = ('sample',)

@admin.register(PHMeasurement)
class PHMeasurementAdmin(admin.ModelAdmin):
    list_display = ('id', 'sample', 'ph_meter', 'ph_value')
    list_filter = ('sample__station__expedition', 'ph_meter')
    raw_id_fields = ('sample',)

@admin.register(Probe)
class ProbeAdmin(admin.ModelAdmin):
    list_display = ('probe_id', 'probe_name', 'description')
    search_fields = ('probe_name',)

@admin.register(CTDData)
class CTDDataAdmin(admin.ModelAdmin):
    list_display = ('ctd_data_id', 'sample', 'probe', 'temp_c', 'salinity_psu')
    list_filter = ('sample__station__expedition', 'probe')
    raw_id_fields = ('sample', 'probe')

@admin.register(CTDMeasurement)
class CTDMeasurementAdmin(admin.ModelAdmin):
    list_display = ('measurement_id', 'profile', 'depth_m', 'temp_c', 'salinity_psu')
    list_filter = ('profile__station__expedition',)
    raw_id_fields = ('profile',)