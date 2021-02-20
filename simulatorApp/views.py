from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone 
from django.utils.dateparse import parse_duration, parse_datetime
from django.utils.timezone import make_aware
from django.db import connections
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from .models import AcknowledgedEvent, Strategy, YES, School, Team, PolicyStrategy, Price, Simulator, MarketEvent, PopupEvent, MarketAttributeType, PolicyEvent, Policy
from .globals import MARKET_ATTRIBUTE_TYPES, secondsToDHMS

# Create your views here.

def get_popups(request):
    'gets the most recent popup notifications for a team'

    if not request.user.is_authenticated:
        return []
    if not request.user.has_perm('simulatorApp.is_team'):
        return []

    return  PopupEvent.objects.filter(
        simulator=Simulator.objects.all()[0]
        ).exclude(
            id__in=[
                x.event.id for x in AcknowledgedEvent.objects.filter(
                    team=Team.objects.get(user=request.user)
                    )
                ]
        )

def get_popup(request):
    'get one popup to display'
    popups = get_popups(request)
    return popups[0] if len(popups)>0 else popups


class Index(View):

    '''
        Djanjo allows for views to be done as classes instead of methods
        for complex views this has the advantage that the get and post
        handlers are separated allowing for more readable code.
    '''

    def get(self,request):

        # attempt to close stale connections
       #connections.close_all()

        context_dict = {}
        # check user is logged in
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        if request.user.is_superuser:
            return redirect(reverse('simulatorApp:logout'))
        if request.user.has_perm('simulatorApp.is_school'):
            context_dict['school_obj'] = School.objects.get(user=request.user)
        elif request.user.has_perm('simulatorApp.is_team'):
            context_dict['team_obj'] = Team.objects.get(user=request.user)
            # MARKET_ATTRIBUTE_TYPES defines the attribute being displayed in graph.
            #get net profit data
            context_dict['attribute_data'] = context_dict['team_obj'].get_team_attribute(MARKET_ATTRIBUTE_TYPES[6])
            context_dict['graph_title'] = MARKET_ATTRIBUTE_TYPES[6]
            context_dict['average_net_profit'] = MarketAttributeType.objects.get(label = MARKET_ATTRIBUTE_TYPES[6]).get_average_value()
            #get market share data
            team_share = context_dict['team_obj'].get_team_attribute(MARKET_ATTRIBUTE_TYPES[8])
            if len(team_share) > 0:
                context_dict['team_market_share'] = team_share[len(team_share)-1].parameterValue
            else:
                context_dict['team_market_share'] = 0
            context_dict['other_market_share'] = 100 - context_dict['team_market_share']
            #get sales data 
            context_dict['attribute_data_small'] = context_dict['team_obj'].get_team_attribute(MARKET_ATTRIBUTE_TYPES[4])
            context_dict['graph_title_small'] = MARKET_ATTRIBUTE_TYPES[4]
            context_dict['average_sales'] = MarketAttributeType.objects.get(label = MARKET_ATTRIBUTE_TYPES[4]).get_average_value()


        # display market events as 'news articles'
        context_dict['news_articles'] = MarketEvent.objects.filter(valid_from__lte=timezone.now()).order_by("-id")
        
        # load any fullscreen notifications for the user
        context_dict['fullscreen_popup'] = get_popup(request)

        sims = Simulator.objects.all()
        if len(sims)>0:
            context_dict['refresh_rate'] = sims[0].lengthOfTradingDay.total_seconds() * 1000
        else:
            context_dict['refresh_rate'] = 60000*5

        return render(request, 'index.html', context=context_dict)

    def post(self,request):
       #connections.close_all()
        team=None
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))

        if request.user.has_perm('simulatorApp.is_school'):
            return self.get(request)
        if request.user.has_perm('sumilator.is_yes_staff'):
            return self.get(request)
        
        elif request.user.has_perm('simulatorApp.is_team'):
            team = Team.objects.get(user=request.user)
        if(request.POST.get('mark_popup_as_read', False)=='true'):
            AcknowledgedEvent.objects.get_or_create(
                team=team,
                event= PopupEvent.objects.get(id=request.POST.get("popup_id",0)),
                has_acknowledged = True
            )
        return self.get(request)

class Logout(View):

    def get(self,request):

        if not request.user.is_authenticated:
            return redirect(reverse('simulatorApp:login'))

        logout(request)
        # Take the user back to the homepage.

        #attempt to close stale connections
       #connections.close_all()

        return redirect(reverse('simulatorApp:login'))

    def post(self, request):
        #attempt to close stale connections
       #connections.close_all()
        if not request.user.is_authenticated:
            return redirect(reverse('simulatorApp:login'))

        logout(request)
        # Take the user back to the homepage.

       #connections.close_all()
        return redirect(reverse('simulatorApp:login'))

