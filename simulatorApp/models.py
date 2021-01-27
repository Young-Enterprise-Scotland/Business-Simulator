from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler

from datetime import timedelta
from .globals import POLICIES, MARKET_ATTRIBUTE_TYPES


# Create your models here.

class Policy(models.Model):

    name = models.CharField(max_length=56, unique=True)

    low_label = models.CharField(max_length=56, default="Low")
    
    low_cost = models.DecimalField(decimal_places=4, max_digits=12, default=0.5)
    low_customer = models.DecimalField(decimal_places=4, max_digits=12, default=1)
    low_sales = models.DecimalField(decimal_places=4, max_digits=12, default=0.75)
    
    med_label = models.CharField(max_length=56, default="Medium")
    med_cost = models.DecimalField(decimal_places=4, max_digits=12, default=1.00)
    med_customer = models.DecimalField(decimal_places=4, max_digits=12, default=3)
    med_sales = models.DecimalField(decimal_places=4, max_digits=12, default=1.00)

    high_label = models.CharField(max_length=56, default="High")
    high_cost = models.DecimalField(decimal_places=4, max_digits=12,default=1.5)
    high_customer = models.DecimalField(decimal_places=4, max_digits=12, default=2)
    high_sales = models.DecimalField(decimal_places=4, max_digits=12, default=0.75)

    def __str__(self):
        return self.name

