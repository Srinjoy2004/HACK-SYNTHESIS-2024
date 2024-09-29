from django.urls import path
from . import views  # Ensure views.py is in the same directory

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('videocall/', views.videocall, name='videocall'),
    path('join_room/', views.join_room, name='join_room'),
    path('logout/', views.logout_view, name='logout'),
    path('process_frame/', views.process_frame, name='process_frame'),  # New route for processing frames
]