class Login(View):

    
    def get(self,request, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('simulatorApp:index'))

        # Pass on any notification message to sweetalert plugin
        if "notify" in kwargs:
            context_dict['notify'] = kwargs['notify']

        return render(request=request,
                        template_name="accounts/login.html",
                    )
    
    def post(self, request):

        notify = {}
        # Hi sid, LoginForm is not defined yet
        # so I have used old fashoned html way
        # until you get your crispy forms working
        # I have commented out your prevous code 
        # for now

        if request.user.is_authenticated:
            return redirect(reverse('simulatorApp:index'))

        #form = LoginForm(request=request, data=request.POST)
        
        #if form.is_valid():
        if True:

            #username=form.cleaned_data.get('username')
            #password=form.cleaned_data.get('password')
            
            
            user=authenticate(username=request.POST.get("username","").strip().lower(), password=request.POST.get("password","").strip())
            if user is not None:
                login(request, user)
                # messages.info(request, f"You are now logged in as {username}")
                return redirect(reverse('simulatorApp:index'))
            else:
                notify['title'] = "Incorrect username or password"
                notify['type'] = 'warning'
                
                return redirect(reverse('simulatorApp:login'))
                # messages.error(request, "Invalid username or password.")
        else:
            return redirect(reverse('simulatorApp:login'))
            # messages.error(request, "Invalid username or password.")
        
        return self.get(request)

class YesProfile(View):

    
    def get(self, request, **kwargs):
       #connections.close_all()
        context_dict = {}
 
        # check user is logged in
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))

        # check user has the correct view permission
        if(not request.user.has_perm("simulatorApp.is_yes_staff")):
            return redirect(reverse('simulatorApp:index'))

        # retrieve the user account from the GET request
        profile_id = request.GET.get("profile_id",False)

        # check profile_id was passed in or return to index page
        if not profile_id:
            return redirect(reverse('simulatorApp:index'))

        try: # Try to retrieve the YES profile information
            user = User.objects.get(id=profile_id)
            user_profile = YES.objects.get(user=user)
        except Exception as e:
            # No profile exists for this id return to index
            
            return redirect(reverse('simulatorApp:index'))
        
        context_dict['user_profile'] = user_profile

        # Pass on any notification message to sweetalert plugin
        if"notify" in kwargs:
            context_dict['notify'] = kwargs['notify']

        return render(request, 'accounts/yes_profile.html', context=context_dict)


    def post(self, request):
       #connections.close_all()
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        
        # check user has the correct view permission
        if(not request.user.has_perm("simulatorApp.is_yes_staff")):
            return redirect(reverse('simulatorApp:index'))

        # retrieve the user account from the GET request
        profile_id = request.GET.get("profile_id",False)

        # check profile_id was passed in or return to index page
        if not profile_id:
            return redirect(reverse('simulatorApp:index'))
        
        try: # Try to retrieve the YES profile information
            user = User.objects.get(id=profile_id)
            user_profile = YES.objects.get(user=user)
        except Exception:
            # No profile exists for this id return to index
            return redirect(reverse('simulatorApp:index'))


        notify = {}
        # check user credentials before editing information
        if(request.POST.get("update_account_info",False)):
            
            # set username and update user and YES model
            user_profile.user.first_name = request.POST.get("first_name",user_profile.user.first_name).strip()
            user_profile.user.save()
            user_profile.save()

            notify['title'] = "Profile Updated"
            notify['type'] = 'success'

        elif request.POST.get("reset_password",False) and request.user == user_profile.user:
            notify['title'] = "Password Reset"
            notify['type'] = 'success'

            new_password = request.POST.get("new_password").strip()
            user_profile.user.set_password(new_password)
            user_profile.user.save()
            user_profile.save()
        
       #connections.close_all()
        return self.get(request, notify=notify)

class SchoolProfile(View):

    def get(self, request, **kwargs):
       #connections.close_all()
        context_dict = {}
 
        # check user is logged in
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))

        # check user has the correct view permission
        if(not (
            request.user.has_perm("simulatorApp.is_yes_staff")
            or 
            request.user.has_perm("simulatorApp.is_school")
            )
        ):
            return redirect(reverse('simulatorApp:index'))

        # retrieve the user account from the GET request
        profile_id = request.GET.get("profile_id",False)

        # check profile_id was passed in or return to index page
        if not profile_id:
            return redirect(reverse('simulatorApp:index'))

        try: # Try to retrieve the YES profile information
            user = User.objects.get(id=profile_id)
            user_profile = School.objects.get(user=user)
        except Exception as e:
            # No profile exists for this id return to index
            
            return redirect(reverse('simulatorApp:index'))

        # Pass on any notification message to sweetalert plugin
        if"notify" in kwargs:
            context_dict['notify'] = kwargs['notify']

        context_dict['user_profile'] = user_profile
        context_dict['can_edit'] = True
        return render(request, 'accounts/school_profile.html', context=context_dict)

    def post(self, request):
       #connections.close_all()
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        
        # check user has the correct view permission
        # either school or YES staff
        if(not (
            request.user.has_perm("simulatorApp.is_school")
            or
            request.user.has_perm("simulatorApp.is_yes_staff") 
            )
        ):
            return redirect(reverse('simulatorApp:index'))
        
         # retrieve the user account from the GET request
        profile_id = request.GET.get("profile_id",False)

        # check profile_id was passed in or return to index page
        if not profile_id:
            return redirect(reverse('simulatorApp:index'))
        
        try: # Try to retrieve the School profile information
            user = User.objects.get(id=profile_id)
            user_profile = School.objects.get(user=user)
        except Exception:
            # No profile exists for this id return to index
            return redirect(reverse('simulatorApp:index'))

        notify = {}
        # if user has requested to change school name
        if(request.POST.get("change_name")):
            new_name = request.POST.get("school_name", user_profile.school_name)
            user_profile.school_name = new_name.strip()
            user_profile.save()

            notify['title'] = "Profile Updated"
            notify['type'] = 'success'

        # if user has requested to reset password
        elif(request.POST.get("reset_password")):
            new_password = request.POST.get("new_password").strip()
            user_profile.user.set_password(new_password)
            user_profile.user.save()
            user_profile.save()

            notify['title'] = "Password Reset"
            notify['type'] = 'success'
        
       #connections.close_all()
        return self.get(request, notify=notify)
        
