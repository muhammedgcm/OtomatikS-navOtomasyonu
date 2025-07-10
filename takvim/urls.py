from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('otomatik-sinav/', views.otomatik_sinav_olustur, name='otomatik_sinav'),
    path('sinav-listesi/', views.sinav_listesi, name='sinav_listesi'),
    path('sinav-listesi/<int:bolum_id>/', views.sinav_listesi, name='sinav_listesi'),
]