class Simulator(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    lengthOfTradingDay = models.DurationField(default=timedelta(days=1))
    productName = models.CharField(max_length=100)
    image = models.ImageField(blank = True)

    # price is of the format xxxxxxx.xxxx
    # allow for more than 2dp to help with roundoff errors
    maxPrice = models.DecimalField(max_digits=12, decimal_places = 4)
    minPrice = models.DecimalField(max_digits=12, decimal_places = 4)

    priceBoundary1 = models.DecimalField(max_digits=12, decimal_places = 4, default=1.50)
    priceBoundary2 = models.DecimalField(max_digits=12, decimal_places = 4, default=3.50)

    marketOpen = models.BooleanField(default=True)

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

        if (self.priceBoundary1 < self.minPrice) or (self.priceBoundary2 < self.minPrice):
            raise ValidationError("Price boundaries must be higher than the minimum price")
        if (self.priceBoundary1 > self.maxPrice) or (self.priceBoundary2 > self.maxPrice):
            raise ValidationError("Price boundaries must be lower than the maximum price")
    
    def __setup_policies(self):
        "Setup the policies for the game. These can be edited by YES staff"
        for policy in POLICIES:
            (object,created) = Policy.objects.get_or_create(name=policy)
    
    def __setup_market_attribute_types(self):
        for attribute_type in MARKET_ATTRIBUTE_TYPES:
            (object,created) = MarketAttributeType.objects.get_or_create(label=attribute_type)  

    def __setup_price_effects(self):
        
        for i in range(1,4):
            PriceEffects.objects.get_or_create(boundary=i)
        return
    def save(self, *args, **kwargs):
        
        # setup game related models
        self.__setup_policies()
        self.__setup_market_attribute_types()
        self.__setup_price_effects()

        super(Simulator, self).save(*args, **kwargs)
        
        from . import cronjobs
        cronjobs.start()
        
    def __str__(self):
        return self.productName+"("+str(self.id)+")"

class YES(models.Model):
    
    # password is managed by the User model

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        
        # Permissions can be accessed like so
        # <YESObject>.user.has_perm('simulatorApp.is_yes_staff')
        permissions = (
                       ("is_yes_staff", "Is a yes member of staff"),
                      )
    
    def save(self, *args, **kwargs):
        self.user.user_permissions.add(Permission.objects.get(codename="is_yes_staff"))
        self.user.save()
        super(YES, self).save(*args, **kwargs)
    
    def has_perm(self,permissionString):
        " checks the associated user model for the permission, returns True/False "
        return self.user.has_perm(permissionString)
    
    def __str__(self):
        return self.user.first_name

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
        self.user.save()
        super(School, self).save(*args, **kwargs)

    def has_perm(self,permissionString):
        " checks the associated user model for the permission, returns True/False "
        return self.user.has_perm(permissionString)

    def __str__(self):
        return self.school_name

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

    def __str__(self):
        try:
            return Team.objects.get(strategyid=self).team_name+" strategy"
        except Exception as e:
           
            return "uninstanciated strategy"

class Team(models.Model):

    # password is managed by the User model

    user                    = models.OneToOneField(User, on_delete=models.CASCADE)

    schoolid                = models.ForeignKey(School, on_delete=models.CASCADE)
    strategyid              = models.OneToOneField(Strategy, on_delete=models.CASCADE, blank=True)
    
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
        '''
            Override default save for Team model. 
            Sets up corresponding Strategy, MarketEntry
            and PolicyStrategy models if not already in
            existance. 
        '''

        self.user.user_permissions.add(Permission.objects.get(codename="is_team"))
        self.user.save()

        # create Strategy, MarketEntry and PolicyStrategy for Team if not exists
        team = Team.objects.filter(user=self.user)
       
        if(len(team)==0):
            #create strategy object for team
            
            self.strategyid = Strategy.objects.create()

            #setup market entry for team
            MarketEntry.objects.create(strategyid=self.strategyid)

            # create base PolicyStrategy objects for team
            for policy in POLICIES:
                PolicyStrategy.objects.create(
                    policy=Policy.objects.get(name=policy),
                    strategy=self.strategyid,
                    chosen_option=1 #set to be low by default
                    )  
        # save instance
        super().save(*args, **kwargs)

        if(len(team)==0):
            #create price object for team
            simulator  = Simulator.objects.annotate(models.Max('id'))[0]
            Price.objects.create(
                simulator=simulator,
                team=self,
                qual=PolicyStrategy.objects.get(strategy=self.strategyid, policy=Policy.objects.get(name="Quality of Raw Materials")),
                price=simulator.minPrice
                ) 
        
    def __str__(self):
        return self.team_name
    
    def has_perm(self,permissionString):
        "Checks the associated user model for the permission, returns True/False"
        return self.user.has_perm(permissionString)
    
    @staticmethod
    def get_teams_by_school(school_obj):
        return Team.objects.filter(schoolid=school_obj)

    @staticmethod
    def get_all_teams():
        return Team.objects.all()

class MarketEntry(models.Model):
    strategyid = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    simulator = models.ForeignKey(Simulator, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        qs = Simulator.objects.annotate(models.Max('id'))
        if len(qs)>=1:
            self.simulator = qs[0] 
        super(MarketEntry, self).save(*args, **kwargs)
    
    def __str__(self):
        return Team.objects.get(strategyid=self.strategyid).team_name+" Market Entry"

class MarketAttributeType(models.Model):
    label = models.CharField(max_length=32)

    def __str__(self):
        return self.label

class MarketAttributeTypeData(models.Model):
    marketEntryId       = models.ForeignKey(MarketEntry, on_delete=models.CASCADE)
    marketAttributeType = models.ForeignKey(MarketAttributeType, on_delete=models.CASCADE)
    date                = models.DateTimeField(default=timezone.now)
    parameterValue      = models.DecimalField(decimal_places=4, max_digits=12)

    def __str__(self):
        return self.marketEntryId.__str__()+"__"+self.marketAttributeType.__str__()+"__"+str(self.date)

class PolicyStrategy(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)

    chosen_option = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.strategy.__str__()+"__"+self.policy.__str__()+"__"+str(self.id)

class PriceEffects(models.Model):

    boundary = models.SmallIntegerField(choices=[(1,'Low'),(2,'Medium'),(3,'High')], default=1)

    low_customers = models.IntegerField(default=1)
    low_sales = models.IntegerField(default=1)

    med_customers = models.IntegerField(default=1)
    med_sales = models.IntegerField(default=1)

    high_customers = models.IntegerField(default=1)
    high_sales = models.IntegerField(default=1)

class Price(models.Model):
    
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    qual = models.ForeignKey(PolicyStrategy, on_delete=models.CASCADE)
    simulator = models.ForeignKey(Simulator, on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=4, max_digits=12, default=1)
    efctOnSales = models.DecimalField(decimal_places=4, max_digits=12, default=0)
    customers = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    def clean(self):
        '''
            Cleanes new fields and saves the object
            returns True if data is clean 
            or raises a ValidationError exception.
        '''
        # Price must be in range
        if (self.price < self.simulator.minPrice):
            raise ValidationError("Price too low.")
        elif (self.price > self.simulator.maxPrice):
            raise ValidationError("Price too high.")
        
        if(self.simulator.priceBoundary1 < self.simulator.minPrice):
            raise ValidationError("Boundary Price is less than minimum price")
        elif(self.simulator.priceBoundary2 > self.simulator.maxPrice):
            raise ValidationError("Boundary price is greater than max price")

        return True

    def getAndSetCustomersAndSales(self):
        '''
            Re-calculates the number of customers and effect on sales. 
            Returns tuple: (no. customers, effect on sales).

            Call this method before handling the num customers 
            and effect on sales attribute as they need to be 
            re-calculated everytime the strategypolicy changes 
        '''
        
        # make sure values are valid
        self.clean()

        qual = int(self.qual.chosen_option)
        price = self.price
        bound1 = self.simulator.priceBoundary1
        bound2 = self.simulator.priceBoundary2
        
        # low quality, low price
        if qual == 1 and (price <= bound1 and price >= self.simulator.minPrice):
            price_effect = PriceEffects.objects.get(boundary=1)
            self.efctOnSales = price_effect.low_sales
            self.customers = price_effect.low_customers

        # low quality med price
        elif qual == 1 and (price <= bound2 and price >= bound1):
            price_effect = PriceEffects.objects.get(boundary=1)
            self.efctOnSales = price_effect.med_sales
            self.customers = price_effect.med_customers

        #low quality high price
        elif qual == 1 and (price <= self.simulator.maxPrice and price >= bound2):
            price_effect = PriceEffects.objects.get(boundary=1)
            self.efctOnSales = price_effect.high_sales
            self.customers = price_effect.high_customers

        #med quality low price
        elif qual == 2 and (price <= bound1 and price >= self.simulator.minPrice):
            price_effect = PriceEffects.objects.get(boundary=2)
            self.efctOnSales = price_effect.low_sales
            self.customers = price_effect.low_customers

        elif qual == 2 and (price <= bound2 and price >= bound1):
            price_effect = PriceEffects.objects.get(boundary=2)
            self.efctOnSales = price_effect.med_sales
            self.customers = price_effect.med_customers

        elif qual == 2 and (price <= self.simulator.maxPrice and price >= bound2):
            price_effect = PriceEffects.objects.get(boundary=2)
            self.efctOnSales = price_effect.high_sales
            self.customers = price_effect.high_customers

        elif qual == 3 and (price <= bound1 and price >= self.simulator.minPrice):
            price_effect = PriceEffects.objects.get(boundary=3)
            self.efctOnSales = price_effect.low_sales
            self.customers = price_effect.low_customers

        elif qual == 3 and (price <= bound2 and price >= bound1):
            price_effect = PriceEffects.objects.get(boundary=3)
            self.efctOnSales = price_effect.med_sales
            self.customers = price_effect.med_customers

        elif qual == 3 and (price <= self.simulator.maxPrice and price >= bound2):
            price_effect = PriceEffects.objects.get(boundary=3)
            self.efctOnSales = price_effect.high_sales
            self.customers = price_effect.high_customers
        
        #save changes
        #self.save()
    
        return self.customers, self.efctOnSales


    def save(self, *args, **kwargs):
        self.getAndSetCustomersAndSales()
        super(Price, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.team.__str__()+" Price"

class MarketEvent(models.Model):

    simulator = models.ForeignKey(Simulator, on_delete=models.CASCADE)
    valid_from = models.DateTimeField(default= timezone.now)
    valid_to   = models.DateTimeField(default= timezone.now)
    market_event_title = models.CharField(max_length=256, default="Market Event")
    market_event_text = models.CharField(max_length=5096, default="The market has changed, this means that consumer habits may also have changed.")

    def __str__(self):
        return self.simulator.__str__()+"__"+self.market_event_title

    @staticmethod
    def get_current_events():
        return MarketEvent.objects.filter(valid_from__lte=timezone.now(), valid_to__gte=timezone.now())

    def get_new_policies(self):
        return PolicyEvent.objects.filter(market_event=self)

class PolicyEvent(models.Model):

    market_event = models.ForeignKey(MarketEvent, on_delete=models.CASCADE)
    policy       = models.ForeignKey(Policy, on_delete=models.CASCADE)
    
    low_cost = models.DecimalField(decimal_places=4, max_digits=12, default=0.5)
    low_customer = models.DecimalField(decimal_places=4, max_digits=12, default=1)
    low_sales = models.DecimalField(decimal_places=4, max_digits=12, default=0.75)
    
    med_cost = models.DecimalField(decimal_places=4, max_digits=12, default=1.00)
    med_customer = models.DecimalField(decimal_places=4, max_digits=12, default=3)
    med_sales = models.DecimalField(decimal_places=4, max_digits=12, default=1.00)

    high_cost = models.DecimalField(decimal_places=4, max_digits=12,default=1.5)
    high_customer = models.DecimalField(decimal_places=4, max_digits=12, default=2)
    high_sales = models.DecimalField(decimal_places=4, max_digits=12, default=0.75)

    def __str__(self):
        return self.market_event.__str__()+"--"+self.policy.__str__()

class PopupEvent(models.Model):
    
    simulator = models.ForeignKey(Simulator, on_delete=models.CASCADE)
    title = models.CharField(max_length=256, default="Alert")
    body_text = models.CharField(max_length=2048, default="")

    # force the popup icon to be from the sweetalert icon library
    icon_class = models.CharField(max_length=32, choices=[
        ("success","Green Tick"),
        ("info","Blue Info"),
        ("error", "Red Cross"),
        ("question", "Grey Question Mark"),
        ("warning", "Yellow Warning"),
        ],
         default="info")

class AcknowledgedEvent(models.Model):
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    event = models.ForeignKey(PopupEvent, on_delete=models.CASCADE)
    has_acknowledged = models.BooleanField(default=False)


@receiver(models.signals.post_delete, sender=Team)
def delete_related_team_objects(sender, instance, **kwargs):
    """
        Strategy is linked to Team however deleting team does not 
        automatically delete the strategy, the reverse is true. 
        
        This method deletes all strategy instances when
        Team.delete() is called
    """
    instance.strategyid.delete()


# start scheduler when server loads app
scheduler = BackgroundScheduler()
scheduler.start() 
