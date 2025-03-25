from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, email=None):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

# User model definition
class User(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    createdCocktails = models.ManyToManyField('Cocktail', related_name='creators', blank=True)
    collections = models.JSONField(blank=True, null=True)  # Assuming CollectionSchema can be represented as JSON
    createdAt = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']  # Required fields for user creation

    def __str__(self):
        return self.username

# Collection Model
class Collection(models.Model):
    name = models.CharField(max_length=255)  # Name of the collection
    cocktails = models.ManyToManyField('Cocktail', related_name='collections')  # List of cocktails in the collection
    shared = models.BooleanField(default=False)  # Whether the collection is shared
    createdBy = models.ForeignKey('User', related_name='created_collections', on_delete=models.CASCADE)  # User who created the collection
    createdAt = models.DateTimeField(auto_now_add=True)  # Timestamp for when the collection was created

    def __str__(self):
        return self.name

# Comment Model
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.created_at}"

# Ingredient Model
class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('oz', 'Ounce (oz)'),
        ('tbsp', 'Tablespoon (tbsp)'),
        ('tsp', 'Teaspoon (tsp)'),
        ('cup', 'Cup'),
        ('ml', 'Milliliter (ml)'),
        ('cl', 'Centiliter (cl)'),
        ('liter', 'Liter'),
        ('pinch', 'Pinch'),
        ('dash', 'Dash'),
        ('slice', 'Slice'),
        ('whole', 'Whole'),
        ('drop', 'Drop'),
        ('none', 'None'),
    ]
    
    name = models.CharField(max_length=255)  # Name of the ingredient (e.g., "Lemon Juice")
    amount = models.CharField(max_length=255)  # Amount (e.g., "2", "1/2")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)  # Unit (e.g., oz, tbsp, etc.)
    garnish = models.BooleanField(default=False)  # Whether it's used as a garnish
    optional = models.BooleanField(default=False)  # Whether it's optional in the recipe
    
    def __str__(self):
        optional_str = " (Optional)" if self.optional else ""
        garnish_str = " (Garnish)" if self.garnish else ""
        return f"{self.amount} {self.unit} of {self.name}{optional_str}{garnish_str}"


# Cocktail Model
class Cocktail(models.Model):
    CATEGORY_CHOICES = [
        ('Classic', 'Classic Cocktails'),
        ('Tropical', 'Tropical Cocktails'),
        ('Signature', 'Signature Cocktails'),
        ('Modern', 'Modern Cocktails'),
        ('Frozen', 'Frozen Cocktails'),
        ('Highball', 'Highball Cocktails'),
        ('Lowball', 'Lowball / Rocks Cocktails'),
        ('Sours', 'Sours'),
        ('Punch', 'Punch Cocktails'),
        ('Shots', 'Shots'),
        ('Martini', 'Martinis'),
        ('Champagne', 'Champagne & Sparkling Cocktails'),
        ('Mocktail', 'Mocktails'),
    ]

    GLASS_TYPE_CHOICES = [
        ('Bowl', 'Bowl'),
        ('Champagne Flute', 'Champagne Flute'),
        ('Cocktail Glass', 'Cocktail Glass'),
        ('Collins Glass', 'Collins Glass'),
        ('Copper mug', 'Copper mug'),
        ('Coupe', 'Coupe'),
        ('Cup', 'Cup'),
        ('Goblet', 'Goblet'),
        ('Highball Glass', 'Highball Glass'),
        ('Hurricane Glass', 'Hurricane Glass'),
        ('Irish Coffee Glass', 'Irish Coffee Glass'),
        ('Margarita Glass', 'Margarita Glass'),
        ('Nick and Nora', 'Nick and Nora'),
        ('Pitcher', 'Pitcher'),
        ('Pub Glass', 'Pub Glass'),
        ('Rocks Glass', 'Rocks Glass'),
        ('Shooter', 'Shooter'),
        ('Snifter', 'Snifter'),
        ('Tiki', 'Tiki'),
        ('Wine Glass', 'Wine Glass'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    ingredients = models.ManyToManyField(Ingredient)  # Many-to-many relationship
    steps = models.JSONField()  # Array of steps (assuming JSONField for steps)
    image_url = models.URLField(blank=True, null=True)  # Store image URL
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    glass_type = models.CharField(max_length=20, choices=GLASS_TYPE_CHOICES)
    alcoholic = models.BooleanField(default=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_cocktails")
    likes = models.ManyToManyField(User, related_name="liked_cocktails", blank=True)  # Users who liked
    shared = models.BooleanField(default=False)
    comments = models.ManyToManyField(Comment, related_name="cocktail_comments", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()
