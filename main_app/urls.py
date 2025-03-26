from django.urls import path
from . import views
from .views import signup_view, logout_view, home, about, cocktail_index, CustomLoginView,cocktail_detail, edit_cocktail, delete_cocktail
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('browse/', views.browse, name='browse'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('create-cocktail/', views.create_cocktail, name='create_cocktail'),
    path('cocktails/<int:cocktail_id>/', views.cocktail_detail, name='cocktail_detail'),
    path('cocktails/<int:cocktail_id>/edit/', views.edit_cocktail, name='edit_cocktail'),
    path('cocktails/<int:cocktail_id>/delete/', views.delete_cocktail, name='delete_cocktail'),
]