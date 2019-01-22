from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name="dashboard.html")),
    path('login/', views.Login.as_view()),
    path('logout/', views.Logout.as_view()),  
    path('user/', views.UserList.as_view()),
    path('user/create/', views.UserCreate.as_view()),    
    path('user/<int:pk>', views.UserDetail.as_view()),
    path('user/<int:pk>/update/', views.UserUpdate.as_view()), 
    path('user/<int:pk>/password/', views.UserPasswordUpdate.as_view()), 
    path('user/<int:pk>/teacher/', views.UserTeacher.as_view()),     
    path('dashboard/',  views.LineList.as_view()),   
    path('line/classmate/<int:classroom_id>/', views.LineClassmateList.as_view()),      
    path('line/<int:user_id>/<int:classroom_id>/create/', views.LineCreate.as_view()), 
    path('line/<int:pk>/', views.LineDetail.as_view()),    
    path('line/download/<int:file_id>/', views.line_download), 
    path('line/showpic/<int:file_id>/', views.line_showpic),     
    #設定教師
    path('teacher/make/', views.make),         
]