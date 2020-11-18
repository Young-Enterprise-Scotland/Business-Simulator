from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.

class YES(models.Model):
    
    # password is managed by the User model

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.TextField(max_length=25)

    class Meta:
        
        # Permissions can be accessed like so
        # user.has_perm('simulatorApp.is_yes_staff')
        permissions = (
                       ("is_yes_staff", "Is a yes member of staff"),
                      )
    
      
class School(models.Model):

    # password is managed by the User model

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # school names can be quite long
    team_name = models.TextField(max_length=256)

    class Meta:
        
        # Permissions can be accessed like so
        # user.has_perm('simulatorApp.is_school')
        permissions = (
                       ("is_school", "Is a school account"),
                      )


"""
    Strategy model must go before the Team model otherwise
        migrations will read Team profile and look for the 
        Strategy table which has not yet been defined!
    Migrations will crash!
"""
class Strategy(models.Model):

    # create skeleton model for now
    # to aid with user model implementation
    # this number is of the format xxx.xxxx
    # to change accuracy increase decimal places,
    # Note: max_digits must always be larger than
    #       decimal_places!
    consistency = models.DecimalField(decimal_places=4, max_digits=7)
    
    


class Team(models.Model):

    # password is managed by the User model

    user                    = models.OneToOneField(User, on_delete=models.CASCADE)

    schoolid                = models.ForeignKey(School, on_delete=models.CASCADE)
    strategyid              = models.OneToOneField(Strategy, on_delete=models.CASCADE)
    
    # setup all new leaderboard positions to be -1. 
    # This way we can easily check if their position 
    # has been calculated for the first time
    leaderboard_position    = models.IntegerField(default=-1)
    school_position = models.IntegerField(default=-1)
    
    class Meta:
        
        # Permissions can be accessed like so
        # user.has_perm('simulatorApp.is_team')
        permissions = (
                       ("is_team", "Is a team account"),
                      )

class Simulator(models.Model):
    ID = models.AutoField(primary_key = True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    lengthOfTradingDay = models.DurationField(default='01:00:00')
    productName = models.CharField(max_length=100)
    image = models.ImageField(blank = True)
    maxPrice = models.DecimalField(max_digits=10, decimal_places = 2)
    minPrice = models.DecimalField(max_digits=10, decimal_places = 2)
    marketOpen = models.BooleanField()

    def clean(self):
        # Start date cannot be after end date
        # Length of trading day must be less than the duration between start and end
        if (self.end is None or self.start is None):
            raise ValidationError("start and end must have values")
        if (self.end <= self.start):
            raise ValidationError("Overlapping dates")
        if (self.start + self.lengthOfTradingDay > self.end):
            raise ValidationError("Length of Trading Day is too short for given start and end dates")
        if (self.minPrice > self.maxPrice):
            raise ValidationError("Minimum price cannot be larger than maximum price")
    
