from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('messages/', views.topics, name='private_messages'),
    path('messages/read/<int:topic_id>/', views.topic_read, name='private_messages_topic'),
    path('messages/new/', views.topic_new, name='private_messages_new'),
    path('messages/delete/', views.topic_delete, name='private_messages_topic_delete'),
    
]