class TeamProfile(View):
     
     def get(self, request, **kwargs):
       #connections.close_all()
        context_dict = {}
 
        # check user is logged in
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))

        # Assign edit permissions based on users view permission
        if(not (
            request.user.has_perm("simulatorApp.is_yes_staff")
            or 
            request.user.has_perm("simulatorApp.is_school")
            )
        ):
            context_dict['can_edit'] = False
        else:
            context_dict['can_edit'] = True


        # retrieve the user account from the GET request
        profile_id = request.GET.get("profile_id",False)

        # check profile_id was passed in or return to index page
        if not profile_id:
            return redirect(reverse('simulatorApp:index'))

        try: # Try to retrieve the YES profile information
            user = User.objects.get(id=profile_id)
            user_profile = Team.objects.get(user=user)
        except Exception:
            # No profile exists for this id return to index
            return redirect(reverse('simulatorApp:index'))
        
        # Pass on any notification message to sweetalert plugin
        if"notify" in kwargs:
            context_dict['notify'] = kwargs['notify']
        context_dict['user_profile'] = user_profile

       #connections.close_all()
        return render(request, 'accounts/team_profile.html', context=context_dict)

     def post(self, request):
       #connections.close_all()
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))

        # post requests used to store user info in db
        # check user has the correct view permission
        # either school or YES staff
        if(not (
            request.user.has_perm("simulatorApp.is_school")
            or
            request.user.has_perm("simulatorApp.is_yes_staff") 
            )
        ):
            return redirect(reverse('simulatorApp:index'))

        profile_id = request.GET.get("profile_id",False)

        # check profile_id was passed in or return to index page
        if not profile_id:
            return redirect(reverse('simulatorApp:index'))
        
        try: # Try to retrieve the School profile information
            user = User.objects.get(id=profile_id)
            user_profile = Team.objects.get(user=user)
        except Exception:
            # No profile exists for this id return to index
            return redirect(reverse('simulatorApp:index'))

        notify = {}
        # if user has requested to change school name
        if(request.POST.get("update_account_info")):
            new_name = request.POST.get("first_name", user_profile.team_name)
            user_profile.team_name = new_name.strip()
            user_profile.save()

            notify['title'] = "Profile Updated"
            notify['type'] = 'success'

        # if user has requested to reset password
        elif(request.POST.get("reset_password")):
            new_password = request.POST.get("new_password").strip()
            user_profile.user.set_password(new_password)
            user_profile.user.save()
            user_profile.save()

            notify['title'] = "Password Reset"
            notify['type'] = 'success'
        
       #connections.close_all()
        return self.get(request, notify=notify)

class ViewTeams(View):

    def get(self, request, **kwargs):
       #connections.close_all()
        context_dict = {}
        teams = None
        schools = None
        
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        
        if request.user.has_perm("simulatorApp.is_team"):
            return redirect(reverse('simulatorApp:index'))
        
        if request.user.has_perm("simulatorApp.is_school"):
            teams = Team.get_teams_by_school(School.objects.get(user=request.user))
            schools = School.objects.filter(user=request.user)
            
        if request.user.has_perm("simulatorApp.is_yes_staff"):
            teams = Team.get_all_teams()
            schools = School.objects.all()

        # Pass on any notification message to sweetalert plugin
        if"notify" in kwargs:
            context_dict['notify'] = kwargs['notify']

        context_dict['teams'] = teams

        for i in range(len(teams)):
            if teams[i].school_position ==-1:
                teams[i].school_position = "Not Assigned"
            if teams[i].leaderboard_position == -1:
                teams[i].leaderboard_position = "Not Assigned"
        context_dict['schools'] = schools

       #connections.close_all()
        return render(request, 'viewTeams.html', context=context_dict)

    
    def post(self, request):
       #connections.close_all()
        notify = {}

        # check permissions
        if not request.user.is_authenticated:
            return redirect(reverse('simulatorApp:login'))
        if request.user.has_perm("simulatorApp.is_team"):
            return redirect(reverse('simulatorApp:index'))

        #check post request for add user
        if request.POST.get('add_team', False):
            
            #retrieve and add new team account
            username = request.POST.get('username')
            team_name = request.POST.get('team_name')
            schoolid = request.POST.get('school')

            try:
                # If a school is adding then force the schoolid for 
                # the team to be the authenticated school account 
                # submitting the request. This is an extra layer on 
                # top of the csrf token to stop schools from 
                # editing the schoolid and assigning users to different
                # schools. 
                if request.user.has_perm("simulatorApp.is_school"):
                    school = School.objects.get(user=request.user)
                else:
                    school = School.objects.get(id=schoolid)

            except Exception:
                notify['title'] = "School does not exist"
                notify['type'] = 'error'
                return self.get(request, notify=notify)

            password = request.POST.get('password')

            # create new user
            (user,created) = User.objects.get_or_create(
                username=username
            )
            
            if not created:
                notify['title'] = "Username already exists, no new account was created"
                notify['type'] = 'warning'
                return self.get(request,notify=notify)
            
            user.set_password(password)

            # create new team for user account

            (team, created)= Team.objects.get_or_create(
                user=user,
                schoolid = school,
                team_name = team_name
            )

            if not created:
                notify['title'] = "Team already exists, no new account was added"
                notify['type'] = 'warning'

                # delete user we just setup as 
                # no new team to assign to
                User.objects.get(id=user.id).delete()


                return self.get(request,notify=notify)
            
            notify['title'] = "Team successfully created"
            notify['type'] = 'success'

        elif request.POST.get('delete_team',False):
            # this is an ajax request so the response must be json
            resp = {}
            team_user_id = request.POST.get('team_id',None)

            if request.user.has_perm("simulatorApp.is_school"):
                # schools can only delete their own teams
                # check team belongs to school
                school = School.objects.get(user=request.user)
                if(school!= Team.objects.get(user=User.objects.get(id=team_user_id)).schoolid):
                    resp['class'] = 'error'
                    resp['msg'] = "You do not have permission to delete this team account. Try deleting one of your own teams!"
                    resp['title'] = 'Uh oh'
                    return JsonResponse(resp)
            if team_user_id is None:
                resp['class'] = 'error'
                resp['msg'] = "Team could not be deleted"
                resp['title'] = 'Uh oh'
            try:
                User.objects.get(id=team_user_id).delete()
                resp['class'] = 'success'
                resp['msg'] = "All associated data has also been deleted"
                resp['title'] = 'Team Deleted'
            except Exception as e:
                resp['class'] = 'error'
                resp['msg'] = "Team has already been deleted"
                resp['title'] = 'Uh oh'
            return JsonResponse(resp)
        
       #connections.close_all()
        return self.get(request, notify=notify)
    
