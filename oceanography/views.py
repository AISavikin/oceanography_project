from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, View
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Avg, Min, Max, Q
from django.core.paginator import Paginator
from .forms import ExpeditionForm, StationForm
from .models import (
    Expedition, Station, Sample, MeteoData, CarbonData, 
    IonicCompositionData, PigmentsData, OxymetrData, 
    NutrientsData, PHMeasurement, Probe, CTDData
)


class ComingSoonView(TemplateView):
    template_name = 'oceanography/coming_soon.html'

class HomeView(TemplateView):
    template_name = 'oceanography/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Основная статистика
        context['expeditions_count'] = Expedition.objects.count()
        context['stations_count'] = Station.objects.count()
        context['samples_count'] = Sample.objects.count()
        context['ctd_data_count'] = CTDData.objects.count()
        
        # Последние экспедиции
        context['recent_expeditions'] = Expedition.objects.select_related().order_by('-start_date')[:5]
        
        # Последние станции с данными об экспедициях
        context['recent_stations'] = Station.objects.select_related('expedition').order_by('-datetime')[:10]
        
        # Последние пробы
        context['recent_samples'] = Sample.objects.select_related(
            'station', 'station__expedition'
        ).order_by('-datetime')[:10]
        
        # Статистика по типам данных
        context['data_stats'] = {
            'meteo': MeteoData.objects.count(),
            'carbon': CarbonData.objects.count(),
            'ionic': IonicCompositionData.objects.count(),
            'pigments': PigmentsData.objects.count(),
            'nutrients': NutrientsData.objects.count(),
            'ph': PHMeasurement.objects.count(),
        }
        
        # Последняя активность
        latest_station = Station.objects.order_by('-datetime').first()
        if latest_station:
            context['latest_activity'] = {
                'type': 'станция',
                'name': latest_station.station_name,
                'expedition': latest_station.expedition.platform,
                'date': latest_station.datetime
            }
        else:
            latest_expedition = Expedition.objects.order_by('-start_date').first()
            if latest_expedition:
                context['latest_activity'] = {
                    'type': 'экспедиция',
                    'name': latest_expedition.platform,
                    'date': latest_expedition.start_date
                }
        
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

class StationSingleCreateView(CreateView):
    """Форма для добавления одной станции"""
    model = Station
    form_class = StationForm
    template_name = 'oceanography/station_single_create.html'
    
    def form_valid(self, form):
        expedition_id = self.kwargs.get('expedition_id')
        form.instance.expedition_id = expedition_id
        
        # Проверка уникальности даты/времени станции в экспедиции
        if Station.objects.filter(
            expedition_id=expedition_id, 
            datetime=form.instance.datetime
        ).exists():
            form.add_error(
                'datetime', 
                f'Станция с датой/временем "{form.instance.datetime}" уже существует в этой экспедиции'
            )
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        messages.success(self.request, f'Станция "{form.instance.station_name}" успешно добавлена!')
        return response
    
    def get_success_url(self):
        expedition_id = self.kwargs.get('expedition_id')
        return reverse('oceanography:expedition_detail', kwargs={'pk': expedition_id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expedition_id = self.kwargs.get('expedition_id')
        
        try:
            context['expedition'] = Expedition.objects.get(pk=expedition_id)
        except Expedition.DoesNotExist:
            context['expedition'] = None
        
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:expedition_list'), 'name': 'Экспедиции'},
            {'url': reverse('oceanography:expedition_detail', kwargs={'pk': expedition_id}), 
             'name': f'Экспедиция {expedition_id}'},
            {'url': '', 'name': 'Добавление станции'}
        ]
        return context

class StationMultipleCreateView(View):
    """Форма с динамическим добавлением полей для нескольких станций"""
    template_name = 'oceanography/station_multiple_create.html'
    
    def get(self, request, *args, **kwargs):
        expedition_id = self.kwargs.get('expedition_id')
        expedition = get_object_or_404(Expedition, pk=expedition_id)
        
        # Создаем formset с одной дополнительной формой
        from django.forms import formset_factory
        StationFormSet = formset_factory(StationForm, extra=1, can_delete=True)
        formset = StationFormSet(prefix='stations')
        
        context = self.get_context_data(formset=formset, expedition=expedition)
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        expedition_id = self.kwargs.get('expedition_id')
        expedition = get_object_or_404(Expedition, pk=expedition_id)
        
        from django.forms import formset_factory
        StationFormSet = formset_factory(StationForm, extra=0, can_delete=True)
        formset = StationFormSet(request.POST, prefix='stations')
        
        if formset.is_valid():
            stations_created = 0
            errors = []
            
            for i, form in enumerate(formset):
                # Пропускаем удаленные формы
                if form.cleaned_data.get('DELETE', False):
                    continue
                    
                if form.is_valid() and form.has_changed():
                    station = form.save(commit=False)
                    station.expedition = expedition
                    
                    # Проверка уникальности даты/времени
                    if Station.objects.filter(expedition=expedition, datetime=station.datetime).exists():
                        errors.append(f"Станция {i+1}: станция с датой/временем '{station.datetime}' уже существует")
                        continue
                    
                    try:
                        station.save()
                        stations_created += 1
                    except Exception as e:
                        errors.append(f"Станция {i+1}: ошибка сохранения - {str(e)}")
            
            if errors:
                for error in errors:
                    messages.error(request, error)
                context = self.get_context_data(formset=formset, expedition=expedition)
                return render(request, self.template_name, context)
            
            if stations_created > 0:
                messages.success(request, f'Успешно добавлено {stations_created} станций!')
            else:
                messages.warning(request, 'Не было добавлено ни одной станции')
                
            return redirect('oceanography:expedition_detail', pk=expedition_id)
        
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
            context = self.get_context_data(formset=formset, expedition=expedition)
            return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        context = kwargs
        expedition_id = self.kwargs.get('expedition_id')
        expedition = get_object_or_404(Expedition, pk=expedition_id)
        
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:expedition_list'), 'name': 'Экспедиции'},
            {'url': reverse('oceanography:expedition_detail', kwargs={'pk': expedition_id}), 
             'name': f'Экспедиция {expedition_id}'},
            {'url': '', 'name': 'Добавление нескольких станций'}
        ]
        return context

