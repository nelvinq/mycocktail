import os, mimetypes, json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, AuthenticationForm, CocktailForm, LoginForm, CollectionForm, CommentForm
from .models import Cocktail, Ingredient, Step, Collection, Comment
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core import serializers
from django.urls import reverse_lazy
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt 
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Home view
def home(request):
    shared_cocktails = Cocktail.objects.filter(shared=True)
    return render(request, 'cocktails/browse.html', {'cocktails': shared_cocktails})

# About view
def about(request):
    return render(request, 'about.html')

# Search and filter Cocktails
def search_cocktails(query, category='', alcoholic=''):
    cocktails = Cocktail.objects.all()
    if query:
        cocktails = cocktails.filter(Q(name__icontains=query))
    if category:
        cocktails = cocktails.filter(category=category)
    if alcoholic:
        is_alcoholic = alcoholic == 'yes'
        cocktails = cocktails.filter(alcoholic=is_alcoholic)
    return cocktails

# Browse view
def browse(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    alcoholic_filter = request.GET.get('alcoholic', '')

    cocktails = search_cocktails(search_query, category_filter, alcoholic_filter)
    shared_cocktails = cocktails.filter(shared=True)

    return render(request, 'cocktails/browse.html', {
        'cocktails': shared_cocktails,
        'search_query': search_query,
        'category_filter': category_filter,
        'alcoholic_filter': alcoholic_filter,
    })

# User Cocktail index view
def my_cocktails(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    alcoholic_filter = request.GET.get('alcoholic', '')

    cocktails = search_cocktails(search_query, category_filter, alcoholic_filter)
    user_cocktails = cocktails.filter(creator=request.user)

    return render(request, 'cocktails/my_cocktails.html', {
        'cocktails': user_cocktails,
        'search_query': search_query,
        'category_filter': category_filter,
        'alcoholic_filter': alcoholic_filter,
    })

# Liked Cocktail index view
@login_required
def liked_cocktails(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    alcoholic_filter = request.GET.get('alcoholic', '')

    cocktails = search_cocktails(search_query, category_filter, alcoholic_filter)
    liked_cocktails = cocktails.filter(likes=request.user)

    return render(request, 'cocktails/liked_cocktails.html', {
        'liked_cocktails': liked_cocktails,
        'search_query': search_query,
        'category_filter': category_filter,
        'alcoholic_filter': alcoholic_filter,
    })

# View Collection Details
@login_required
def collection_detail(request, id):
    collection = get_object_or_404(Collection, id=id)

    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '')
    alcoholic_filter = request.GET.get('alcoholic', '')

    cocktails = collection.cocktails.all()

    filtered_cocktails = search_cocktails(search_query, category_filter, alcoholic_filter).filter(id__in=cocktails.values_list('id', flat=True))

    return render(request, 'collections/collection_detail.html', {
        'collection': collection,  
        'cocktails': filtered_cocktails,    
        'search_query': search_query,
        'category_filter': category_filter,
        'alcoholic_filter': alcoholic_filter,
    })

# My Collection View
@login_required
def my_collections(request):
    collections = Collection.objects.filter(createdBy=request.user)
    return render(request, 'collections/my_collections.html', {'collections': collections})

# Create Collection View
@login_required
def create_collection(request):
    if request.method == "POST":
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.createdBy = request.user
            collection.save()
            return redirect('my_collections')
    else:
        form = CollectionForm()
    return render(request, 'collections/create_collection.html', {'form': form})

# Edit Collection View
@login_required
def edit_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, createdBy=request.user)
    if request.method == "POST":
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
        return redirect('collection_detail', id=collection.id)
    else:
        form = CollectionForm(instance=collection)
    return render(request, 'collections/edit_collection.html', {'form': form, 'collection': collection})

# Add to Collection View
@login_required
def add_to_collection(request, cocktail_id):
    cocktail = get_object_or_404(Cocktail, id=cocktail_id)
    user_collections = Collection.objects.filter(createdBy=request.user)

    if request.method == "POST":
        collection_id = request.POST.get("collection_id")
        collection = get_object_or_404(Collection, id=collection_id)

        if cocktail in collection.cocktails.all():
            messages.warning(request, "Cocktail is already in this collection!")
        else:
            collection.cocktails.add(cocktail)
            messages.success(request, "Cocktail added to collection successfully!")

        return redirect('cocktail_detail', cocktail_id=cocktail.id)

    return render(request, 'cocktails/add_to_collection.html', {
        'cocktail': cocktail,
        'user_collections': user_collections
    })

login_required
def remove_cocktail(request, cocktail_id):
    if request.method == 'DELETE':
        cocktail = get_object_or_404(Cocktail, id=cocktail_id)
        cocktail.delete()
        return JsonResponse({'message': 'Cocktail removed successfully'}, status=200)
    return JsonResponse({'message': 'Invalid request'}, status=400)

@login_required
def delete_collection(request, id):
    collection = get_object_or_404(Collection, id=id)

    if request.method == "POST":
        collection.delete()
        messages.success(request, "Collection deleted successfully!")
        return redirect('my_collections')

    return render(request, 'collections/delete_collection.html', {'collection': collection})

def like_cocktail(request, cocktail_id):
    cocktail = get_object_or_404(Cocktail, id=cocktail_id)

    if request.user in cocktail.likes.all():
        cocktail.likes.remove(request.user)
        liked = False
    else:
        cocktail.likes.add(request.user)
        liked = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': cocktail.likes.count(),
            'status': 'liked' if liked else 'unliked'
        })

    return redirect('cocktail_detail', cocktail_id=cocktail.id)