class ViewSchools(View):

    def get(self, request, **kwargs):
       #connections.close_all()
        context_dict = {}
        schools = None

        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        
        if request.user.has_perm("simulatorApp.is_team") or request.user.has_perm("simulatorApp.is_school"):
            return redirect(reverse('simulatorApp:index'))
        
        if request.user.has_perm("simulatorApp.is_yes_staff"):
            schools = School.objects.all()

        # Pass on any notification message to sweetalert plugin
        if"notify" in kwargs:
            context_dict['notify'] = kwargs['notify']

        context_dict['schools'] = schools 
       #connections.close_all()
        return render(request, 'viewSchools.html', context=context_dict)

    def post(self, request, **kwargs):
        notify = {}
       #connections.close_all()
        # check permissions
        if not request.user.is_authenticated:
            return redirect(reverse('simulatorApp:login'))
        if request.user.has_perm("simulatorApp.is_team"):
            return redirect(reverse('simulatorApp:index'))
        if request.user.has_perm("simulatorApp.is_school"):
            return redirect(reverse("simulatorApp:index"))

        #check post request for add user
        if request.POST.get('add_school'):
            
            #retrieve and add new team account
            username = request.POST.get('username')
            school_name = request.POST.get('school_name')
            password = request.POST.get('password')

            # create new user
            (user,created) = User.objects.get_or_create(
                username=username
            )
            
            if not created:
                notify['title'] = "Username already exists, no new account was created"
                notify['type'] = 'warning'

               #connections.close_all()
                return self.get(request,notify=notify)
            
            user.set_password(password)

            # create new school for user account
            (team, created)= School.objects.get_or_create(
                user=user,
                school_name=school_name
            )
            if not created:
                notify['title'] = "School already exists, no new account was added"
                notify['type'] = 'warning'

                # delete user we just setup as 
                # no new team to assign to
                User.objects.get(id=user.id).delete()

               #connections.close_all()
                return self.get(request,notify=notify)
            
            notify['title'] = "School account successfully created"
            notify['type'] = 'success'

        elif request.POST.get('delete_school',False):
            # build a json response to deliver to the page
            # regarding the result of their action
            resp = {}

            schooluser_id = request.POST.get('account_id',None)
            if schooluser_id is None:
                # no school account for that id
                resp['class'] = 'error'
                resp['msg'] = "School could not be deleted"
                resp['title'] = 'Uh oh'
            try: 
                # attempt to delete school
                school_user = User.objects.get(id=schooluser_id)
                school = School.objects.get(user=school_user)
                
                teams = Team.objects.filter(schoolid=school) 
                for team in teams:
                    User.objects.get(id=team.user.id).delete() 
                school.delete()
                school_user.delete()

                resp['class'] = 'success'
                resp['msg'] = "All associated school accounts and their data has also been deleted"
                resp['title'] = 'School Deleted'
            except Exception as e:
                # school object has already been deleted
                resp['class'] = 'error'
                resp['msg'] = "School has already been deleted"
                resp['title'] = 'Uh oh'
            return JsonResponse(resp)

        return self.get(request, notify=notify)

