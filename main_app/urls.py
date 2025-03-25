from django.urls import path
from . import views
from .views import signup_view, logout_view, home, about, cocktail_index
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('browse/', views.browse, name='browse'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('create-cocktail/', views.create_cocktail, name='create_cocktail'),
    ]