from django import forms
from .models import Bolum, Donem  # 👈 Donem modelini içe aktardık

class BolumSecimForm(forms.Form):
    bolum = forms.ModelChoiceField(queryset=Bolum.objects.all(), label="Bölüm Seçin")

    SINAV_TURLERI = [
        ('vize', 'Vize'),
        ('final', 'Final'),
        ('but', 'Bütünleme'),
    ]
    tur = forms.ChoiceField(choices=SINAV_TURLERI, label="Sınav Türü")

    # 🆕 Dönem alanı burada eklendi
    donem = forms.ModelChoiceField(queryset=Donem.objects.all(), label="Dönem Seçin")

    baslangic_tarihi = forms.DateField(
        label="Sınav Başlangıç Tarihi",
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    bitis_tarihi = forms.DateField(
        label="Sınav Bitiş Tarihi",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