# Add a comment
@login_required
def add_comment(request, cocktail_id):
    cocktail = get_object_or_404(Cocktail, id=cocktail_id)

    if request.method == 'POST':
        text = request.POST.get('text')

        if text and text.strip():
            comment = Comment.objects.create(user=request.user, text=text, cocktail=cocktail)
            cocktail.comments.add(comment)
            cocktail.save()
            messages.success(request, "Comment added successfully!")
            return redirect('cocktail_detail', cocktail_id=cocktail.id)

    return redirect('cocktail_detail', cocktail_id=cocktail.id)

#Edit comments
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        text = request.POST.get('text')
        comment.text = text
        comment.save()
        messages.success(request, "Comment edited successfully!")
        return JsonResponse({'success': True, 'new_text': comment.text})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

#Delete comments
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.user:
        cocktail_id = comment.cocktail.id
        comment.delete()
        messages.success(request, "Comment deleted successfully!")
        return redirect('cocktail_detail', cocktail_id=cocktail_id)

    return redirect('cocktail_detail', cocktail_id=comment.cocktail.id)

# Create Cocktail
@login_required
def create_cocktail(request):
    if request.method == "POST":
        try:
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST

            name = data.get("name")
            description = data.get("description", "")
            category = data.get("category")
            glass_type = data.get("glass_type")
            alcoholic = data.get("alcoholic", True)
            if isinstance(alcoholic, str):
                alcoholic = alcoholic.lower() in ["true", "1", "yes", "on"] 
 
            shared = data.get("shared", True)
            if isinstance(shared, str):
                shared = shared.lower() in ["true", "1", "yes", "on"] 

            steps_data = request.POST.getlist('steps[]')
            steps = [Step.objects.create(description=step_desc) for step_desc in steps_data]

            image_url = None
            if "image" in request.FILES:
                image = request.FILES["image"]
                
                file_path = f"cocktail_images/{request.user.username}/{image.name}"

                file_content = image.read()
                content_type = mimetypes.guess_type(image.name)[0] or "application/octet-stream"

                try:
                    res = supabase.storage.from_("cocktail-images").upload(
                        path=file_path,
                        file=file_content,
                        file_options={"content-type": content_type}
                    )

                    image_url = supabase.storage.from_("cocktail-images").get_public_url(file_path)

                except Exception as e:
                    return JsonResponse({"error": f"Failed to upload image: {str(e)}"}, status=400)

            cocktail = Cocktail.objects.create(
                name=name,
                description=description,
                category=category,
                glass_type=glass_type,
                alcoholic=alcoholic,
                shared=shared,
                creator=request.user,
                image_url=image_url,
            )

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

            for ingredient_data in ingredient_list:
                ingredient = Ingredient.objects.create(
                    name=ingredient_data["name"],
                    amount=ingredient_data["amount"],
                    unit=ingredient_data["unit"],
                    garnish=ingredient_data.get("garnish", False),
                    optional=ingredient_data.get("optional", False),
                )
                cocktail.ingredients.add(ingredient)

            cocktail.steps.set(steps) 

            cocktail.save()

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
    comments = cocktail.comments.all().order_by("created_at")

    if request.user.is_authenticated:
        user_collections = Collection.objects.filter(createdBy=request.user)
    else:
        user_collections = []
        
    return render(request, 'cocktails/cocktail_detail.html', {'cocktail': cocktail, 'user_collections': user_collections, 'comments': comments})
    
