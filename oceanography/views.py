from django.views.generic import TemplateView, ListView
from .models import (
    Expedition, Station, Sample, MeteoData, CarbonData, 
    IonicCompositionData, PigmentsData, OxymetrData, 
    NutrientsData, PHMeasurement, Probe, CTDData
)

class ComingSoonView(TemplateView):
    template_name = 'coming_soon.html'

class HomeView(ListView):
    model = Expedition
    template_name = 'oceanography/home.html'
    context_object_name = 'expeditions'
    
    def get_queryset(self):
        return Expedition.objects.all()[:5]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_samples'] = Sample.objects.select_related(
            'station', 'station__expedition'
        ).all()[:10]
        
        # Статистика для главной страницы
        context['expeditions_count'] = Expedition.objects.count()
        context['stations_count'] = Station.objects.count()
        context['samples_count'] = Sample.objects.count()
        context['ctd_data_count'] = CTDData.objects.count()
        
        return context
