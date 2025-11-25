from django.urls import path
from .views import *

app_name = 'oceanography'

urlpatterns = [
    # Основные URLs
    path('', HomeView.as_view(), name='home'),
    path('coming-soon/', ComingSoonView.as_view(), name='coming_soon'),
    path('expeditions/', ExpeditionListView.as_view(), name='expedition_list'),
    path('expeditions/<int:pk>/', ExpeditionDetailView.as_view(), name='expedition_detail'),
    path('expeditions/<int:expedition_id>/add-station/single/', StationSingleCreateView.as_view(), name='add_station_single'),
    path('expeditions/<int:expedition_id>/add-stations/excel/', StationExcelUploadView.as_view(), name='add_stations_excel'),
    path('expeditions/create/', ExpeditionCreateView.as_view(), name='expedition_create'),
    
    # Просмотр всех данных
    path('data/', DataOverviewView.as_view(), name='data_overview'),
    path('data/expeditions/', ExpeditionDataView.as_view(), name='data_expeditions'),
    path('data/stations/', StationDataView.as_view(), name='data_stations'),
    path('data/samples/', SampleDataView.as_view(), name='data_samples'),
    path('data/meteo/', MeteoDataView.as_view(), name='data_meteo'),
    path('data/carbon/', CarbonDataView.as_view(), name='data_carbon'),
    path('data/ionic/', IonicDataView.as_view(), name='data_ionic'),
    path('data/pigments/', PigmentsDataView.as_view(), name='data_pigments'),
    path('data/oxymetr/', OxymetrDataView.as_view(), name='data_oxymetr'),
    path('data/nutrients/', NutrientsDataView.as_view(), name='data_nutrients'),
    path('data/ph/', PHDataView.as_view(), name='data_ph'),
    path('data/probes/', ProbeDataView.as_view(), name='data_probes'),
    path('data/ctd/', CTDDataView.as_view(), name='data_ctd'),

     # CTD профили
    path('ctd-profiles/', CTDProfileListView.as_view(), name='ctd_profile_list'),
    path('ctd-profiles/create/', CTDProfileCreateView.as_view(), name='ctd_profile_create'),
    path('ctd-profiles/<int:pk>/', CTDProfileDetailView.as_view(), name='ctd_profile_detail'),
    path('stations/<int:station_id>/add-ctd-profile/', CTDProfileCreateView.as_view(), name='add_ctd_profile'),
    path('expeditions/<int:expedition_id>/add-meteo/excel/', MeteoExcelUploadView.as_view(), name='add_meteo_excel'),
    path('logs/', LogViewerView.as_view(), name='log_viewer'),
]