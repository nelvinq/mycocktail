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

class User(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    createdCocktails = models.ManyToManyField('Cocktail', related_name='creators', blank=True)
    collections = models.JSONField(blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return self.username

class Collection(models.Model):
    name = models.CharField(max_length=255) 
    description = models.TextField(null=True, blank=True)
    cocktails = models.ManyToManyField('Cocktail', related_name='collections')
    shared = models.BooleanField(default=False)
    createdBy = models.ForeignKey('User', related_name='created_collections', on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cocktail = models.ForeignKey('Cocktail', on_delete=models.CASCADE, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.created_at}"

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
    
    name = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    garnish = models.BooleanField(default=False)
    optional = models.BooleanField(default=False)
    
    def __str__(self):
        optional_str = " (Optional)" if self.optional else ""
        garnish_str = " (Garnish)" if self.garnish else ""
        return f"{self.amount} {self.unit} of {self.name}{optional_str}{garnish_str}"

class Step(models.Model):
    description = models.TextField()

    def __str__(self):
        return self.description

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
    ingredients = models.ManyToManyField(Ingredient)
    steps = models.ManyToManyField(Step) 
    image_url = models.URLField(blank=True, null=True)  
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    glass_type = models.CharField(max_length=20, choices=GLASS_TYPE_CHOICES)
    alcoholic = models.BooleanField(default=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_cocktails")
    likes = models.ManyToManyField(User, related_name="liked_cocktails", blank=True)
    shared = models.BooleanField(default=True)
    comments = models.ManyToManyField(Comment, related_name="cocktail_comments", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'ingredients': [ingredient.name for ingredient in self.ingredients.all()],
            'steps': [step.description for step in self.steps.all()],
            'image_url': self.image_url,
            'category': self.category,
            'glass_type': self.glass_type,
            'alcoholic': self.alcoholic,
            'creator': self.creator.username,
            'like_count': self.like_count(),
            'comment_count': self.comment_count(),
            'likes': [user.username for user in self.likes.all()],
            'comments': [comment.text for comment in self.comments.all()],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        } 