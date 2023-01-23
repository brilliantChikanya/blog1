from django.contrib import admin

from .models import Category, Post, Comment, Profile

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    # prepopulated_fields = {'slug': ('title',)}
    pass


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'photo']


admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Profile, ProfileAdmin)
