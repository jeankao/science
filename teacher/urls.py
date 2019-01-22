from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from . import views

urlpatterns = [
    path('classroom/', views.ClassroomList.as_view()),
    path('classroom/create/', views.ClassroomCreate.as_view()),    
    path('classroom/<int:pk>/update/', views.ClassroomUpdate.as_view()),  
    path('classroom/assistant/<int:classroom_id>/', views.classroom_assistant),
    path('classroom/assistant/add/<int:classroom_id>/', views.AssistantListView.as_view()),    
    #公告
    path('announce/<int:classroom_id>/', views.AnnounceListView.as_view()),
    path('announce/add/<int:classroom_id>/', views.AnnounceCreateView.as_view()),
    path('announce/detail/<int:message_id>/', views.announce_detail),    
    #設定助教
    path('assistant/', views.AssistantClassroomListView.as_view()),
    path('assistant/make/', views.assistant_make),    
]