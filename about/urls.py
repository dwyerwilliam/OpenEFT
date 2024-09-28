from django.urls import path

from . import views

urlpatterns = [
    path('about', views.about, name='about'),
    path('features', views.features, name='features'),
    path('support', views.support, name='support'),
]