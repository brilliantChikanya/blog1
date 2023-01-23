from email.policy import default
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
import uuid




# Create your models here.
class Profile(models.Model):
    # We want to extend the user model to include additional data about our users, 
    # hence the Profile model, with a one to one relationship with the User model
    
    # We use the AUTH_USER_MODEL setting to refer to the User model in defining the Profile model's 
    # relations to the User model, instead of referring to the auth User model directly:
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(default='')
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='images/', blank=True)
    # We will add other fields as we go...
    
    def __str__(self):
        return f"Profile for user {self.user.username}"
    




class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    def __str__(self):
        return self.name



class Post(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    image = models.ImageField(upload_to='images/',blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # slug = models.SlugField(blank=True, default='',)
    #id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("post_view", args=[str(self.slug)])
    
    # This method handles image issues by checking if an image exists or not in the 
    # database, then either returns the url or an empty string:
    
    @property
    def imageURL(self):
        
        try:
            img = self.image.url
        except:
            img = ''
        return img
    
    
    
    class Meta:
        ordering = ['-updated', '-created']
    



class Comment(models.Model):
    body = models.TextField(null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated', '-created']
    
    
    def __str__(self):
        return self.body[0:50]