# ============================================================================
# ПРЕДСТАВЛЕНИЯ ДЛЯ ПРОСМОТРА ВСЕХ ДАННЫХ
# ============================================================================

class DataOverviewView(TemplateView):
    """Обзор всех данных в системе"""
    template_name = 'oceanography/data_overview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Статистика по всем основным таблицам
        context['stats'] = {
            'expeditions': {
                'count': Expedition.objects.count(),
                'recent': Expedition.objects.order_by('-start_date')[:5],
                'total_stations': Station.objects.count(),
            },
            'stations': {
                'count': Station.objects.count(),
                'with_samples': Station.objects.filter(samples__isnull=False).distinct().count(),
                'recent': Station.objects.select_related('expedition').order_by('-datetime')[:10],
            },
            'samples': {
                'count': Sample.objects.count(),
                'recent': Sample.objects.select_related('station', 'station__expedition').order_by('-datetime')[:10],
            },
            'meteo_data': {
                'count': MeteoData.objects.count(),
                'recent': MeteoData.objects.select_related('sample', 'sample__station', 'sample__station__expedition')[:10],
            },
            'carbon_data': {
                'count': CarbonData.objects.count(),
                'recent': CarbonData.objects.select_related('sample', 'sample__station', 'sample__station__expedition')[:10],
            },
            'ionic_data': {
                'count': IonicCompositionData.objects.count(),
                'recent': IonicCompositionData.objects.select_related('sample', 'sample__station', 'sample__station__expedition')[:10],
            },
            'pigments_data': {
                'count': PigmentsData.objects.count(),
                'recent': PigmentsData.objects.select_related('sample', 'sample__station', 'sample__station__expedition')[:10],
            },
            'oxymetr_data': {
                'count': OxymetrData.objects.count(),
                'recent': OxymetrData.objects.select_related('sample', 'sample__station', 'sample__station__expedition')[:10],
            },
            'nutrients_data': {
                'count': NutrientsData.objects.count(),
                'recent': NutrientsData.objects.select_related('sample', 'sample__station', 'sample__station__expedition')[:10],
            },
            'ph_measurements': {
                'count': PHMeasurement.objects.count(),
                'recent': PHMeasurement.objects.select_related('sample', 'sample__station', 'sample__station__expedition')[:10],
            },
            'probes': {
                'count': Probe.objects.count(),
                'recent': Probe.objects.all()[:10],
            },
            'ctd_data': {
                'count': CTDData.objects.count(),
                'stations_with_ctd': CTDData.objects.values('sample__station').distinct().count(),
                'recent': CTDData.objects.select_related('sample', 'sample__station', 'sample__station__expedition', 'probe')[:10],
            },
        }
        
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': '', 'name': 'Обзор данных'}
        ]
        
        return context

class ExpeditionDataView(ListView):
    """Детальный просмотр всех экспедиций"""
    model = Expedition
    template_name = 'oceanography/data_expeditions.html'
    context_object_name = 'expeditions'
    paginate_by = 20
    
    def get_queryset(self):
        return Expedition.objects.annotate(
            stations_count=Count('stations'),
            samples_count=Count('stations__samples')
        ).order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:data_overview'), 'name': 'Обзор данных'},
            {'url': '', 'name': 'Все экспедиции'}
        ]
        return context

class StationDataView(ListView):
    """Детальный просмотр всех станций"""
    model = Station
    template_name = 'oceanography/data_stations.html'
    context_object_name = 'stations'
    paginate_by = 50
    
    def get_queryset(self):
        return Station.objects.select_related('expedition').annotate(
            samples_count=Count('samples')
        ).order_by('-datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:data_overview'), 'name': 'Обзор данных'},
            {'url': '', 'name': 'Все станции'}
        ]
        return context