class ViewLeaderboard(View):
    def get(self, request, **kwargs):
       #connections.close_all()
        context_dict = {}
        # check user is logged in
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        # check user has the correct view permission
        if(request.user.has_perm("simulatorApp.is_team")):
            this_team = Team.objects.get(user = request.user) 
            teams = Team.get_teams_by_school(School.objects.get(user=this_team.schoolid.user))
            context_dict['teams'] = teams.order_by('school_position')      
            
        if(request.user.has_perm("simulatorApp.is_school")):
            teams = Team.get_teams_by_school(School.objects.get(user = request.user))
            context_dict['teams'] = teams.order_by('school_position')
            
        if(request.user.has_perm("simulatorApp.is_yes_staff")):
            teams = Team.objects.all()
            if len(teams) < 10:
                context_dict['teams'] = teams.order_by('leaderboard_position')
            else:
                context_dict['teams'] = teams.order_by('leaderboard_position')[:10]
        
        context_dict['teams_global'] = Team.objects.all().order_by("leaderboard_position")
       #connections.close_all()
        return render(request, 'viewLeaderboard.html', context=context_dict)        
        
class EditStrategy(View):
    
    def get(self, request, **kwargs):
       #connections.close_all()
        context_dict = {}
 
        # check user is logged in
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))

        # check user has the correct view permission
        if(not (
            request.user.has_perm("simulatorApp.is_team")
            )
        ):
           #connections.close_all()
            return redirect(reverse('simulatorApp:index'))

        # retrieve the user account from the GET request
        profile_id = request.GET.get("profile_id",False)

        # check profile_id was passed in or return to index page
        if not profile_id:
           #connections.close_all()
            return redirect(reverse('simulatorApp:index'))

        try: # Try to retrieve the profile information
            user = User.objects.get(id=profile_id)
            user_profile = Team.objects.get(user=user)
        except Exception as e:
            # No profile exists for this id return to index
           #connections.close_all()
            return redirect(reverse('simulatorApp:index'))

        # Pass on any notification message to sweetalert plugin
        if"notify" in kwargs:
            context_dict['notify'] = kwargs['notify']

        policies = PolicyStrategy.objects.filter(strategy=user_profile.strategyid)
        price = Price.objects.get(team=user_profile)
        maxPrice = float(price.simulator.maxPrice)-0.01

        context_dict['maxPrice'] = maxPrice
        context_dict['price'] = price
        context_dict['policies'] = policies
        context_dict['user_profile'] = user_profile
        context_dict['can_edit'] = True

       #connections.close_all()
        return render(request, 'editStrategy.html', context=context_dict)

    def post(self, request, **kwargs):
       #connections.close_all()
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        
        # check user has the correct view permission
        if(not (
            request.user.has_perm("simulatorApp.is_team")
            )
        ):
            return redirect(reverse('simulatorApp:index'))
        
         # retrieve the user account from the GET request
        profile_id = request.GET.get("profile_id",False)

        # check profile_id was passed in or return to index page
        if not profile_id:
            return redirect(reverse('simulatorApp:index'))
        
        try: # Try to retrieve the profile information
            user = User.objects.get(id=profile_id)
            user_profile = Team.objects.get(user=user)
        except Exception:
            # No profile exists for this id return to index
            return redirect(reverse('simulatorApp:index'))

        notify = {}

        # retrieve all policy strategies linked to this team and the price of their product
        policies = PolicyStrategy.objects.filter(strategy=user_profile.strategyid)
        price = Price.objects.get(team=user_profile)
        
        # if user has requested to change strategy
        if(request.POST.get("change_strat")):
            # Update each policy
            for pol in policies:
                pol.chosen_option = request.POST.get(pol.policy.name + "_option").strip()
                pol.save()

            # Update the price
            price.price = float(request.POST.get("price").strip())
            price.save()

            notify['title'] = "Policy Updated"
            notify['type'] = 'success'
       #connections.close_all()
        return self.get(request, notify=notify)