# Edit cocktail
@login_required
def edit_cocktail(request, cocktail_id):
    try:
        cocktail = Cocktail.objects.get(id=cocktail_id)

        if request.method == 'GET':
            cocktail_data = {
                'id': cocktail.id,
                'name': cocktail.name,
                'description': cocktail.description,
                'category': cocktail.category,
                'glass_type': cocktail.glass_type,
                'alcoholic': cocktail.alcoholic,
                'shared': cocktail.shared,
                'ingredients': [
                    {
                        'name': ingredient.name,
                        'amount': ingredient.amount,
                        'unit': ingredient.unit,
                        'garnish': ingredient.garnish,
                        'optional': ingredient.optional
                    } for ingredient in cocktail.ingredients.all()
                ],
                'steps': list(cocktail.steps.all().values_list('description', flat=True))
            }
            return JsonResponse({'cocktail': cocktail_data})
        
        elif request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('description')
            category = request.POST.get('category')
            glass_type = request.POST.get('glass_type')
            alcoholic = request.POST.get('alcoholic') == 'on'
            shared = request.POST.get('shared') == 'on'
            ingredients_names = request.POST.getlist('ingredients_name[]')
            ingredients_amounts = request.POST.getlist('ingredients_amount[]')
            ingredients_units = request.POST.getlist('ingredients_unit[]')
            ingredients_garnishes = request.POST.getlist('ingredients_garnish[]')
            ingredients_optionals = request.POST.getlist('ingredients_optional[]')
            steps = request.POST.getlist('steps[]')

            image_url = None
            if "image" in request.FILES:
                image = request.FILES["image"] 
                
                file_path = f"cocktail_images/{request.user.username}/{image.name}"

                file_content = image.read()
                content_type = mimetypes.guess_type(image.name)[0] or "application/octet-stream"

                try:
                    res = supabase.storage.from_("cocktail-images").upload(
                        path=file_path,
                        file=file_content,
                        file_options={"content-type": content_type}
                    )

                    image_url = supabase.storage.from_("cocktail-images").get_public_url(file_path)

                except Exception as e:
                    return JsonResponse({"error": f"Failed to upload image: {str(e)}"}, status=400)


            cocktail.name = name
            cocktail.description = description
            cocktail.category = category
            cocktail.glass_type = glass_type
            cocktail.alcoholic = alcoholic
            cocktail.shared = shared
            cocktail.image_url=image_url

            if len(ingredients_garnishes) < len(ingredients_names):
                ingredients_garnishes.extend([False] * (len(ingredients_names) - len(ingredients_garnishes)))
            
            if len(ingredients_optionals) < len(ingredients_names):
                ingredients_optionals.extend([False] * (len(ingredients_names) - len(ingredients_optionals)))

            if not (len(ingredients_names) == len(ingredients_amounts) == len(ingredients_units) == len(ingredients_garnishes) == len(ingredients_optionals)):
                return JsonResponse({'error': 'Mismatch in ingredient data lengths'}, status=400)

            cocktail.ingredients.clear()
            for i in range(len(ingredients_names)):
                garnish = ingredients_garnishes[i] if isinstance(ingredients_garnishes[i], bool) else ingredients_garnishes[i].lower() in ["true", "1", "yes", "on"]
                optional = ingredients_optionals[i] if isinstance(ingredients_optionals[i], bool) else ingredients_optionals[i].lower() in ["true", "1", "yes", "on"]

                ingredient = Ingredient.objects.create(
                    name=ingredients_names[i],
                    amount=ingredients_amounts[i],
                    unit=ingredients_units[i],
                    garnish=garnish,
                    optional=optional,
                )
                cocktail.ingredients.add(ingredient)

            cocktail.steps.clear()
            for step_desc in steps:
                step = Step.objects.create(description=step_desc)
                cocktail.steps.add(step)

            cocktail.save()

            return JsonResponse({'message': 'Cocktail updated successfully'}, status=200)

    except Cocktail.DoesNotExist:
        return JsonResponse({'error': 'Cocktail not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Delete cocktail
@login_required
def delete_cocktail(request, cocktail_id):
    cocktail = get_object_or_404(Cocktail, id=cocktail_id, creator=request.user)
    if request.method == "POST":
        cocktail.delete()
        messages.success(request, "Cocktail deleted successfully!")
        return redirect('my_cocktails')

    return render(request, 'cocktails/delete_cocktail.html', {'cocktail': cocktail})

# Signup view
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('browse')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

# Use the built-in LoginView for login
class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = LoginForm

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is None:
            messages.error(self.request, "Invalid credentials. Please try again.")

        return self.render_to_response(self.get_context_data(form=form))

def logout_view(request):
    logout(request)
    return redirect('browse')
