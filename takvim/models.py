from django.db import models

class Bolum(models.Model):
    ad = models.CharField(max_length=100)

    def __str__(self):
        return self.ad

# 🆕 Donem modeli eklendi
class Donem(models.Model):
    ad = models.CharField(max_length=20)

    def __str__(self):
        return self.ad

class Ders(models.Model):
    ad = models.CharField(max_length=200)
    bolum = models.ForeignKey(Bolum, on_delete=models.CASCADE)
    donem = models.ForeignKey(Donem, on_delete=models.CASCADE, null=True, blank=True)  # ✅ null ve blank eklendi

    def __str__(self):
        return f"{self.ad} ({self.bolum.ad})"

class Salon(models.Model):
    ad = models.CharField(max_length=100)
    bolum = models.ForeignKey(Bolum, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.ad} - {self.bolum.ad}"

class Gozetmen(models.Model):
    ad = models.CharField(max_length=100)
    bolum = models.ForeignKey(Bolum, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.ad} ({self.bolum.ad})"

class Sinav(models.Model):
    SINAV_TURLERI = [
        ('vize', 'Vize'),
        ('final', 'Final'),
        ('but', 'Bütünleme'),
    ]

    ders = models.ForeignKey(Ders, on_delete=models.CASCADE)
    tarih = models.DateField()
    saat = models.TimeField()
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    gozetmen = models.ForeignKey(Gozetmen, on_delete=models.CASCADE)
    tur = models.CharField(max_length=10, choices=SINAV_TURLERI, default='vize')

    def __str__(self):
        return f"{self.ders.ad} ({self.get_tur_display()}) - {self.tarih} {self.saat}"
