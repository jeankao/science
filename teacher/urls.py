from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from . import views

urlpatterns = [
    path('classroom/', views.ClassroomList.as_view()),
    path('classroom/create/', views.ClassroomCreate.as_view()),    
    path('classroom/<int:pk>/update/', views.ClassroomUpdate.as_view()),  
    path('announce/<int:classroom_id>/create/', views.AnnounceCreate.as_view()),      
    #設定助教	
    path('assistant/', views.AssistantClassroomListView.as_view()),
    path('assistant/make/', views.assistant_make),    
]