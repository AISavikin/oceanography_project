from django.urls import path
from .views import *

app_name = 'oceanography'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('coming-soon/', ComingSoonView.as_view(), name='coming_soon'),
    path('expeditions/', ExpeditionListView.as_view(), name='expedition_list'),
    path('expeditions/<int:pk>/', ExpeditionDetailView.as_view(), name='expedition_detail'),
    path('expeditions/<int:expedition_id>/add-station/single/', StationSingleCreateView.as_view(), name='add_station_single'),
    path('expeditions/<int:expedition_id>/add-station/multiple/', StationMultipleCreateView.as_view(), name='add_station_multiple'),
    path('expeditions/create/', ExpeditionCreateView.as_view(), name='expedition_create'),
]
    