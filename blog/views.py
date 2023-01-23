from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q # enables us to wrap search parameters
from blog.models import Category, Post, Comment, Profile
from .forms import PostForm, SendEmailForm, CommentForm, UserEditForm, ProfileEditForm, ContactUsForm
from django.core.paginator import Paginator

# Create your views here.
def loginPage(request):
    page = 'login'
    # If the user is already logged in, we want to send them to the home page.
    # They must not be able to login again
    if request.user.is_authenticated:
        return redirect('home')
    
    # get the username and password entered in by the user
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        # first, lets make sure the user exists. if not we throw an error message
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
    # If the user does exist, then we continue as follows:
        # make sure the credentials provided are correct
        user = authenticate(request, username=username, password=password)
        # The authenticate method either returns a user object that matches these credentials
        # or it will return an error
        
        if user is not None:
            # lets go ahead and login the user. This will create a session in the database and inside the browser
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exist')
       
    context = {'page': page}
    return render(request, 'blog/login_register.html', context)



def registerUser(request):
    # page = 'register' 
    form = UserCreationForm()
    # Here we make use of the default UserCreationForm, but we can also create
    # a form based on the User model and use it here instead. A sample form is provided 
    # in forms.py, UserRegistrationForm
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid:
            # Create a new user object, but not saving it yet:
            user = form.save(commit=False)
            user.username = user.username.lower()
            # save the user object:
            user.save()
            
            # Create the User profile
            # When users register on our site, we create an empty profile associated with them:
            profile = Profile.objects.create(user=user)
            
            # Then log in the user:
            login(request, user)
            
            # Send them to the home page:
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
    else:
        form = UserCreationForm()
    
    context = {'form': form}
    return render(request, 'blog/login_register.html', context)

"""
    # If instead of the default UserCreationForm, we decide to make use of a custom form
    # such as in this case, UserRegistrationForm, we would continue like this:
    
    form = UserRegistrationForm()
    # Here we make use of the form based on the User model    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid:
            # Create a new user object, but not saving it yet:
            user = form.save(commit=False)
            user.username = user.username.lower()
            # The view for creating user accounts (registering users) is simplified, 
            # because here, instead of saving the raw password entered by the user, 
            # we use the set_password() method of the User model that handles 
            # encryption to save for safety.
            
            # set the chosen password:
            user.set_password(form.cleaned_data['password'])
            # save the user object:
            user.save()
            login(request, user)
            return redirect('home')
    
"""   


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    posts = user.post_set.all()
    post_comments = user.comment_set.all()
    categorys = Category.objects.all()
    
    context = {'user': user, 'posts': posts, 'categorys': categorys, 'post_comments':post_comments}
    return render(request, 'blog/profile.html', context)




   
@login_required(login_url='login')
def editProfile(request):
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, instance=request.user.profile, files=request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            return redirect('home')
            
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        
        
    
    context = {'user_form':user_form, 'profile_form':profile_form}
    return render(request, 'blog/edit_profile.html', context)
            



def logoutUser(request):
    # For logout functionality we do not need a template, but we just make use of the logout function
    logout(request)
    return redirect('home')
    


def home (request):
    # q is a search parameter. It can be any value but that's how i decided to call it
    q = request.GET.get('q') if request.GET.get('q') != None else ''    # q is going to be whatever is passed in the url
    # We are using the Post model to search because it has a one to many relationship
    # with the Category model. So we are able to search for posts of a particular category
    
    posts = Post.objects.filter(
        Q(category__name__icontains=q) |
        Q(title__icontains=q) |
        Q(body__icontains=q) |
        Q(author__username__icontains=q)
    )
    
    # After getting all the posts, we only want to show 5 on a single page. For that:
    # Set up Pagination, and create an instance
    # We instantiate the Paginator class with the number of objects we want to display in each page:
    p = Paginator(Post.objects.filter(
        Q(category__name__icontains=q) |
        Q(title__icontains=q) |
        Q(body__icontains=q) |
        Q(author__username__icontains=q)
    ), 5)                           # This will show 5 posts per page, 
                                                                   # but needs to be updated at a later stage.
    
    
    # Next we get the page GET parameter that indicates the current page number
    page_number = request.GET.get('page')               # page_number is the request
    page_obj = p.get_page(page_number)
    
    categorys = Category.objects.all()[0:5]
    post_count = posts.count()
    post_comments = Comment.objects.filter(
        Q(post__category__name__icontains=q))[0:3]
    
    context = {'categorys': categorys, 'posts':posts,'post_count':post_count, 'post_comments':post_comments, 'page_obj': page_obj }
    return render(request, 'blog/home.html', context)



def categoriesPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    categorys = Category.objects.filter(name__icontains=q)
    return render(request, 'blog/categories.html', {'categorys': categorys})


def activityPage(request):
    post_comments = Comment.objects.all()
    return render(request, 'blog/activity.html', {'post_comments': post_comments})




def post(request, pk):
    page = 'detail'             # We using this variable because we dont want the profile to show 
                                # on the home page, but only on the post detail view.
    post = Post.objects.get(id=pk)
    categorys = Category.objects.all()
    form = CommentForm()
    new_comment = None
        
    # Lets query child objects of a certain parent (in this case post), 
    # that is all comments related to any post. We do that by using 
    # the post.comment_set.all() method.
    comments = post.comment_set.all()
    
    # We also want to have a list of all users who participate in commenting on various 
    # posts. We call them participants:
    participants = post.participants.all()
    
    # We want to send the comment to the database (that is save it)
    if request.method == 'POST':
        # Here we are using the create method, but we can just make use
        # of the ModelForm, which takes care of everything
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            # Add the commentor (participant) to the list of participants:
            post.participants.add(request.user)
            return redirect('post_view', pk=post.id)
            
        #comment = Comment.objects.create(
            #body = request.POST.get('body'),   # we get the body from the typed in comment by the user, under name='body'
            #post = post,           # current post, as defined above
            #user = request.user    # currently logged in user
        #)
        # After saving the comment, we want to send the user to the same post page:
        #return redirect('post_view', pk=post.id)
    
    context = {'participants':participants, 'post': post, 'comments': comments, 'categorys': categorys, 'form':form, 'new_comment':new_comment, 'page':page}
    return render(request, 'blog/post_view.html', context)





@login_required(login_url='login')
def createPost(request):
    page = 'create'
    form = PostForm()
    
    if request.method == 'POST':
        # print(request.POST) -- this sends the request data to the backend
        # request.POST.get('name') -- processing manually, but its not necessary 
        # since we have a ModelForm that handles all that logic as follows:
        form = PostForm(request.POST, request.FILES) # passing all the post data into the form
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
        
        
    context = {'form': form, 'page':page}
    return render(request, 'blog/post_form.html', context)



@login_required(login_url='login')
def updatePost(request, pk):
    post = Post.objects.get(id=pk)
    form = PostForm(instance=post) # the form will be pre-filled with the Post we want to edit
    
    if request.user != post.author:
        return HttpResponse('You are not allowed to be here!!')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')
    
    context = {'form': form}
    return render(request, 'blog/post_form.html', context)   # we use the same template as the one for the 
                                                             # createPost method



@login_required(login_url='login')
def deletePost(request, pk):
    post = Post.objects.get(id=pk)
    
    if request.method == 'POST':
        post.delete()
        return redirect('home')    
    
    return render(request, 'blog/delete.html', {'obj': post}) # The post will be called 'obj' in the template



@login_required(login_url='login')
def deleteComment(request, pk):
    comment = Comment.objects.get(id=pk)

    if request.user != comment.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        comment.delete()
        return redirect('home')
    return render(request, 'blog/delete.html', {'obj': comment})



def contactUs(request):
    form = ContactUsForm
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            print('Form is valid')
    
    context = {'form': form}
    return render(request, 'blog/contact.html', context)



def send_email(request):
    # send email from a contact form
        
    if request.method =='POST':
        form = SendEmailForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
            email = data['email']
            name = data['name']
            message = data['body']
            # send the email to the specified address
            print(request.POST)
            send_mail('Subject', 'Message', 'sender_email', ['brilliant.chikanya@gmail.com', 'mchawadya552@gmail.com'])
            return redirect('home')
        
    else:
        form = SendEmailForm()
    
    
    context = {'form':form}
    return render(request, 'blog/send_email.html', context)

def func(request):
    pass


