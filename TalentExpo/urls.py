"""
URL configuration for TalentExpo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

from social_app.views import  HomePage, add_location, add_talent, candidate_dashboard,chatbot_response, check_email, delete_candidate, delete_director, direc_profile, director_dashboard, director_post, forgot_password, get_directors, get_profile, logout, new_post,register_candidate, register_director,search_candidates, search_directors, send_schedule, show_candidates, show_posts, user_login,logout, view_candidates_and_directors

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePage, name='home'),
    path('register/candidate', register_candidate, name='register_candidate'),
    path('register/director/', register_director, name='register_director'),
    path('login/', user_login, name='user_login'),
    path('logout/', logout, name='logout'),
    path('check_email/', check_email, name='check_email'),
    path('view_candidates_and_directors/', view_candidates_and_directors, name='view_candidates_and_directors'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('add-talent/', add_talent, name='add_talent'),
    path('add-location/', add_location, name='add_location'),
    path('candidate_dashboard/', candidate_dashboard, name='candidate_dashboard'),
    path('candidate_dashboard/new_post/', new_post, name='new_post'), 
    path('director_dashboard/', director_dashboard, name='director_dashboard'),
    path('show_candidates/', show_candidates, name='show_candidates'),
    path('show_posts/', show_posts, name='show_posts'),
    path('search_candidates', search_candidates, name='search_candidates'),
    path('director_dashboard/director_post/', director_post, name='director_post'),
    path('send_schedule/', send_schedule, name='send_schedule'),
    path('get_directors/', get_directors, name='get_directors'),
    path('search-directors/', search_directors, name='search_directors'),
    path('get_profile/', get_profile, name='get_profile'),
    
    path('chatbot/', chatbot_response, name='chatbot_response'),
    path('direc_profile', direc_profile, name='direc_profile'),
    path('delete_candidate', delete_candidate, name='delete_candidate'),
    path('delete_director', delete_director, name='delete_director'),
    
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
