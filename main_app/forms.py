from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms
from .models import Cocktail, Ingredient
from django.core.exceptions import ValidationError

User = get_user_model()

# Signup Form
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        # Add custom validation if necessary
        if not username or not password:
            raise ValidationError("Both username and password are required.")
        return cleaned_data

class CocktailForm(forms.ModelForm):
    # Fields for Cocktail details
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Cocktail Name'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Cocktail Description'}), required=False)
    category = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Category'}))
    glass_type = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Glass Type'}))
    alcoholic = forms.BooleanField(initial=True, required=False)  # Boolean to check if alcoholic or not
    shared = forms.BooleanField(initial=False, required=False)    
    
    # Handling image upload
    image = forms.ImageField(required=False)
    
    # Fields for ingredients and steps
    ingredient_name = forms.CharField(max_length=100, required=False)
    ingredient_amount = forms.CharField(max_length=100, required=False)
    ingredient_unit = forms.CharField(max_length=100, required=False)
    ingredient_garnish = forms.BooleanField(initial=False, required=False)
    ingredient_optional = forms.BooleanField(initial=False, required=False)
    
    steps = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Steps for the Cocktail'}), required=False)

    class Meta:
        model = Cocktail
        fields = ['name', 'description', 'category', 'glass_type', 'alcoholic', 'image']
    
    # Method to clean ingredients
    def clean_ingredients(self):
        ingredients = []
        for i in range(len(self.cleaned_data.get('ingredient_name', []))):
            ingredients.append({
                'name': self.cleaned_data.get('ingredient_name')[i],
                'amount': self.cleaned_data.get('ingredient_amount')[i],
                'unit': self.cleaned_data.get('ingredient_unit')[i],
                'garnish': self.cleaned_data.get('ingredient_garnish')[i],
                'optional': self.cleaned_data.get('ingredient_optional')[i],
            })
        return ingredients

    # Method to clean steps (could be extended as necessary)
    def clean_steps(self):
        return [step.strip() for step in self.cleaned_data.get('steps', '').split('\n') if step.strip()]

from django import forms
from .models import Collection

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'shared']