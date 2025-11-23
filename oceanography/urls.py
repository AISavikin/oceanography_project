from django.urls import path
from . import views

app_name = 'oceanography'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('coming-soon/', ComingSoonView.as_view(), name='coming_soon'),
    # Expedition URLs
    path('expeditions/', views.ExpeditionListView.as_view(), name='expedition_list'),
    path('expeditions/<int:pk>/', views.ExpeditionDetailView.as_view(), name='expedition_detail'),
