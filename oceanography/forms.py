from django import forms
from .models import Expedition, Station, CTDProfile
from django.forms import inlineformset_factory
from django.forms import modelformset_factory

class StationForm(forms.ModelForm):
    class Meta:
        model = Station
        fields = ['station_name', 'datetime', 'latitude', 'longitude', 'bottom_depth', 'secchi_depth']
        widgets = {
            'station_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название станции'}),
            'datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'placeholder': '55.123456'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'placeholder': '37.654321'}),
            'bottom_depth': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '25.5'}),
            'secchi_depth': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '12.3'}),
        }
        labels = {
            'station_name': 'Название станции',
            'datetime': 'Дата и время станции',
            'latitude': 'Широта',
            'longitude': 'Долгота',
            'bottom_depth': 'Глубина дна (м)',
            'secchi_depth': 'Прозрачность по Секки (м)',
        }

# Formset для множественного добавления станций
StationFormSet = modelformset_factory(
    Station, 
    form=StationForm,
    extra=1,  # Начинаем с одной пустой формы
    can_delete=True
)


class ExpeditionForm(forms.ModelForm):
    class Meta:
        model = Expedition
        fields = ['platform', 'start_date', 'end_date', 'area']
        widgets = {
            'platform': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название судна или платформы'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),            
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Район работ'}),
        }
        labels = {
            'platform': 'Название судна/платформы',
            'start_date': 'Дата и время начала',
            'end_date': 'Дата и время окончания',
            'area': 'Район работ',
        }


class CTDProfileForm(forms.ModelForm):
    class Meta:
        model = CTDProfile
        fields = ['station', 'probe', 'start_datetime', 'end_datetime', 'max_depth', 'data_file', 'comment']
        widgets = {
            'station': forms.Select(attrs={'class': 'form-control'}),
            'probe': forms.Select(attrs={'class': 'form-control'}),
            'start_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'max_depth': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'data_file': forms.FileInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'station': 'Станция',
            'probe': 'Зонд',
            'start_datetime': 'Время начала профилирования',
            'end_datetime': 'Время окончания профилирования',
            'max_depth': 'Максимальная глубина (м)',
            'data_file': 'Файл с данными',
            'comment': 'Комментарии',
        }

# Добавить в forms.py
class MeteoDataUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel файл с метеоданными',
        help_text='Загрузите заполненный шаблон Excel с метеоданными',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'})
    )