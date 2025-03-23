from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import SignUpForm, LoginForm

# Your existing cocktail data
cocktails = [
    {
        "name": "Margarita",
        "description": "A classic cocktail with a tangy lime kick.",
        "ingredients": [
            {"name": "Tequila", "amount": "2 oz"},
            {"name": "Triple sec", "amount": "1 oz"},
            {"name": "Lime juice", "amount": "1 oz"},
            {"name": "Salt", "amount": "For rim"}
        ],
        "steps": [
            "Rim the glass with salt.",
            "Shake the tequila, triple sec, and lime juice with ice.",
            "Strain into the glass and garnish with a lime wedge."
        ],
        "image": "https://example.com/images/margarita.jpg",
        "category": "Classic",
        "glassType": "Classic",
        "alcoholic": True,
        "creator": "user_123",
        "likes": ["user_456", "user_789"],
        "shared": True,
        "comments": [
            {"user": "user_101", "text": "Great flavor, one of my favorites!", "created_at": "2025-03-20T08:00:00"}
        ],
        "createdAt": "2025-03-18T08:00:00",
        "updatedAt": "2025-03-20T08:00:00"
    },
    {
        "name": "Pina Colada",
        "description": "A tropical cocktail made with rum, coconut cream, and pineapple juice.",
        "ingredients": [
            {"name": "Rum", "amount": "2 oz"},
            {"name": "Coconut cream", "amount": "1 oz"},
            {"name": "Pineapple juice", "amount": "3 oz"}
        ],
        "steps": [
            "Blend the rum, coconut cream, and pineapple juice with ice.",
            "Serve in a tall glass with a pineapple slice garnish."
        ],
        "image": "https://example.com/images/pina_colada.jpg",
        "category": "Tropical",
        "glassType": "Tropical",
        "alcoholic": True,
        "creator": "user_124",
        "likes": ["user_100", "user_111"],
        "shared": False,
        "comments": [
            {"user": "user_201", "text": "Perfect drink for summer!", "created_at": "2025-03-19T12:00:00"}
        ],
        "createdAt": "2025-03-15T09:00:00",
        "updatedAt": "2025-03-20T09:00:00"
    }
]

# Home view
def home(request):
    # Get shared cocktails (if you are using a model, modify this to query the database)
    shared_cocktails = [cocktail for cocktail in cocktails if cocktail["shared"]]  # Modify this based on your models
    
    return render(request, 'home.html', {
        'shared_cocktails': shared_cocktails
    })

# About view
def about(request):
    return render(request, 'about.html')

# Cocktail index view
def cocktail_index(request):
    if request.user.is_authenticated:
        print(f"User {request.user.username} is logged in.")
    else:
        print("No user is logged in.")
    shared_cocktails = [cocktail for cocktail in cocktails if cocktail["shared"]]
    return render(request, 'cocktails/index.html', {'cocktails': shared_cocktails})

# Signup view
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            return redirect('cocktail-index')  # Change 'home' to your homepage
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

# Use the built-in LoginView for login
class CustomLoginView(LoginView):
    template_name = 'login.html'  # You can change this to your custom template
    form_class = LoginForm


def logout_view(request):
    logout(request)
    return redirect('home')
