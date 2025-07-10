from django.contrib import admin
from .models import Bolum, Ders, Salon, Gozetmen, Sinav, Donem  # 👈 Donem'i içe aktar

# 👇 Donem modelini admin paneline kaydet
admin.site.register(Donem)

admin.site.register(Bolum)
admin.site.register(Ders)
admin.site.register(Salon)
admin.site.register(Gozetmen)
admin.site.register(Sinav)
