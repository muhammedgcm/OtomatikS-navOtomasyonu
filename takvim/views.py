import random
from datetime import timedelta, time
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BolumSecimForm
from .models import Ders, Salon, Gozetmen, Sinav, Bolum
from collections import defaultdict
import pytz
from django.utils import timezone
from datetime import datetime

def otomatik_sinav_olustur(request):
    if request.method == 'POST':
        form = BolumSecimForm(request.POST)
        if form.is_valid():
            bolum = form.cleaned_data['bolum']
            tur = form.cleaned_data['tur']
            donem = form.cleaned_data['donem']  # Yeni eklenen dönem bilgisi
            baslangic_tarihi = form.cleaned_data['baslangic_tarihi']
            bitis_tarihi = form.cleaned_data['bitis_tarihi']

            # Eski sınavları sil (aynı bölüm ve türde)
            Sinav.objects.filter(ders__bolum=bolum, tur=tur).delete()

            # Dersleri seçilen döneme göre filtrele
            dersler = list(Ders.objects.filter(bolum=bolum, donem=donem))
            salonlar = list(Salon.objects.filter(bolum=bolum))
            gozetmenler = list(Gozetmen.objects.filter(bolum=bolum))

            if not salonlar or not gozetmenler:
                messages.error(request, "Bu bölüm için salon ya da gözetmen tanımlı değil.")
                return redirect('otomatik_sinav')

            sinav_saatleri = [time(8, 0), time(10, 0), time(13, 0), time(15, 0)]
            gun_sayisi = (bitis_tarihi - baslangic_tarihi).days + 1
            tarih_listesi = [baslangic_tarihi + timedelta(days=i) for i in range(gun_sayisi)]

            # Gözetmenlere rastgele ama eşit gün atama
            gozetmen_gunleri = defaultdict(list)
            for i, tarih in enumerate(tarih_listesi):
                g = gozetmenler[i % len(gozetmenler)]
                gozetmen_gunleri[g].append(tarih)

            gun_index = 0
            saat_index = 0
            turkey_tz = pytz.timezone('Europe/Istanbul')

            for ders in dersler:
                atandi = False
                deneme_sayisi = 0
                while not atandi and deneme_sayisi < 100:
                    sinav_tarihi = baslangic_tarihi + timedelta(days=gun_index)
                    if sinav_tarihi > bitis_tarihi:
                        messages.error(request, "Belirtilen tarih aralığında tüm sınavlar yerleştirilemedi.")
                        return redirect('otomatik_sinav')

                    sinav_saati = sinav_saatleri[saat_index]

                    # Aynı gün, aynı bölümde 2'den fazla sınav olmasın
                    ayni_gun_bolumde_sinav_sayisi = Sinav.objects.filter(
                        ders__bolum=bolum, tarih=sinav_tarihi
                    ).count()
                    if ayni_gun_bolumde_sinav_sayisi >= 2:
                        gun_index += 1
                        saat_index = 0
                        continue

                    # Aynı gün, aynı bölümde, aynı saatte sınav olmasın
                    cakisiyor_mu = Sinav.objects.filter(
                        ders__bolum=bolum, tarih=sinav_tarihi, saat=sinav_saati
                    ).exists()
                    if cakisiyor_mu:
                        saat_index = (saat_index + 1) % len(sinav_saatleri)
                        if saat_index == 0:
                            gun_index += 1
                        deneme_sayisi += 1
                        continue

                    uygun_salonlar = [
                        salon for salon in salonlar
                        if not Sinav.objects.filter(tarih=sinav_tarihi, saat=sinav_saati, salon=salon).exists()
                    ]

                    # Yalnızca o gün görevli gözetmenler
                    uygun_gozetmenler = [
                        g for g in gozetmenler
                        if sinav_tarihi in gozetmen_gunleri[g] and
                        not Sinav.objects.filter(tarih=sinav_tarihi, saat=sinav_saati, gozetmen=g).exists()
                    ]

                    if not uygun_salonlar or not uygun_gozetmenler:
                        saat_index = (saat_index + 1) % len(sinav_saatleri)
                        if saat_index == 0:
                            gun_index += 1
                        deneme_sayisi += 1
                        continue

                    salon = random.choice(uygun_salonlar)
                    gozetmen = random.choice(uygun_gozetmenler)

                    # Türkiye saatine göre aware datetime (sadece saat alanı için gerek yok, ama ileride datetime'a geçersen hazır olsun)
                    # sinav_datetime = timezone.make_aware(datetime.combine(sinav_tarihi, sinav_saati), turkey_tz)

                    sinav = Sinav(
                        ders=ders,
                        tarih=sinav_tarihi,
                        saat=sinav_saati,
                        salon=salon,
                        gozetmen=gozetmen,
                        tur=tur
                    )

                    try:
                        sinav.full_clean()
                        sinav.save()
                        atandi = True
                    except Exception:
                        deneme_sayisi += 1
                        continue

                if not atandi:
                    messages.warning(request, f"{ders.ad} dersi için sınav atanamadı.")
                else:
                    messages.success(request, f"{ders.ad} sınavı başarıyla atandı.")

            return redirect(f'/sinav-listesi/{bolum.id}/?tur={tur}&donem={donem.id}')

    else:
        form = BolumSecimForm()

    return render(request, 'takvim/otomatik_sinav.html', {'form': form})

def sinav_listesi(request, bolum_id=None):
    from .models import Donem, Bolum
    bolumler = Bolum.objects.all()
    donemler = Donem.objects.all()
    turler = [
        ('vize', 'Vize'),
        ('final', 'Final'),
        ('but', 'Bütünleme'),
    ]
    bolum_id = request.GET.get('bolum', bolum_id)
    tur = request.GET.get('tur')
    donem_id = request.GET.get('donem')
    bolum = Bolum.objects.filter(pk=bolum_id).first() if bolum_id else None
    donem = Donem.objects.filter(pk=donem_id).first() if donem_id else None
    sinavlar = None
    if bolum and tur and donem:
        sinavlar = Sinav.objects.filter(ders__bolum=bolum, tur=tur, ders__donem=donem).order_by('tarih', 'saat')
    return render(request, 'takvim/sinav_listesi.html', {
        'bolumler': bolumler,
        'donemler': donemler,
        'turler': turler,
        'bolum': bolum,
        'sinavlar': sinavlar,
        'tur': tur,
        'donem': donem
    })

def index(request):
    return render(request, 'takvim/index.html')
