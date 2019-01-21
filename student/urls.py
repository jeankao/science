from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from . import views

urlpatterns = [
    path('classroom/', views.ClassroomList.as_view()),
    path('classroom/join/', views.ClassroomJoinList.as_view()),    
    path('classroom/<int:pk>/enroll/', views.ClassroomEnrollCreate.as_view()), 
    path('classroom/<int:pk>/classmate/', views.ClassmateList.as_view()),    
    path('classroom/<int:pk>/seat/', views.ClassroomSeatUpdate.as_view()),   
]