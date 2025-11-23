from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .forms import StationImportForm, ExpeditionForm
from .models import (
    Expedition, Station, Sample, MeteoData, CarbonData, 
    IonicCompositionData, PigmentsData, OxymetrData, 
    NutrientsData, PHMeasurement, Probe, CTDData
)


class ComingSoonView(TemplateView):
    template_name = 'oceanography/coming_soon.html'

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

class ExpeditionListView(ListView):
    model = Expedition
    template_name = 'oceanography/expedition_list.html'
    context_object_name = 'expeditions'
    paginate_by = 20
    
    def get_queryset(self):
        return Expedition.objects.all().prefetch_related('stations')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': '', 'name': 'Экспедиции'}
        ]
        return context

class ExpeditionCreateView(CreateView):
    model = Expedition
    form_class = ExpeditionForm
    template_name = 'oceanography/expedition_form.html'
    success_url = reverse_lazy('oceanography:expedition_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Экспедиция "{self.object.platform}" успешно создана!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:expedition_list'), 'name': 'Экспедиции'},
            {'url': '', 'name': 'Создание экспедиции'}
        ]
        return context

class ExpeditionDetailView(DetailView):
    model = Expedition
    template_name = 'oceanography/expedition_detail.html'
    context_object_name = 'expedition'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expedition = self.get_object()
        
        context['stations'] = expedition.stations.all().prefetch_related('samples')
        context['samples_count'] = Sample.objects.filter(station__expedition=expedition).count()
        
        # Расчет длительности в днях
        if expedition.start_date and expedition.end_date:
            delta = expedition.end_date - expedition.start_date
            context['duration_days'] = delta.days
        else:
            context['duration_days'] = None
        
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:expedition_list'), 'name': 'Экспедиции'},
            {'url': '', 'name': f'{expedition.platform} ({expedition.start_date.year})'}
        ]
        return context

class StationImportView(FormView):
    form_class = StationImportForm
    template_name = 'oceanography/station_import.html'
    
    def get_initial(self):
        initial = super().get_initial()
        expedition_id = self.kwargs.get('expedition_id')
        if expedition_id:
            initial['expedition'] = Expedition.objects.get(pk=expedition_id)
        return initial
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Устанавливаем queryset для поля expedition
        form.fields['expedition'].queryset = Expedition.objects.all()
        return form
    
    def form_valid(self, form):
        # TODO: Реализовать парсинг и сохранение станций
        messages.info(self.request, 'Функциональность парсинга станций будет реализована в следующем шаге')
        expedition_id = self.kwargs.get('expedition_id')
        return redirect('oceanography:expedition_detail', pk=expedition_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expedition_id = self.kwargs.get('expedition_id')
        if expedition_id:
            context['expedition'] = Expedition.objects.get(pk=expedition_id)
        
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:expedition_list'), 'name': 'Экспедиции'},
            {'url': reverse('oceanography:expedition_detail', kwargs={'pk': expedition_id}), 'name': f'Экспедиция {expedition_id}'},
            {'url': '', 'name': 'Добавление станций'}
        ]
        return context


class StationFileImportView(TemplateView):
    template_name = 'oceanography/station_file_import.html'
    
    def get(self, request, *args, **kwargs):
        messages.info(request, 'Функциональность загрузки из файла будет реализована в следующем шаге')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expedition_id = self.kwargs.get('expedition_id')
        if expedition_id:
            context['expedition'] = Expedition.objects.get(pk=expedition_id)
        
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:expedition_list'), 'name': 'Экспедиции'},
            {'url': reverse('oceanography:expedition_detail', kwargs={'pk': expedition_id}), 'name': f'Экспедиция {expedition_id}'},
            {'url': '', 'name': 'Загрузка станций из файла'}
        ]
        return context