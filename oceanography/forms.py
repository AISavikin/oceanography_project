from django import forms
from .models import Expedition, Station

class StationImportForm(forms.Form):
    expedition = forms.ModelChoiceField(
        queryset=None,
        widget=forms.HiddenInput(),
        required=True
    )
    station_data = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 15,
            'placeholder': 'Введите данные станций в формате:\nНазвание_станции Широта Долгота Глубина_дна Прозрачность_Секки\n\nПример:\nстанция_1 55.123456 37.654321 25.5 12.3\nстанция_2 55.223456 37.754321 30.0 15.7\n\nПримечание: Глубина дна и прозрачность - опциональные параметры',
            'class': 'form-control font-monospace small'
        }),
        label='Данные станций',
        help_text='Каждая строка - отдельная станция. Параметры разделяются пробелами. Рекомендуется использовать загрузку из файла для больших объемов данных.'
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