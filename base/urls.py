from django.urls import path
from . import views
from .views import SearchView

urlpatterns = [
    path('', views.home, name="home"),
    path('room/<int:pk>/', views.room, name="room"),
    path('sneakerek/', views.sneakerek, name="sneakerek"),
    path('search/', SearchView.as_view(), name='search'),
    path('gyakorikerdesek/', views.gyk, name='gyakorikerdesek'),
]
