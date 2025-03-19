from django.urls import path
from . import views
from .views import signup_view, login_view, logout_view


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('browse/', views.cocktail_index, name='cocktail-index'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]