from django.urls import path
from . import views
from .views import signup_view, logout_view, home, about, cocktail_index, CustomLoginView,cocktail_detail, edit_cocktail, delete_cocktail, my_cocktails, my_collections, create_collection, edit_collection, add_to_collection, delete_collection
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
    path('cocktails/my-cocktails', views.my_cocktails, name='my_cocktails'),
    path('my-collections/', my_collections, name='my_collections'),
    path('create-collection/', create_collection, name='create_collection'),
    path('collections/<int:id>/', views.collection_detail, name='collection_detail'),
    path('collection/edit-collection/<int:collection_id>/', edit_collection, name='edit_collection'),
    path('cocktails/<int:cocktail_id>/add-to-collection/', views.add_to_collection, name='add_to_collection'),
    path('collection/<int:id>/delete/', views.delete_collection, name='delete_collection'),
]