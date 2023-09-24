from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name= 'home'),
    path('register/', views.register_team, name = 'register'),
    path('match_schedule/', views.generate_schedule, name='match_schedule'),
    path('team_information/', views.team_information, name='team_information'),
    path('admin/', admin.site.urls),
    path('update_goals/', views.update_goals, name='update_goals')
]