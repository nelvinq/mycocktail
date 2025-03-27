import os
import mimetypes
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, AuthenticationForm, CocktailForm, LoginForm
from .models import Cocktail, Ingredient, Step
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core import serializers
from django.urls import reverse_lazy
from supabase import create_client


# Initialize Supabase Client
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Home view
def home(request):
    shared_cocktails = Cocktail.objects.filter(shared=True)  # Reuse the same query
    return render(request, 'home.html', {'cocktails': shared_cocktails})

# About view
def about(request):
    return render(request, 'about.html')

# Browse view
def browse(request):
    shared_cocktails = Cocktail.objects.filter(shared=True)
    return render(request, 'cocktails/browse.html', {'cocktails': shared_cocktails})

# Cocktail index view
def cocktail_index(request):
    shared_cocktails = Cocktail.objects.filter(shared=True)
    return render(request, 'cocktails/index.html', {'cocktails': shared_cocktails})

# Create Cocktail
@login_required
def create_cocktail(request):
    if request.method == "POST":
        try:
            # Parse JSON data from the request
            # Determine if the request is JSON or Form Data
            if request.content_type == "application/json":
                data = json.loads(request.body)  # Handle JSON request
            else:
                data = request.POST  # Handle form data

            # Extract basic data
            name = data.get("name")
            description = data.get("description", "")
            category = data.get("category")
            glass_type = data.get("glass_type")
            alcoholic = data.get("alcoholic", True)
            if isinstance(alcoholic, str):  # Handle form-data case
                alcoholic = alcoholic.lower() in ["true", "1", "yes", "on"] 
 
            shared = data.get("shared", None)
            if shared is not None:
                if isinstance(shared, str):  # Only apply lower() if it's a string
                    shared = shared.lower() in ["true", "1", "yes", "on"]
                # If shared is already a boolean, don't apply .lower()
            else:
                shared = False  # Default to False if shared is not provided

            steps_data = request.POST.getlist('steps[]')  # Get the steps from the form
            steps = [Step.objects.create(description=step_desc) for step_desc in steps_data]

            # Handle Image Upload
            image_url = None
            if "image" in request.FILES:
                image = request.FILES["image"]  # InMemoryUploadedFile
                
                # Generate unique file path for storage
                file_path = f"cocktail_images/{request.user.username}/{image.name}"

                # Read file content and determine MIME type
                file_content = image.read()
                content_type = mimetypes.guess_type(image.name)[0] or "application/octet-stream"

                try:
                    # Upload to Supabase Storage
                    res = supabase.storage.from_("cocktail-images").upload(
                        path=file_path,
                        file=file_content,
                        file_options={"content-type": content_type}
                    )

                    # Get Public URL of uploaded image
                    image_url = supabase.storage.from_("cocktail-images").get_public_url(file_path)

                except Exception as e:
                    return JsonResponse({"error": f"Failed to upload image: {str(e)}"}, status=400)

            # Create the cocktail instance
            cocktail = Cocktail.objects.create(
                name=name,
                description=description,
                category=category,
                glass_type=glass_type,
                alcoholic=alcoholic,
                shared=shared,
                creator=request.user,  # Assign the creator
                image_url=image_url,
            )

            # Process and save ingredients
            ingredient_list = data.get("ingredients", [])
            if not ingredient_list and request.POST.getlist('ingredients_name[]'):
                ingredient_list = []
                names = request.POST.getlist('ingredients_name[]')
                amounts = request.POST.getlist('ingredients_amount[]')
                units = request.POST.getlist('ingredients_unit[]')
                garnishes = request.POST.getlist('ingredients_garnish[]')
                optionals = request.POST.getlist('ingredients_optional[]')

                for i in range(len(names)):
                    ingredient_list.append({
                        "name": names[i],
                        "amount": amounts[i],
                        "unit": units[i],
                        "garnish": garnishes[i].lower() in ["true", "1", "yes", "on"],
                        "optional": optionals[i].lower() in ["true", "1", "yes", "on"],
                    })

            # Save ingredients to DB
            for ingredient_data in ingredient_list:
                ingredient = Ingredient.objects.create(
                    name=ingredient_data["name"],
                    amount=ingredient_data["amount"],
                    unit=ingredient_data["unit"],
                    garnish=ingredient_data.get("garnish", False),
                    optional=ingredient_data.get("optional", False),
                )
                cocktail.ingredients.add(ingredient)

            # Set the steps for the cocktail
            cocktail.steps.set(steps) 

            cocktail.save()  # Save final cocktail with ingredients

            return JsonResponse({"message": "Cocktail created successfully!"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except ValidationError as e:
            return JsonResponse({"error": f"Validation error: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)

# View cocktail details
def cocktail_detail(request, cocktail_id):
    cocktail = Cocktail.objects.get(id=cocktail_id)
    print({cocktail.description})
    return render(request, 'cocktails/cocktail_detail.html', {'cocktail': cocktail})
    
# Edit cocktail (only creator can edit)
@login_required
def edit_cocktail(request, cocktail_id):
    cocktail = Cocktail.objects.get(id=cocktail_id)
    return render(request, 'edit_cocktail_modal.html', {'cocktail': cocktail})

# Delete cocktail (only creator can delete)
@login_required
def delete_cocktail(request, cocktail_id):
    cocktail = get_object_or_404(Cocktail, id=cocktail_id, creator=request.user)
    if request.method == "POST":
        cocktail.delete()
        return redirect('browse')  # Redirect to the cocktail list after deletion

    return render(request, 'cocktails/delete_cocktail.html', {'cocktail': cocktail})

# Signup view
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            return redirect('browse')  # Change 'home' to your homepage
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

# Use the built-in LoginView for login
class CustomLoginView(LoginView):
    template_name = 'login.html'  # Make sure the path is correct
    form_class = LoginForm

    def form_valid(self, form):
        # Return to the usual page when login is successful
        return super().form_valid(form)

    def form_invalid(self, form):
        # Handling invalid login
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is None:
            # If no user is found with these credentials, add an error
            messages.error(self.request, "Invalid credentials. Please try again.")

        # Return the form with errors back to the page
        return self.render_to_response(self.get_context_data(form=form))

def logout_view(request):
    logout(request)
    return redirect('home')
