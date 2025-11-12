from django.urls import path
from . import views
from .views import SearchView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

urlpatterns = [
    path('', views.home, name="home"),
    path("ads.txt", serve, {
        'path': "ads.txt",
        'document_root': os.path.join(settings.BASE_DIR, "templates"),
        'show_indexes': False
    }),
    path('privacypolicy/', views.gyk, name='gyakorikerdesek'),
    path('aboutus/', views.ab, name='aboutus'),
    path('whatispsl/', views.wp, name='whatispsl'),
    path('aboutlooksmaxxing/', views.looks, name='aboutlooksmaxxing'),
    path('psychology-of-self-image/', views.pos, name='pos'),
    path('contact/', views.contact, name='contact'),
    path('terms-of-use/', views.term, name='term'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
