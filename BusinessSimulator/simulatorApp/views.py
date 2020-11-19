from django.shortcuts import render
from django.views import View
# Create your views here.


class Index(View):

    '''
        Djanjo allows for views to be done as classes instead of methods
        for complex views this has the advantage that the get and post
        handlers are separated allowing for more readable code.
    '''

    def get(self,request):
        return render(request, 'index.html')

    def post(self,request):
        pass

class Logout(View):

    def get(self,request):
        pass

    def post(self, request):
        pass
