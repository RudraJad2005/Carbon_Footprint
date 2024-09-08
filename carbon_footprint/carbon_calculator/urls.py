from django.urls import path
from . import views
from .views import carbon_footprint_view, register, air_quality_view

urlpatterns = [
    path('', views.home, name='index'),
    path('carbon-footprint/', carbon_footprint_view, name='carbon_footprint_view'),
    path('about/', views.about, name='about'),
    path('login/', views.login, name='login'),
    path('register/', register, name='register'),
    path('blog/', views.blog, name='blog'),
    path('donate/', views.donate, name='donate'),
    path('data_represent/', views.data_r, name='data_represent'),
    path('resources/', views.resources, name='resources'),
    path('carbon_footprint_history/', views.carbon_footprint_history_view, name='carbon_footprint_history'),
    path('contact/', views.contact, name='contact'),
    path('air-quality/', air_quality_view, name='air_quality'),
]
