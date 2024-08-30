from django.urls import path
from . import views
from .views import carbon_footprint_view

urlpatterns = [
    path('', views.home, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('carbon-footprint/', carbon_footprint_view, name='carbon_footprint_view'),
]