class SampleDataView(ListView):
    """Детальный просмотр всех проб"""
    model = Sample
    template_name = 'oceanography/data_samples.html'
    context_object_name = 'samples'
    paginate_by = 50
    
    def get_queryset(self):
        return Sample.objects.select_related(
            'station', 'station__expedition'
        ).prefetch_related(
            'meteo_data', 'carbon_data', 'ionic_data', 
            'pigments_data', 'nutrients_data', 'ph_measurements'
        ).order_by('-datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:data_overview'), 'name': 'Обзор данных'},
            {'url': '', 'name': 'Все пробы'}
        ]
        return context

class MeteoDataView(ListView):
    """Детальный просмотр всех метеоданных"""
    model = MeteoData
    template_name = 'oceanography/data_meteo.html'
    context_object_name = 'meteo_data'
    paginate_by = 50
    
    def get_queryset(self):
        return MeteoData.objects.select_related(
            'sample', 'sample__station', 'sample__station__expedition'
        ).order_by('-sample__datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:data_overview'), 'name': 'Обзор данных'},
            {'url': '', 'name': 'Метеоданные'}
        ]
        return context

class CarbonDataView(ListView):
    """Детальный просмотр всех данных по углероду"""
    model = CarbonData
    template_name = 'oceanography/data_carbon.html'
    context_object_name = 'carbon_data'
    paginate_by = 50
    
    def get_queryset(self):
        return CarbonData.objects.select_related(
            'sample', 'sample__station', 'sample__station__expedition'
        ).order_by('-sample__datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:data_overview'), 'name': 'Обзор данных'},
            {'url': '', 'name': 'Данные по углероду'}
        ]
        return context

class IonicDataView(ListView):
    """Детальный просмотр всех данных по ионному составу"""
    model = IonicCompositionData
    template_name = 'oceanography/data_ionic.html'
    context_object_name = 'ionic_data'
    paginate_by = 50
    
    def get_queryset(self):
        return IonicCompositionData.objects.select_related(
            'sample', 'sample__station', 'sample__station__expedition'
        ).order_by('-sample__datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:data_overview'), 'name': 'Обзор данных'},
            {'url': '', 'name': 'Данные по ионному составу'}
        ]
        return context

class PigmentsDataView(ListView):
    """Детальный просмотр всех данных по пигментам"""
    model = PigmentsData
    template_name = 'oceanography/data_pigments.html'
    context_object_name = 'pigments_data'
    paginate_by = 50
    
    def get_queryset(self):
        return PigmentsData.objects.select_related(
            'sample', 'sample__station', 'sample__station__expedition'
        ).order_by('-sample__datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:data_overview'), 'name': 'Обзор данных'},
            {'url': '', 'name': 'Данные по пигментам'}
        ]
        return context

class OxymetrDataView(ListView):
    """Детальный просмотр всех данных оксиметра"""
    model = OxymetrData
    template_name = 'oceanography/data_oxymetr.html'
    context_object_name = 'oxymetr_data'
    paginate_by = 50
    
    def get_queryset(self):
        return OxymetrData.objects.select_related(
            'sample', 'sample__station', 'sample__station__expedition'
        ).order_by('-sample__datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:data_overview'), 'name': 'Обзор данных'},
            {'url': '', 'name': 'Данные оксиметра'}
        ]
        return context

class NutrientsDataView(ListView):
    """Детальный просмотр всех данных по биогенным элементам"""
    model = NutrientsData
    template_name = 'oceanography/data_nutrients.html'
    context_object_name = 'nutrients_data'
    paginate_by = 50
    
    def get_queryset(self):
        return NutrientsData.objects.select_related(
            'sample', 'sample__station', 'sample__station__expedition'
        ).order_by('-sample__datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:data_overview'), 'name': 'Обзор данных'},
            {'url': '', 'name': 'Данные по биогенным элементам'}
        ]
        return context

class PHDataView(ListView):
    """Детальный просмотр всех измерений pH"""
    model = PHMeasurement
    template_name = 'oceanography/data_ph.html'
    context_object_name = 'ph_measurements'
    paginate_by = 50
    
    def get_queryset(self):
        return PHMeasurement.objects.select_related(
            'sample', 'sample__station', 'sample__station__expedition'
        ).order_by('-sample__datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:data_overview'), 'name': 'Обзор данных'},
            {'url': '', 'name': 'Измерения pH'}
        ]
        return context

class ProbeDataView(ListView):
    """Детальный просмотр всех зондов"""
    model = Probe
    template_name = 'oceanography/data_probes.html'
    context_object_name = 'probes'
    paginate_by = 50
    
    def get_queryset(self):
        return Probe.objects.annotate(
            ctd_measurements_count=Count('ctd_measurements')
        ).order_by('probe_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:data_overview'), 'name': 'Обзор данных'},
            {'url': '', 'name': 'Зонды'}
        ]
        return context

class CTDDataView(ListView):
    """Детальный просмотр всех CTD данных"""
    model = CTDData
    template_name = 'oceanography/data_ctd.html'
    context_object_name = 'ctd_data'
    paginate_by = 50
    
    def get_queryset(self):
        return CTDData.objects.select_related(
            'sample', 'sample__station', 'sample__station__expedition', 'probe'
        ).order_by('-sample__datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:data_overview'), 'name': 'Обзор данных'},
            {'url': '', 'name': 'CTD данные'}
        ]
        return context