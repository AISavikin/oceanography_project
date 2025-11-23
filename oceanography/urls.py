from django.urls import path
from .views import *

app_name = 'oceanography'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('coming-soon/', ComingSoonView.as_view(), name='coming_soon'),
]
    