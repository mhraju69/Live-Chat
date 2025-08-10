"""
URL configuration for LiveChat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path,re_path
from User.views import *
from django.conf import settings
from django.conf.urls.static import static as static_urls
from Chat.views import *



urlpatterns = [
    path('admin/', admin.site.urls),
    path('',user_login, name='login'),
    path('logout/', logout_view, name='logout'),
    path("signup/", signup, name="signup"),
    path("chat/", ChatView, name="chat"),
    path("chat/<int:room_id>/", ChatView, name="chat-room"),
    path('chat/create-room/<int:user_id>/', create_chat_room, name='create-chat-room'),
    path("chat/search/", SearchView, name="search"),
    path('update-profile/', Update_Profile, name='profile_update'),


]

if settings.DEBUG:
    urlpatterns += static_urls(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

