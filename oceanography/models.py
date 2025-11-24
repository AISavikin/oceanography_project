from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Expedition(models.Model):
    """Экспедиции"""
    expedition_id = models.AutoField(primary_key=True)
    start_date = models.DateField(verbose_name="Дата начала экспедиции")
    end_date = models.DateField(verbose_name="Дата окончания экспедиции")
    platform = models.CharField(max_length=200, verbose_name="Название судна/платформы")
    area = models.CharField(max_length=300, verbose_name="Район работ")
        
    class Meta:
        db_table = 'expeditions'
        verbose_name = "Экспедиция"
        verbose_name_plural = "Экспедиции"
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['platform']),
            models.Index(fields=['area']),
        ]
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.platform} ({self.start_date})"

class Station(models.Model):
    """Станции наблюдений"""
    station_id = models.AutoField(primary_key=True)
    expedition = models.ForeignKey(Expedition, on_delete=models.CASCADE, verbose_name="Экспедиция", related_name='stations')
    station_name = models.CharField(max_length=200, verbose_name="Название станции")
    datetime = models.DateTimeField(verbose_name="Дата и время станции")  # НОВОЕ ПОЛЕ
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Долгота")
    bottom_depth = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Глубина дна (м)")
    secchi_depth = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Прозрачность по диску Секки (м)")
    
    class Meta:
        db_table = 'stations'
        verbose_name = "Станция"
        verbose_name_plural = "Станции"
        indexes = [
            models.Index(fields=['expedition', 'datetime']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['datetime']),
        ]
        unique_together = ['expedition', 'datetime']  
        ordering = ['expedition', 'datetime']
    
    def __str__(self):
        return f"{self.station_name} ({self.datetime.date()})"

class Sample(models.Model):
    """Пробы - основная связующая сущность"""
    sample_id = models.AutoField(primary_key=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, verbose_name="Станция", related_name='samples')
    datetime = models.DateTimeField(verbose_name="Дата и время отбора пробы")
    sampling_depth = models.CharField(max_length=50, verbose_name="Горизонт отбора")
    comment = models.TextField(blank=True, verbose_name="Комментарии")
    
    class Meta:
        db_table = 'samples'
        verbose_name = "Проба"
        verbose_name_plural = "Пробы"
        indexes = [
            models.Index(fields=['station', 'datetime']),
            models.Index(fields=['datetime']),
            models.Index(fields=['sampling_depth']),
        ]
        ordering = ['station__expedition', 'station', 'datetime']
    
    def __str__(self):
        return f"Проба {self.sample_id} - {self.station.station_name} ({self.datetime})"
    
    @property
    def expedition(self):
        """Получить экспедицию через станцию"""
        return self.station.expedition

class MeteoData(models.Model):
    """Метеоданные"""
    meteo_data_id = models.AutoField(primary_key=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, verbose_name="Проба", related_name='meteo_data')
    
    t_air_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Температура воздуха (°C)")
    humidity_percent = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="Влажность (%)")
    wind_speed_m_s = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Скорость ветра (м/с)")
    wind_direction = models.IntegerField(null=True, blank=True, verbose_name="Направление ветра")
    pressure_hpa = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name="Атмосферное давление (гПа)")
    
    class Meta:
        db_table = 'meteo_data'
        verbose_name = "Метеоданные"
        verbose_name_plural = "Метеоданные"
    
    def __str__(self):
        return f"Метео {self.sample.sample_id}"

class CarbonData(models.Model):
    """Данные по углероду"""
    carbon_data_id = models.AutoField(primary_key=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, verbose_name="Проба", related_name='carbon_data')
    
    dtc_mg_c_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Растворенный углерод (мгC/л)")
    dic_mg_c_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Неорганический углерод (мгC/л)")
    doc_mg_c_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Органический углерод (мгC/л)")
    tss_mg_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Взвесь общая (мг/л)")
    poc_mg_c_m3 = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Взвешенный углерод (мгС/м³)")
    
    class Meta:
        db_table = 'carbon_data'
        verbose_name = "Данные по углероду"
        verbose_name_plural = "Данные по углероду"
    
    def __str__(self):
        return f"Углерод {self.sample.sample_id}"


class IonicCompositionData(models.Model):
    """Данные по ионному составу"""
    ionic_data_id = models.AutoField(primary_key=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, verbose_name="Проба", related_name='ionic_data')
    
    # Хлориды
    cl_meq_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Хлориды (мг-экв/л)")
    cl_mg_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Хлориды (мг/л)")
    
    # Гидрокарбонаты
    hco3_meq_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Гидрокарбонаты (мг-экв/л)")
    hco3_mg_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Гидрокарбонаты (мг/л)")
    
    # Сульфаты
    so4_meq_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Сульфаты (мг-экв/л)")
    so4_mg_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Сульфаты (мг/л)")
    
    # Жесткость и катионы
    hardness_meq_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Жесткость (мг-экв/л)")
    ca_meq_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Кальций (мг-экв/л)")
    ca_mg_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Кальций (мг/л)")
    mg_meq_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Магний (мг-экв/л)")
    mg_mg_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Магний (мг/л)")
    
    # Натрий и калий
    na_k_meq_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Натрий+Калий (мг-экв/л)")
    na_k_mg_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Натрий+Калий (мг/л)")
    
    # Общая минерализация
    mineralization_mg_l = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Общая минерализация (мг/л)")
    
    class Meta:
        db_table = 'ionic_composition_data'
        verbose_name = "Данные по ионному составу"
        verbose_name_plural = "Данные по ионному составу"
    
    def __str__(self):
        return f"Ионы {self.sample.sample_id}"

