from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('opportunites/', views.opportunites, name='opportunites'),
]


