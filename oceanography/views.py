from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, View
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from .forms import StationForm, ExpeditionForm, StationFormSet
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

from django.views.generic import CreateView
from .forms import StationForm

class StationSingleCreateView(CreateView):
    """Вариант 1: Форма для добавления одной станции"""
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
    """Вариант 2: Форма с динамическим добавлением полей для нескольких станций"""
    template_name = 'oceanography/station_multiple_create.html'
    
    def get(self, request, *args, **kwargs):
        expedition_id = self.kwargs.get('expedition_id')
        expedition = get_object_or_404(Expedition, pk=expedition_id)
        
        # Создаем formset с одной дополнительной формой
        StationFormSet = formset_factory(StationForm, extra=1, can_delete=True)
        formset = StationFormSet(prefix='stations')
        
        context = self.get_context_data(formset=formset, expedition=expedition)
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        expedition_id = self.kwargs.get('expedition_id')
        expedition = get_object_or_404(Expedition, pk=expedition_id)
        
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