from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User

from .models import Category, Post, Comment, Profile


class UserEditForm(ModelForm):
    # This form will allow users to edit their first name, last name, 
    # and e-mail, which are stored in the built-in User model.
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        

class ProfileEditForm(ModelForm):
    # This form will allow users to edit the extra data we save in the
    # custom Profile model. Users will be able to edit their date of birth 
    # and upload a picture for their profile.
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'bio','photo'] 



class PostForm(ModelForm):
    # This form is the same that will be used to create a new post as well
    # as updating an existing post. The caveat here is that in updating an existing 
    # post, we need a reference to that post, in the form of a primary key
    class Meta:
        model = Post
        fields = '__all__'
        exclude = ['author', 'participants']
         

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class SendEmailForm(forms.Form):
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    # Later i will need to remove this to field, because this form will be supposed 
    # to be used to send emails to my email address
    to = forms.EmailField()
    body = forms.CharField(required=True, max_length=250, widget=forms.Textarea)
    

class ContactUsForm(forms.Form):
    pass

    
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'
        exclude = ['post', 'user']
        
        
# If we do want to create a custom user registration form, here is how you can go about it
# First we create a form for users to enter their username and password
# An alternative to this approach is making use of the default UserCreationForm from Django
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput) 
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    
    
    class Meta:
        # Because we are creating a custom user registration form,
        # have to make sure to import the User model above
        model = User
        fields = ['username', 'first_name', 'email']
        
    # We added two additional fields password and password2 for the user
    # to set their password and confirm it   
    
    # The method clean_password2() is used to check the second password against the first 
    # one and invalidate the form if the passwords do not match
    def clean_password2(self):
        # we call the data submitted by the user as data:
        data = self.cleaned_data
        if data['password'] != data['password2']:
            raise forms.ValidationError('Passwords do not match')
        return data['password2']