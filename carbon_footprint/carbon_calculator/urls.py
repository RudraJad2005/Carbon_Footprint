from django.urls import path
from . import views
from .views import carbon_footprint_view

urlpatterns = [
    path('', views.home, name='index'),
    path('carbon-footprint/', carbon_footprint_view, name='carbon_footprint_view'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('donate/', views.donate, name='donate'),
    path('data_represent/', views.data_r, name='data_represent'),
    path('resources/', views.resources, name='resources'),
    path('carbon_footprint_history/', views.carbon_footprint_history_view, name='carbon_footprint_history'),
    path('contact/', views.contact, name='contact'),
]
