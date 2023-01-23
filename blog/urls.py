from django.urls import path

from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginPage, name='login'),
    path('logout', views.logoutUser, name='logout'),
    path('register/', views.registerUser, name='register'),
    path('profile/<str:pk>/', views.userProfile, name='user_profile'),
    path('edit_profile', views.editProfile, name='edit_profile'),
    path('send_email', views.send_email, name='send_email'),
    path('categories/', views.categoriesPage, name='categories'),
    path('activity/', views.activityPage, name='activity'),
    path('create_post/', views.createPost, name='create_post'),
    path('update_post/<str:pk>/', views.updatePost, name='update_post'),
    path('delete_post/<str:pk>/', views.deletePost, name='delete_post'),
    path('delete_comment/<str:pk>/', views.deleteComment, name='delete_comment'),
    path('post/<str:pk>/', views.post, name='post_view'),
    path('contact/', views.contactUs, name='contact'),
]

