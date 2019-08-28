from . import views
from django.urls import path
from rest_framework_swagger.views import get_swagger_view
from Chatapp.accounts.views import (login, signup, forget, delete)
schema_view = get_swagger_view(title='Django API Docs')

urlpatterns = [
    path('api_docs', schema_view),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('activate/<token>/', views.activate, name='activate'),
    path('delete', views.delete, name='delete'),
    path('forget', views.forget, name='forget'),
    path('reset/<token>/', views.reset, name='reset'),
]
