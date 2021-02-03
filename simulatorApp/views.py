import simulatorApp
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone 
from django.views import View
from .models import AcknowledgedEvent, Strategy, YES, School, Team, PolicyStrategy, Price, Simulator, MarketEvent, PopupEvent, MarketAttributeType
from .globals import MARKET_ATTRIBUTE_TYPES


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
        return render(request, 'index.html', context=context_dict)

    def post(self,request):
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
        return redirect(reverse('simulatorApp:login'))

    def post(self, request):

        if not request.user.is_authenticated:
            return redirect(reverse('simulatorApp:login'))

        logout(request)
        # Take the user back to the homepage.
        return redirect(reverse('simulatorApp:login'))

class Login(View):

    
    def get(self,request):

        if request.user.is_authenticated:
            return redirect(reverse('simulatorApp:index'))

        return render(request=request,
                        template_name="accounts/login.html",
                    )
    
    def post(self, request):

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
            
            
            user=authenticate(username=request.POST.get("username","").strip(), password=request.POST.get("password","").strip())
            if user is not None:
                login(request, user)
                # messages.info(request, f"You are now logged in as {username}")
                return redirect(reverse('simulatorApp:index'))
            else:
                print("User login failed")
                return redirect(reverse('simulatorApp:login'))
                # messages.error(request, "Invalid username or password.")
        else:
            return redirect(reverse('simulatorApp:login'))
            # messages.error(request, "Invalid username or password.")
        
        return self.get(request)

class YesProfile(View):

    
    def get(self, request, **kwargs):
        
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
        if(not request.user.is_authenticated):
            return redirect(reverse('simulatorApp:login'))
        
        # check user has the correct view permission
        if(not request.user.has_perm("simulatorApp.is_yes_staff")):
            print("User does not have permission")
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

        
        return self.get(request, notify=notify)

class SchoolProfile(View):

    def get(self, request, **kwargs):

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
            
        return self.get(request, notify=notify)
        
class TeamProfile(View):
     
     def get(self, request, **kwargs):
        
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

        return render(request, 'accounts/team_profile.html', context=context_dict)

     def post(self, request):
        
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
            
        return self.get(request, notify=notify)

class ViewTeams(View):

    def get(self, request, **kwargs):
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

        return render(request, 'viewTeams.html', context=context_dict)

    
    def post(self, request):
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
        return self.get(request, notify=notify)
    
class ViewSchools(View):

    def get(self, request, **kwargs):
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
        return render(request, 'viewSchools.html', context=context_dict)

    def post(self, request, **kwargs):
        notify = {}

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
                print(e)
                # school object has already been deleted
                resp['class'] = 'error'
                resp['msg'] = "School has already been deleted"
                resp['title'] = 'Uh oh'
            return JsonResponse(resp)

        return self.get(request, notify=notify)

class ViewLeaderboard(View):
    def get(self, request, **kwargs):
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
        return render(request, 'viewLeaderboard.html', context=context_dict)        
        
class EditStrategy(View):
    
    def get(self, request, **kwargs):
        context_dict = {}
 
        # check user is logged in
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
        except Exception as e:
            # No profile exists for this id return to index
            
            return redirect(reverse('simulatorApp:index'))

        # Pass on any notification message to sweetalert plugin
        if"notify" in kwargs:
            context_dict['notify'] = kwargs['notify']

        policies = PolicyStrategy.objects.filter(strategy=user_profile.strategyid)
        price = Price.objects.get(team=user_profile)
        maxPrice = float(price.simulator.maxPrice)-0.01

        context_dict['maxPrice']=maxPrice
        context_dict['price'] = price
        context_dict['policies'] = policies
        context_dict['user_profile'] = user_profile
        context_dict['can_edit'] = True
        return render(request, 'editStrategy.html', context=context_dict)

    def post(self, request, **kwargs):
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
            
        return self.get(request, notify=notify)
 