class PigmentsData(models.Model):
    """Данные по пигментам"""
    pigments_data_id = models.AutoField(primary_key=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, verbose_name="Проба", related_name='pigments_data')
    
    chl_a_mg_m3 = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Хлорофилл-а (мг/м³)")
    chl_a_pheo_mg_m3 = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Хлорофилл-а+феофитин (мг/м³)")
    chl_a_tri_mg_m3 = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Хлорофилл-а (трихроматический) (мг/м³)")
    total_chl_mg_m3 = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Суммарный хлорофилл (мг/м³)")
    
    class Meta:
        db_table = 'pigments_data'
        verbose_name = "Данные по пигментам"
        verbose_name_plural = "Данные по пигментам"
    
    def __str__(self):
        return f"Пигменты {self.sample.sample_id}"

class OxymetrData(models.Model):
    """Данные оксиметра"""
    oxymetr_data_id = models.AutoField(primary_key=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, verbose_name="Проба", related_name='oxymetr_data')
    do_mg_l_oxy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Кислород (мг/л), по оксиметру")
    do_sat_percent_oxy = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="Насыщение кислородом (%), по оксиметру")
    turbidity_ntu_oxy = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Мутность (NTU), по оксиметру")

    class Meta:
        db_table = 'oxymetr_data'
        verbose_name = "Данные оксиметра"
        verbose_name_plural = "Данные оксиметра"

    def __str__(self):
        return f'Оксиметр {self.sample.sample_id}'



class NutrientsData(models.Model):
    """Данные по биогенным элементам"""
    nutrients_data_id = models.AutoField(primary_key=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, verbose_name="Проба", related_name='nutrients_data')
    
    # Азотные соединения
    no2_mg_n_l = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True, verbose_name="Нитриты (мгN/л)")
    no3_mg_n_l = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True, verbose_name="Нитраты (мгN/л)")
    nh4_mg_n_l = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True, verbose_name="Аммоний (мгN/л)")
    
    # Фосфор
    po4_mg_p_l = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True, verbose_name="Фосфаты (мгP/л)")
    
    # Кремний
    si_mg_si_l = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True, verbose_name="Кремний (мгSi/л)")
    
    # Общие параметры
    dtotn_mg_n_l = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True, verbose_name="Растворенный азот (мгN/л)")
    totn_mg_n_l = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True, verbose_name="Валовой азот (мгN/л)")
    dtotp_mg_p_l = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True, verbose_name="Растворенный фосфор (мгP/л)")
    totp_mg_p_l = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True, verbose_name="Валовой фосфор (мгP/л)")
    
    class Meta:
        db_table = 'nutrients_data'
        verbose_name = "Данные по биогенам"
        verbose_name_plural = "Данные по биогенам"
    
    def __str__(self):
        return f"Биогены {self.sample.sample_id}"


class PHMeasurement(models.Model):
    """Измерения pH"""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, verbose_name="Проба", related_name='ph_measurements')
    ph_meter = models.CharField(max_length=100, verbose_name="Название/модель прибора")
    ph_value = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Значение pH")
    
    class Meta:
        db_table = 'ph_measurements'
        verbose_name = "Измерение pH"
        verbose_name_plural = "Измерения pH"
    
    def __str__(self):
        return f"pH {self.ph_value} - {self.sample}"


class Probe(models.Model):
    """Зонды для измерений"""
    probe_id = models.AutoField(primary_key=True)
    probe_name = models.CharField(max_length=100, verbose_name="Название/модель зонда")
    description = models.TextField(blank=True, verbose_name="Описание характеристик")
    
    class Meta:
        db_table = 'probes'
        verbose_name = "Зонд"
        verbose_name_plural = "Зонды"
    
    def __str__(self):
        return self.probe_name

class CTDData(models.Model):
    """Данные CTD-зонда"""
    ctd_data_id = models.AutoField(primary_key=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, verbose_name="Проба", related_name='ctd_data')
    probe = models.ForeignKey(Probe, on_delete=models.CASCADE, verbose_name="Зонд", related_name='ctd_measurements')
    
    # Основные параметры
    pressure_dbar = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Давление (dBar)")
    temp_c = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Температура (°C)")
    cond_ms_cm = models.DecimalField(max_digits=7, decimal_places=4, verbose_name="Электропроводность (мС/см)")
    salinity_psu = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="Соленость (PSU)")
    
    # Кислород
    do_ml_l = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Кислород (мл/л), по CTD")
    do_mg_l = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Кислород (мг/л), по CTD")
    do_sat_percent = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="Насыщение кислородом (%), по CTD")
    
    # Дополнительные параметры
    chl_a_ug_l = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Хлорофилл-а (µg/L)")
    turbidity_ntu = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Мутность (NTU), по CTD")
    cdom_ppb = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="CDOM (ppb)")
    sigma_kg_m3 = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, verbose_name="Плотность (kg/m³)")
    measured_depth_m = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Измеренная глубина (м)")
    
    class Meta:
        db_table = 'ctd_data'
        verbose_name = "Данные CTD"
        verbose_name_plural = "Данные CTD"
        indexes = [
            models.Index(fields=['sample', 'probe']),
        ]
    
    @property
    def sigma_plus_1000(self):
        if self.sigma_kg_m3 is not None:
            return self.sigma_kg_m3 + 1000
        return None

    def __str__(self):
        return f"CTD {self.sample.sample_id} - {self.probe.probe_name}"
    def __str__(self):
        return f"CTD {self.sample.sample_id} - {self.probe.probe_name}"


