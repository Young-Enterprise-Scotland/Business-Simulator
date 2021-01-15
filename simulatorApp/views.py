from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django.urls import reverse 
from django.views import View
from .models import Strategy, YES, School, Team


# Create your views here.


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

        if request.user.has_perm('simulatorApp.is_school'):
            context_dict['school_obj'] = School.objects.get(user=request.user)
        elif request.user.has_perm('simulatorApp.is_team'):
            context_dict['team_obj'] = Team.objects.get(user=request.user)

        return render(request, 'index.html', context=context_dict)

    def post(self,request):
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
        if request.POST.get('add_team'):
            
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
        return self.get(request)