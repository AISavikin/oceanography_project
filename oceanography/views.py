from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
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
        form.fields['expedition'].queryset = Expedition.objects.all()
        return form
    
    def parse_station_data(self, text_data, expedition):
        """
        Парсит текстовые данные станций и возвращает результат
        Обрабатывает как точки, так и запятые в десятичных числах
        """
        def parse_number(value_str):
            """Парсит число, заменяя запятые на точки"""
            if not value_str:
                return None
            normalized = value_str.replace(',', '.').strip()
            try:
                return float(normalized)
            except ValueError:
                return None

        lines = text_data.strip().split('\n')
        results = {
            'success': [],
            'errors': [],
            'total_lines': len(lines)
        }
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                parts = line.split()
                
                if len(parts) < 3:
                    station_preview = parts[0] if parts else "пустая строка"
                    results['errors'].append(
                        f"Ошибка в строке {line_num}: '{station_preview}' - недостаточно параметров (нужно минимум 3)"
                    )
                    continue
                    
                station_name = parts[0]
                
                latitude = parse_number(parts[1])
                longitude = parse_number(parts[2])
                
                if latitude is None or longitude is None:
                    results['errors'].append(
                        f"Ошибка в строке {line_num}: '{station_name}' - неверный формат координат"
                    )
                    continue
                
                if not (-90 <= latitude <= 90):
                    results['errors'].append(
                        f"Ошибка в строке {line_num}: '{station_name}' - широта должна быть между -90 и 90"
                    )
                    continue
                    
                if not (-180 <= longitude <= 180):
                    results['errors'].append(
                        f"Ошибка в строке {line_num}: '{station_name}' - долгота должна быть между -180 и 180"
                    )
                    continue
                
                bottom_depth = None
                secchi_depth = None
                
                if len(parts) >= 4:
                    bottom_depth = parse_number(parts[3])
                    if bottom_depth is None:
                        results['errors'].append(
                            f"Ошибка в строке {line_num}: '{station_name}' - неверный формат глубины дна"
                        )
                        continue
                        
                if len(parts) >= 5:
                    secchi_depth = parse_number(parts[4])
                    if secchi_depth is None:
                        results['errors'].append(
                            f"Ошибка в строке {line_num}: '{station_name}' - неверный формат прозрачности Секки"
                        )
                        continue
                
                if Station.objects.filter(expedition=expedition, station_name=station_name).exists():
                    results['errors'].append(
                        f"Ошибка в строке {line_num}: '{station_name}' - станция с таким названием уже существует в этой экспедиции"
                    )
                    continue
                
                station_data = {
                    'station_name': station_name,
                    'latitude': latitude,
                    'longitude': longitude,
                    'bottom_depth': bottom_depth,
                    'secchi_depth': secchi_depth,
                    'line_number': line_num
                }
                
                results['success'].append(station_data)
                
            except Exception as e:
                station_preview = parts[0] if 'parts' in locals() and parts else "неизвестная станция"
                results['errors'].append(
                    f"Ошибка в строке {line_num}: '{station_preview}' - непредвиденная ошибка: {str(e)}"
                )
        
        return results
    
    def form_valid(self, form):
        expedition = form.cleaned_data['expedition']
        station_data = form.cleaned_data['station_data']
        
        parse_results = self.parse_station_data(station_data, expedition)
        
        # Если есть ошибки - остаемся на странице и показываем их
        if parse_results['errors']:
            for error in parse_results['errors']:
                messages.error(self.request, error)
            
            # Добавляем форму в контекст с ошибками
            return self.render_to_response(self.get_context_data(form=form))
        
        # Если ошибок нет - показываем успешное сообщение
        else:
            messages.success(
                self.request, 
                f"Успешно обработано {len(parse_results['success'])} станций. "
                f"Данные готовы к сохранению (функция сохранения будет реализована в следующем шаге)."
            )
            
            # ВРЕМЕННО: не сохраняем в БД, только показываем успех
            # TODO: Реализовать сохранение на следующем этапе
            
            expedition_id = self.kwargs.get('expedition_id')
            return redirect('oceanography:expedition_detail', pk=expedition_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expedition_id = self.kwargs.get('expedition_id')
        
        # Всегда получаем экспедицию, даже при ошибках
        if expedition_id:
            try:
                context['expedition'] = Expedition.objects.get(pk=expedition_id)
            except Expedition.DoesNotExist:
                context['expedition'] = None
        
        context['breadcrumbs'] = [
            {'url': reverse('oceanography:home'), 'name': 'Главная'},
            {'url': reverse('oceanography:expedition_list'), 'name': 'Экспедиции'},
            {'url': reverse('oceanography:expedition_detail', kwargs={'pk': expedition_id}), 
             'name': f'Экспедиция {expedition_id}'},
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