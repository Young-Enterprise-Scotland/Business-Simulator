from django.shortcuts import render, redirect
from django.urls import reverse 
from django.views import View
from .models import YES, School, Team


# Create your views here.


class Index(View):

    '''
        Djanjo allows for views to be done as classes instead of methods
        for complex views this has the advantage that the get and post
        handlers are separated allowing for more readable code.
    '''

    def get(self,request):

        # check user is logged in
        # if(not request.user.is_authenticated):
        #     return redirect(reverse('simulatorApp:login'))

        return render(request, 'index.html')

    def post(self,request):
        pass

class Logout(View):

    def get(self,request):
        pass

    def post(self, request):
        pass

class Login(View):

    def get(self,request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        pass


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
            user_profile = YES.objects.get(id=profile_id)
        except Exception:
            # No profile exists for this id return to index
            return redirect(reverse('simulatorApp:index'))
        
        context_dict['user_profile'] = user_profile

        # if the post method has saved informatio
        # let the user know that their info has
        # been updated
        if"notify" in kwargs:
            context_dict['notify'] = kwargs['notify']

        return render(request, 'accounts/yes_profile.html', context=context_dict)



    def post(self, request):
        
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
            user_profile = YES.objects.get(id=profile_id)
        except Exception:
            # No profile exists for this id return to index
            return redirect(reverse('simulatorApp:index'))

        # check user credentials before editing information
        if(user_profile.user.check_password(request.POST.get("password").strip())):
            
            # set username and update user and YES model
            user_profile.user.first_name = request.POST.get("first_name",user_profile.user.first_name).strip()
            user_profile.user.save()
            user_profile.save()

            notify = "Profile updated."
        else:
            notify = "Password is incorrect."
        
        return self.get(request, notify=notify)

class SchoolProfile(View):

    def get(self, request):
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
            user_profile = School.objects.get(id=profile_id)
        except Exception:
            # No profile exists for this id return to index
            return redirect(reverse('simulatorApp:index'))
        
        context_dict['user_profile'] = user_profile
        context_dict['can_edit'] = True

        return render(request, 'school_profile.html', context=context_dict)

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

class TeamProfile(View):
     
     def get(self, request):
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
            user_profile = Team.objects.get(id=profile_id)
        except Exception:
            # No profile exists for this id return to index
            return redirect(reverse('simulatorApp:index'))
        
        context_dict['user_profile'] = user_profile
        context_dict['can_edit'] = True

        return render(request, 'team_profile.html', context=context_dict)

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