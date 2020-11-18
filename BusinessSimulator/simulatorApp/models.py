from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from datetime import datetime


# Create your models here.

class Simulator(models.Model):
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



class YES(models.Model):
    
    # password is managed by the User model

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.TextField(max_length=25)

    class Meta:
        
        # Permissions can be accessed like so
        # <YESObject>.user.has_perm('simulatorApp.is_yes_staff')
        permissions = (
                       ("is_yes_staff", "Is a yes member of staff"),
                      )
    
    def save(self, *args, **kwargs):
        self.user.user_permissions.add(Permission.objects.get(codename="is_yes_staff"))
        super(YES, self).save(*args, **kwargs)
    
    def has_perm(self,permissionString):
        " checks the associated user model for the permission, returns True/False "
        return self.user.has_perm(permissionString)

class School(models.Model):

    # password is managed by the User model

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # school names can be quite long
    school_name = models.TextField(max_length=256)

    class Meta:
        
        # Permissions can be accessed like so
        # <SchoolObject>.user.has_perm('simulatorApp.is_school')
        permissions = (
                       ("is_school", "Is a school account"),
                      )
    def save(self, *args, **kwargs):
        self.user.user_permissions.add(Permission.objects.get(codename="is_school"))
        super(School, self).save(*args, **kwargs)

    def has_perm(self,permissionString):
        " checks the associated user model for the permission, returns True/False "
        return self.user.has_perm(permissionString)


"""
    Strategy model must go before the Team model otherwise
        migrations will read Team profile and look for the 
        Strategy table which has not yet been defined!
    Migrations will crash!
"""
class Strategy(models.Model):

    # create skeleton model for now
    # to aid with user model implementation
    # this number is of the format xxxxxxx.xxxx
    # to change accuracy increase decimal places,
    # Note: max_digits must always be larger than
    #       decimal_places!
    consistency = models.DecimalField(decimal_places=4, max_digits=12, default=0)
    # add relationship with policy once requirements are confirmed
    


class Team(models.Model):

    # password is managed by the User model

    user                    = models.OneToOneField(User, on_delete=models.CASCADE)

    schoolid                = models.ForeignKey(School, on_delete=models.CASCADE)
    strategyid              = models.OneToOneField(Strategy, on_delete=models.CASCADE)
    
    team_name = models.TextField(max_length=256)

    # setup all new leaderboard positions to be -1. 
    # This way we can easily check if their position 
    # has been calculated for the first time
    leaderboard_position    = models.IntegerField(default=-1)
    school_position = models.IntegerField(default=-1)
    
    class Meta:
        
        # Permissions can be accessed like so
        # <TeamObject>.user.has_perm('simulatorApp.is_team')
        permissions = (
                       ("is_team", "Is a team account"),
                      )
    def save(self, *args, **kwargs):
        'Override default save for Team model. If instanciating new object: create strategy instance, create market entry instance'


        self.user.user_permissions.add(Permission.objects.get(codename="is_team"))
    
        # create Strategy and MarketEntry for Team if not exists
        team = Team.objects.filter(team_name=self.team_name)
        if(len(team)==0):
            self.strategyid = Strategy.objects.create()
            MarketEntry.objects.create(strategyid=self.strategyid)
        
        # save instance
        super(Team, self).save(*args, **kwargs)

        
    
    def has_perm(self,permissionString):
        " checks the associated user model for the permission, returns True/False "
        return self.user.has_perm(permissionString)

class MarketEntry(models.Model):
    strategyid = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    #simulatorid = models.ForeignKey(<name of simulatormodel>, on_delete=models.CASCADE)


class MarketAttributeType(models.Model):
    label = models.CharField(max_length=32)

class MarketAttributeTypeData(models.Model):
    marketEntryId       = models.ForeignKey(MarketEntry, on_delete=models.CASCADE)
    marketAttributeType = models.ForeignKey(MarketAttributeType, on_delete=models.CASCADE)
    date                = models.DateTimeField(default=datetime.now)
    parameterValue      = models.DecimalField(decimal_places=4, max_digits=12)