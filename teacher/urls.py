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
    # 作業
    path('work/<int:lesson>/<int:classroom_id>/', views.WorkList.as_view()),
    path('work/add/<int:lesson>/<int:classroom_id>/', views.WorkCreate.as_view()),
    path('work/update/<int:pk>/<int:lesson>/<int:classroom_id>/', views.WorkUpdate.as_view()),    
    #path('work/question/<int:work_id>/<int:lesson>/<int:classroom_id>/', views.Science1QuestionList.as_view()),	
    path('work/question/answer/<int:lesson>/<int:classroom_id>/<int:work_id>/<int:q_id>/', views.Science1QuestionAnswer.as_view()),	
    path('work/question/add/<int:lesson>/<int:classroom_id>/<int:work_id>/', views.Science1QuestionCreate.as_view()),
    path('work/question/update/<int:pk>/<int:lesson>/<int:classroom_id>/<int:work_id>/', views.Science1QuestionUpdate.as_view()),    
    path('work/score/<int:lesson>/<int:classroom_id>/<int:index>', views.WorkScoreList.as_view()),    
    # 記錄
    path('log/<int:classroom_id>/', views.LogList.as_view()),    
]