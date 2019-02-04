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
    path('work/<int:typing>/<int:lesson>/<int:classroom_id>/', views.work_list),
    path('work/submit/<int:typing>/<int:lesson>/<int:index>/', views.submit),
    path('work/content/edit/<int:types>/<int:typing>/<int:lesson>/<int:index>/<int:question_id>/<int:content_id>/', views.content_edit),
    path('work/content/delete/<int:types>/<int:typing>/<int:lesson>/<int:index>/<int:question_id>/<int:content_id>/', views.content_delete),
    path('work/content1/history/<int:typing>/<int:lesson>/<int:index>/<int:question_id>/', views.content1_history),
]