class GameSettings(View):
    
    @staticmethod
    def format_timedelta(unit:int)->str:
        if int(unit)<10:
            return "0"+str(unit)
        return str(unit)

    def get(self, request, **kwargs):
       #connections.close_all()
        context_dict = {}
        
         # check user is logged in
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))

        # check user has the correct view permission
        if(not request.user.has_perm("simulatorApp.is_yes_staff")):
            return redirect(reverse('simulatorApp:index'))

        # Pass on any notification message to sweetalert plugin
        if"notify" in kwargs:
            context_dict['notify'] = kwargs['notify']
            
        sims = Simulator.objects.all()
        if len(sims) >0:
            context_dict['simulator']=sims
            context_dict['start'] = sims[0].start.strftime("%d-%m-%Y")
            context_dict['start_time'] = sims[0].start.strftime("%I:%M")

            context_dict['end'] = sims[0].end.strftime("%d-%m-%Y")
            context_dict['end_time'] = sims[0].end.strftime("%I:%M")
            
            # Show days and time (hours,minutes,seconds)
            length = sims[0].lengthOfTradingDay.total_seconds()
            (days, hours, minutes, seconds,) = secondsToDHMS(length)
            
            context_dict['days'] = days
            context_dict['time'] = f"{GameSettings.format_timedelta(hours)}:{GameSettings.format_timedelta(minutes)}:{GameSettings.format_timedelta(seconds)}"
            context_dict['productName'] = sims[0].productName
            context_dict['image'] = sims[0].image
            context_dict['maxPrice'] = sims[0].maxPrice
            context_dict['minPrice'] = sims[0].minPrice
            context_dict['priceBoundary1'] = sims[0].priceBoundary1
            context_dict['priceBoundary2'] = sims[0].priceBoundary2
            context_dict['startQuizUrl'] = sims[0].startQuizUrl
            context_dict['endQuizUrl'] = sims[0].endQuizUrl
            context_dict['marketOpen'] = sims[0].marketOpen
       #connections.close_all()
        return render(request, 'gameSettings.html', context=context_dict)
        
    
    
    def post(self, request, **kwargs):
       #connections.close_all()
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        
        # check user has the correct view permission
        if(not (
            request.user.has_perm("simulatorApp.is_yes_staff")
            )
        ):
            return redirect(reverse('simulatorApp:index'))

        notify = {}

        # if user requested to delete the simulation
        if (request.POST.get("delete_market")):
            simulators = Simulator.objects.all()
            if len(simulators)==0:
                notify['title'] = "No simulator to delete"
                notify['type'] = 'error'

               #connections.close_all()
                return self.get(request, notify=notify)
            else:
                simulators.delete()
                notify['title'] = "Simulator deleted"
                notify['type'] = 'success'
               #connections.close_all()
                return self.get(request, notify=notify)

         # if user has requested to add a simulation
        if(request.POST.get("add_market")):
            
            
            start = request.POST.get('start')
            start_time = request.POST.get('start_time')
            end = request.POST.get('end')
            end_time = request.POST.get("end_time")
            days = request.POST.get('days')
            time = request.POST.get('time')
            image = request.POST.get('image')
            productName = request.POST.get('productName')
            maxPrice = request.POST.get('maxPrice')
            minPrice = request.POST.get('minPrice')
            priceBoundary1 = request.POST.get('priceBoundary1')
            priceBoundary2 = request.POST.get('priceBoundary2')
            marketOpen = request.POST.get('marketOpen')
            startQuizUrl = request.POST.get('startQuizUrl')
            endQuizUrl = request.POST.get('endQuizUrl')
            if marketOpen == None:
                marketOpen = False
            
            # Convert strings into datetime objects
            start_dt = datetime.strptime(start+" "+start_time, '%d-%m-%Y %H:%M')
            end_dt = datetime.strptime(end+" "+end_time,'%d-%m-%Y %H:%M')
            start_t = make_aware(start_dt)
            end_t = make_aware(end_dt)
            s = str(days)
            ss = str(time)
            length = parse_duration(s+" "+ss)
            
            # Convet strings to decimal
            minPrice=Decimal(minPrice)
            maxPrice=Decimal(maxPrice)
            priceBoundary1=Decimal(priceBoundary1)
            priceBoundary2=Decimal(priceBoundary2)

            # Check values are in the correct ranges
            
            if minPrice > maxPrice:
                notify['title'] = "Minimum price has to be lower than the maximum price "
                notify['type'] = 'warning'
                return self.get(request, notify=notify)

            if (priceBoundary1 > priceBoundary2):
                notify['title'] ="Price boundary 1 has to be lower than price boundary 2"
                notify['type'] = 'warning'
                return self.get(request, notify=notify)
                
            if (minPrice > priceBoundary1) or (minPrice > priceBoundary2):
                notify['title'] ="Minimum price has to be lower than the price boundaries"
                notify['type'] = 'warning'
                return self.get(request, notify=notify)

            if (maxPrice < priceBoundary1) or (maxPrice < priceBoundary2):
                notify['title'] = "Price boundaries must to be smaller than maximum price"
                notify['type'] = 'warning'
                return self.get(request, notify=notify)
            
            if end_t < (start_t + length):
                notify['title'] = "Overlapping dates "
                notify['type'] = 'warning'

               #connections.close_all()
                return self.get(request, notify=notify)

            # create new Simulator
           
            sim = Simulator.objects.all()
            if len(sim) ==0:
                simulation = Simulator()
                simulation.start= start_t
                simulation.end=end_t
                simulation.lengthOfTradingDay=length
                simulation.productName=productName
                simulation.image = image
                simulation.maxPrice=maxPrice
                simulation.minPrice=minPrice
                simulation.priceBoundary1 = priceBoundary1
                simulation.priceBoundary2 = priceBoundary2
                simulation.marketOpen=marketOpen
                simulation.startQuizUrl = startQuizUrl
                simulation.endQuizUrl = endQuizUrl
                simulation.save()
                notify['title'] = "Simulator created"
                notify['type'] = 'success'

               #connections.close_all()
                return self.get(request, notify=notify)
            else:
                simulation = sim[0]
                simulation.start= start_t
                simulation.end=end_t
                simulation.lengthOfTradingDay=length
                simulation.productName=productName
                simulation.image = image
                simulation.maxPrice=maxPrice
                simulation.minPrice=minPrice
                simulation.priceBoundary1 = priceBoundary1
                simulation.priceBoundary2 = priceBoundary2
                simulation.marketOpen=marketOpen
                simulation.startQuizUrl = startQuizUrl
                simulation.endQuizUrl = endQuizUrl
                simulation.save()
                notify['title'] = "Simulator updated"
                notify['type'] = 'success'

       #connections.close_all()
        return self.get(request, notify=notify)
        
