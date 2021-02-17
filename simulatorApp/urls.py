from simulatorApp import views
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView


 # app_name is refered to in templates and views
 # example usage: href='{% url 'simulatorApp:index' %}' 
 #
app_name = 'simulatorApp'


urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('login', views.Login.as_view(), name='login'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('yesProfile',views.YesProfile.as_view(),name='viewYesAccount'),
    path('schoolProfile',views.SchoolProfile.as_view(),name='viewSchoolAccount'),
    path('teamProfile',views.TeamProfile.as_view(), name="viewTeamAccount"),
    path('viewTeams', views.ViewTeams.as_view(), name="viewTeams"),
    path('viewSchools', views.ViewSchools.as_view(), name="viewSchools"),
    path('editStrategy', views.EditStrategy.as_view(), name="editStrategy"),
    path('gameSettings', views.GameSettings.as_view(), name="gameSettings"),
    path('viewLeaderboard', views.ViewLeaderboard.as_view(), name="viewLeaderboard"),
    path('viewMarketEvents', views.viewMarketEvents.as_view(), name="viewMarketEvents"),
    path('editMarketEvent', views.editMarketEvent.as_view(), name="editMarketEvent"),
    path('editPolictEvent', views.editPolicyEvent.as_view(), name="editPolicyEvent"),
    path('viewPolicies', views.ViewPolicies.as_view(), name="viewPolicies"),
]
