from django.urls import path
from . import views
from .views import carbon_footprint_view

urlpatterns = [
    path('', views.home, name='index'),
    path('carbon-footprint/', carbon_footprint_view, name='carbon_footprint_view'),
    path('about/', views.about, name='about'),
    path('data_represent/', views.data_r, name='data_represent'),
    path('resources/', views.resources, name='resources'),
]