class viewMarketEvents(View):
    def get(self, request, **kwargs):
       #connections.close_all()

        # check user is logged in
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))

        # check user has the correct view permission
        if(not (
            request.user.has_perm("simulatorApp.is_yes_staff")
            )
        ):
            return redirect(reverse('simulatorApp:index'))

        context_dict = {}
        # Pass on any notification message to sweetalert plugin
        if "notify" in kwargs:
            context_dict['notify'] = kwargs['notify']


        # Retrieve all market event objects        
        context_dict["events"] = MarketEvent.objects.all()

       #connections.close_all()
        return render(request, 'viewMarketEvents.html', context=context_dict)

    def post(self, request, **kwargs):
       #connections.close_all()
        # check user is logged in
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        
        # check user has the correct view permission
        if(not (
            request.user.has_perm("simulatorApp.is_yes_staff")
            )
        ):
            return redirect(reverse('simulatorApp:index'))

        notify = {}

        # if user has requested to add an event
        if(request.POST.get("addEvent")):

            # Creates a market event object
            simulators = Simulator.objects.all()
            if(len(simulators)==0):
                notify['title'] = "No simulators exist"
                notify['type'] = 'error' 
                return self.get(request, notify=notify)

            MarketEvent.objects.create(
                simulator=simulators[0], 
                # add 1 day day to stop popup from being sent 
                # out before the event is properly configured
                valid_from=timezone.now()+timedelta(days=1)) 

            notify['title'] = "Event Added"
            notify['type'] = 'success'

        # if the user has requested to delete an event
        if(request.POST.get("delEvent")):

            # Retrieves the event and its policies
            event = MarketEvent.objects.get(id = int(request.POST.get('delevent')))
            policies = PolicyEvent.objects.filter(market_event = event)

            # Deletes all policies
            for pol in policies:
                pol.delete()

            # Deletes the event
            event.delete()

            notify['title'] = "Event Deleted"
            notify['type'] = 'success'            

       #connections.close_all()           
        return self.get(request, notify=notify)

class editMarketEvent(View):
    def get(self, request, **kwargs):
       #connections.close_all()

        context_dict = {}
        
        if(not (
            request.user.has_perm("simulatorApp.is_yes_staff")
            )
        ):
            return redirect(reverse('simulatorApp:index'))
            
        # check user has the correct view permission
        if(not (
            request.user.has_perm("simulatorApp.is_yes_staff")
            )
        ):
            return redirect(reverse('simulatorApp:index'))

        # retrieve the event from the GET request
        event_id = request.GET.get("event_id",False)

        # check event_id was passed in or return to index page
        if not event_id:
            return redirect(reverse('simulatorApp:index'))

        try: # Try to retrieve the event object
            event = MarketEvent.objects.get(id=event_id)
        except Exception as e:
            # No event exists for this id return to index
            return redirect(reverse('simulatorApp:index'))

        # Split date and time in order to display it on form
        datefrom, timefrom = str(event.valid_from).split(" ")
        dateto, timeto = str(event.valid_to).split(" ")

        context_dict['poltypes'] = Policy.objects.all()
        context_dict['policies'] = PolicyEvent.objects.filter(market_event=event)
        context_dict['simulators'] = Simulator.objects.all()    
        context_dict['eventObj'] = event
        context_dict['datefrom'] = datefrom
        context_dict['timefrom'] = timefrom[:5]
        context_dict['dateto'] = dateto
        context_dict['timeto'] = timeto[:5]
        context_dict['can_edit'] = True

       #connections.close_all()
        return render(request, 'editMarketEvent.html', context=context_dict)

    def post(self, request, **kwargs):
       #connections.close_all()

        # check user is logged in
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        
        # check user has the correct view permission
        if(not (
            request.user.has_perm("simulatorApp.is_yes_staff")
            )
        ):
            return redirect(reverse('simulatorApp:index'))

        notify = {}

        # if user has requested to edit event
        if(request.POST.get("editEvent")):
            # Retrieve the event object
            iden = request.GET.get("event_id").strip()
            event = MarketEvent.objects.get(id=int(iden))

            # Set simulator field
            event.simulator = Simulator.objects.get(id=int(request.POST.get("Simulator").strip()))

            # Read in the date and time
            fromdate = request.POST.get("fromdate").strip()
            fromtime = request.POST.get("fromtime").strip()

            # Convert date and time to datetime
            fromd = datetime.strptime(fromdate + " " + fromtime + ":00", '%Y-%m-%d %H:%M:%S')
            event.valid_from = fromd.replace(tzinfo=timezone.utc)
            
            todate = request.POST.get("todate").strip()
            totime = request.POST.get("totime").strip()

            tod = datetime.strptime(todate + " " + totime + ":00", '%Y-%m-%d %H:%M:%S')
            event.valid_to = tod.replace(tzinfo=timezone.utc)

            # Update the title and description
            event.market_event_title = request.POST.get("title").strip()
            event.market_event_text = request.POST.get("desc").strip()

            # If the dates given are valid then save
            if (event.valid_from < event.valid_to):
                event.save()
                notify['title'] = "Event Updated"
                notify['type'] = 'success'
            else:
                notify['title'] = "Time Invalid"
                notify['type'] = 'error'

        # If user has requested to add policy
        if(request.POST.get("addPolicy")):
            # Retrieve the market event and the policy this PolicyEvent redefines
            iden = request.GET.get("event_id").strip()
            event = MarketEvent.objects.get(id=int(iden))
            pol = Policy.objects.get(id = request.POST.get("poltype"))

            # If the policy does not already exist, create it
            if PolicyEvent.objects.filter(market_event=event, policy=pol).exists():
                notify['title'] = "Policy Already Exists"
                notify['type'] = 'error'
            else:
                PolicyEvent.objects.create(market_event=event, policy = pol)

                notify['title'] = "Event Policy Added"
                notify['type'] = 'success'

        # If user has requested to delete policy
        if(request.POST.get("delPolicy")):
            # Retrieve the policy and delete it
            policy = PolicyEvent.objects.get(id = int(request.POST.get('delpol')))
            policy.delete()
            notify['title'] = "Event Policy Deleted"
            notify['type'] = 'success'
        
       #connections.close_all()
        return self.get(request, notify=notify)

class editPolicyEvent(View):
    def get(self, request, **kwargs):
       #connections.close_all()

        context_dict = {}

        # check user is logged in
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))

        # check user has the correct view permission
        if(not (
            request.user.has_perm("simulatorApp.is_yes_staff")
            )
        ):
            return redirect(reverse('simulatorApp:index'))

        # retrieve the PolicyEvent from the GET request
        pol_id = request.GET.get("pol_id",False)

        # check pol_id was passed in or return to index page
        if not pol_id:
            return redirect(reverse('simulatorApp:index'))

        try: # Try to retrieve the PolicyEvent object
            policy = PolicyEvent.objects.get(id=pol_id)
        except Exception as e:
            # No profile object exists for this id return to index
            return redirect(reverse('simulatorApp:index'))

        # Pass on any notification message to sweetalert plugin
        if"notify" in kwargs:
            context_dict['notify'] = kwargs['notify']

        context_dict['polObj'] = policy
        context_dict['can_edit'] = True

       #connections.close_all()
        return render(request, 'editPolicyEvent.html', context=context_dict)

    def post(self, request, **kwargs):
       #connections.close_all()

        # check user is logged in
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        
        # check user has the correct view permission
        if(not (
            request.user.has_perm("simulatorApp.is_yes_staff")
            )
        ):
            return redirect(reverse('simulatorApp:index'))

        notify = {}

        # if user has requested to edit policy
        if(request.POST.get("editPolicy")):
            # Retrieve the PolicyEvent object
            iden = request.GET.get("pol_id").strip()
            policy = PolicyEvent.objects.get(id=int(iden))

            # Set the values and save
            policy.low_cost = float(request.POST.get('lowcost').strip())
            policy.low_customer = float(request.POST.get('lowcustomers').strip())
            policy.low_sales = float(request.POST.get('lowsales').strip())
            policy.med_cost = float(request.POST.get('medcost').strip())
            policy.med_customer = float(request.POST.get('medcustomers').strip())
            policy.med_sales = float(request.POST.get('medsales').strip())
            policy.high_cost = float(request.POST.get('highcost').strip())
            policy.high_customer = float(request.POST.get('highcustomers').strip())
            policy.high_sales = float(request.POST.get('highsales').strip())
                    

            policy.save()
            notify['title'] = "Event Updated"
            notify['type'] = 'success'
        
       #connections.close_all()
        return self.get(request, notify=notify)

class ViewPolicies(View):
    def get(self, request, **kwargs):
       #connections.close_all()

        context_dict = {}

        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        
        # check user has the correct view permission
        if( not request.user.has_perm("simulatorApp.is_yes_staff")):
            return redirect(reverse('simulatorApp:index'))

        # Pass on any notification message to sweetalert plugin
        if"notify" in kwargs:
            context_dict['notify'] = kwargs['notify']
        
        context_dict['policies'] = Policy.objects.all().order_by('-id')

       #connections.close_all()
        return render(request, 'viewPolicies.html', context=context_dict)

    def post(self, request):
       #connections.close_all()

        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        
        # check user has the correct view permission
        if( not request.user.has_perm("simulatorApp.is_yes_staff")):
            return redirect(reverse('simulatorApp:index'))

        notify = {}
        id = request.POST.get('policy_id')
        if not id:
            notify['type'] = "error"
            notify['title'] = "No policy provided" 
            return self.get(request, notify=notify)
        
        policies = Policy.objects.filter(id=id)
        if len(policies) != 1:
            notify['type'] = "error"
            notify['title'] = "Policy does not exist" 
            return self.get(request, notify=notify)
        policy = policies[0]

        policy.low_label =     request.POST.get("low_label",policy.low_label)
        policy.low_cost =      Decimal(request.POST.get("low_cost", policy.low_cost))
        policy.low_customer =  Decimal(request.POST.get("low_customer", policy.low_customer))
        policy.low_sales =     Decimal(request.POST.get("low_sales", policy.low_sales))

        policy.med_label =    request.POST.get("med_label",policy.med_label)
        policy.med_cost =     Decimal(request.POST.get("med_cost", policy.med_cost))
        policy.med_customer = Decimal(request.POST.get("med_customer", policy.med_customer))
        policy.med_sales =    Decimal(request.POST.get("med_sales", policy.med_sales))

        policy.high_label =     request.POST.get("high_label",policy.high_label)
        policy.high_cost =      Decimal(request.POST.get("high_cost", policy.high_cost))
        policy.high_customer =  Decimal(request.POST.get("high_customer", policy.high_customer))
        policy.high_sales =     Decimal(request.POST.get("high_sales", policy.high_sales))

        policy.save()
        notify['type'] = "success" 
        notify['title'] = policy.name+" updated"

       #connections.close_all()
        return self.get(request, notify=notify)
