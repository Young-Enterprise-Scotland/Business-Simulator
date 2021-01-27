import decimal
from django.test import TestCase
from datetime import timedelta, datetime, time
from django.utils import timezone

# Create your tests here.
from .models import *
from .globals import POLICIES
from .calculations import *

class TestUserAccessLevels(TestCase):

    """
        Test the correctness of user permissions
        using object.user.has_perm()
        and object.has_perm() methods.
    """

    def setUp(self):

        # create objects for this test to use
        # django will check for this methods existance 
        # when running python manage.py test
        Simulator.objects.create(
            start=timezone.now(),
            end=timezone.now()+ timedelta(1),
            productName="Test Product",
            maxPrice=10.00,
            minPrice=1.00
            )
        YES.objects.create(user=User.objects.create(username="Staff 1"))
        YES.objects.create(user=User.objects.create(username="Staff 2"))

        School.objects.create(school_name="School 1", user=User.objects.create(username="School 1"))
        School.objects.create(school_name="School 2", user=User.objects.create(username="School 2"))

        Team.objects.create(team_name="Team 1", schoolid=School.objects.get(school_name="School 1"), user=User.objects.create(username="Team 1"))
        Team.objects.create(team_name="Team 2", schoolid=School.objects.get(school_name="School 2"), user=User.objects.create(username="Team 2"))

    def test_yes_staff_permisisons(self):

        #
        #   Test that YES staff permissions are unique to
        #   YES user model objects
        #

        staff_1 = YES.objects.get(user=User.objects.get(username="Staff 1"))
        staff_2 = YES.objects.get(user=User.objects.get(username="Staff 2"))

        self.assertTrue(staff_1.user.has_perm("simulatorApp.is_yes_staff"))
        self.assertTrue(staff_2.user.has_perm("simulatorApp.is_yes_staff"))

        school_1 = School.objects.get(school_name="School 1")
        school_2 = School.objects.get(school_name="School 2")
        self.assertFalse(school_1.user.has_perm("simulatorApp.is_yes_staff"))
        self.assertFalse(school_2.user.has_perm("simulatorApp.is_yes_staff"))

        team_1 = Team.objects.get(team_name="Team 1")
        team_2 = Team.objects.get(team_name="Team 2")

        self.assertFalse(team_1.user.has_perm("simulatorApp.is_yes_staff"))
        self.assertFalse(team_2.user.has_perm("simulatorApp.is_yes_staff"))

    def test_school_permisisons(self):

        #
        #   Test that school permissions are unique to
        #   school user model objects
        #

        staff_1 = YES.objects.get(user=User.objects.get(username="Staff 1"))
        staff_2 = YES.objects.get(user=User.objects.get(username="Staff 2"))
        self.assertFalse(staff_1.user.has_perm("simulatorApp.is_school"))
        self.assertFalse(staff_2.user.has_perm("simulatorApp.is_school"))

        school_1 = School.objects.get(school_name="School 1")
        school_2 = School.objects.get(school_name="School 2")
        self.assertTrue(school_1.user.has_perm("simulatorApp.is_school"))
        self.assertTrue(school_2.user.has_perm("simulatorApp.is_school"))

        team_1 = Team.objects.get(team_name="Team 1")
        team_2 = Team.objects.get(team_name="Team 2")

        self.assertFalse(team_1.user.has_perm("simulatorApp.is_school"))
        self.assertFalse(team_2.user.has_perm("simulatorApp.is_school"))


        staff_1 = YES.objects.get(user=User.objects.get(username="Staff 1"))
        staff_2 = YES.objects.get(user=User.objects.get(username="Staff 2"))
        self.assertFalse(staff_1.has_perm("simulatorApp.is_school"))
        self.assertFalse(staff_2.has_perm("simulatorApp.is_school"))

        school_1 = School.objects.get(school_name="School 1")
        school_2 = School.objects.get(school_name="School 2")
        self.assertTrue(school_1.has_perm("simulatorApp.is_school"))
        self.assertTrue(school_2.has_perm("simulatorApp.is_school"))

        team_1 = Team.objects.get(team_name="Team 1")
        team_2 = Team.objects.get(team_name="Team 2")

        self.assertFalse(team_1.has_perm("simulatorApp.is_school"))
        self.assertFalse(team_2.has_perm("simulatorApp.is_school"))

    def test_team_permisisons(self):

        #
        #   Test that team permissions are unique to
        #   team user model objects
        #

        staff_1 = YES.objects.get(user=User.objects.get(username="Staff 1"))
        staff_2 = YES.objects.get(user=User.objects.get(username="Staff 2"))
        self.assertFalse(staff_1.user.has_perm("simulatorApp.is_team"))
        self.assertFalse(staff_2.user.has_perm("simulatorApp.is_team"))

        school_1 = School.objects.get(school_name="School 1")
        school_2 = School.objects.get(school_name="School 2")
        self.assertFalse(school_1.user.has_perm("simulatorApp.is_team"))
        self.assertFalse(school_2.user.has_perm("simulatorApp.is_team"))

        team_1 = Team.objects.get(team_name="Team 1")
        team_2 = Team.objects.get(team_name="Team 2")

        self.assertTrue(team_1.user.has_perm("simulatorApp.is_team"))
        self.assertTrue(team_2.user.has_perm("simulatorApp.is_team"))

        staff_1 = YES.objects.get(user=User.objects.get(username="Staff 1"))
        staff_2 = YES.objects.get(user=User.objects.get(username="Staff 2"))
        self.assertFalse(staff_1.has_perm("simulatorApp.is_team"))
        self.assertFalse(staff_2.has_perm("simulatorApp.is_team"))

        school_1 = School.objects.get(school_name="School 1")
        school_2 = School.objects.get(school_name="School 2")
        self.assertFalse(school_1.has_perm("simulatorApp.is_team"))
        self.assertFalse(school_2.has_perm("simulatorApp.is_team"))

        team_1 = Team.objects.get(team_name="Team 1")
        team_2 = Team.objects.get(team_name="Team 2")

        self.assertTrue(team_1.has_perm("simulatorApp.is_team"))
        self.assertTrue(team_2.has_perm("simulatorApp.is_team"))

class TestMarketEntry(TestCase):

    def setUp(self):

        Simulator.objects.create(start=timezone.now(),end=timezone.now()+ timedelta(1),productName="Test Product",maxPrice=10.00,minPrice=1.00)

        School.objects.create(school_name="School 1", user=User.objects.create(username="School 1"))
      
        Team.objects.create(team_name="Team 1", schoolid=School.objects.get(school_name="School 1"), user=User.objects.create(username="Team 1"))
        Team.objects.create(team_name="Team 2", schoolid=School.objects.get(school_name="School 1"), user=User.objects.create(username="Team 2"))



    def test_team_market_entry(self):
        """
            Test that for any given team, the market entry, attribute data is related to that team and to that team only. 
        """
        market_entry_t_1 = MarketEntry.objects.get(
            strategyid=Team.objects.get(
                team_name="Team 1"
            ).strategyid
        ) 

        market_entry_t_2 = MarketEntry.objects.get(
            strategyid=Team.objects.get(
                team_name="Team 2"
            ).strategyid
        )

        attib_data_t_1_1 = MarketAttributeTypeData.objects.create(
            marketEntryId=market_entry_t_1, 
            marketAttributeType=MarketAttributeType.objects.get(label="Price"),
            parameterValue=10.05
            )
        attib_data_t_1_2 = MarketAttributeTypeData.objects.create(
            marketEntryId=market_entry_t_1, 
            marketAttributeType=MarketAttributeType.objects.get(label="Price"),
            parameterValue=10.50,
            date=timezone.now()+timedelta(1) 
            )

        attib_data_t_1_2 = MarketAttributeTypeData.objects.create(
            marketEntryId=market_entry_t_1, 
            marketAttributeType=MarketAttributeType.objects.get(label="Profit"),
            parameterValue=4.20,
            )
        
        self.assertEqual(
            len(MarketAttributeTypeData.objects.filter(
                marketEntryId       =market_entry_t_1, 
                marketAttributeType =MarketAttributeType.objects.get(label="Price")
                )),
                2
            )
        self.assertEqual(
            len(MarketAttributeTypeData.objects.filter(
                marketEntryId       =market_entry_t_1, 
                marketAttributeType =MarketAttributeType.objects.get(label="Profit")
                )),
                1
            )
        self.assertEqual(
            len(MarketAttributeTypeData.objects.filter(
                marketEntryId       =market_entry_t_2, 
                marketAttributeType =MarketAttributeType.objects.get(label="Price")
                )),
                0
            )
        
class TestPolicy(TestCase):

    def setUp(self):
        # create objects for this test to use
        # django will check for this methods existance 
        # when running python manage.py test
        Simulator.objects.create(
            start=timezone.now(),
            end=timezone.now()+ timedelta(1),
            productName="Test Product",
            maxPrice=10.00,
            minPrice=1.00
            )
        YES.objects.create(user=User.objects.create(username="Staff 1"))
        YES.objects.create(user=User.objects.create(username="Staff 2"))

        School.objects.create(school_name="School 1", user=User.objects.create(username="School 1"))
        School.objects.create(school_name="School 2", user=User.objects.create(username="School 2"))

        Team.objects.create(team_name="Team 1", schoolid=School.objects.get(school_name="School 1"), user=User.objects.create(username="Team 1"))
        Team.objects.create(team_name="Team 2", schoolid=School.objects.get(school_name="School 2"), user=User.objects.create(username="Team 2"))

    def test_policy_assign(self):
        # test that policies are assigned 
        # to teams when teams are created
        team_1 = Team.objects.get(team_name="Team 1") 
        team_1_policy_strategies = PolicyStrategy.objects.filter(strategy=team_1.strategyid)
        self.assertTrue(len(team_1_policy_strategies) == len(POLICIES))
    
    def test_policy_change(self):
        # test that teams can change policy
        team_1 = Team.objects.get(team_name="Team 1")
        team_1_policy_strategies = PolicyStrategy.objects.filter(strategy=team_1.strategyid)
        for strat in team_1_policy_strategies:
            strat.chosen_option = 2
            strat.save()
            self.assertFalse(strat.chosen_option == 1)

    def test_numCustomers_calculation(self):
        # Test that the number of customers  
        # allocated is correct
        team_1 = Team.objects.get(team_name="Team 1") 
        team_1_policy_strategies = PolicyStrategy.objects.filter(strategy=team_1.strategyid)
        price_obj = Price.objects.get(team=team_1)
        price_obj.price = decimal.Decimal(5.00)

        for strat in team_1_policy_strategies:

            strat.chosen_option = 1
            strat.save()

        #price_obj.getAndSetCustomersAndSales()
        price_obj.save()
        self.assertEqual(numCustomers(team_1),10)

        
        for strat in team_1_policy_strategies:
            strat.chosen_option = 2
            strat.save()

        #price_obj.getAndSetCustomersAndSales()
        price_obj.save()
        self.assertEqual(numCustomers(team_1),31)

        
        for strat in team_1_policy_strategies:
            strat.chosen_option = 3
            strat.save()
        
        #price_obj.getAndSetCustomersAndSales()
        price_obj.save()
        self.assertEqual(numCustomers(team_1),22)
        
    def test_num_products_sold_calculation(self):
        # Test that the number of customers  
        # allocated is correct
        team_1 = Team.objects.get(team_name="Team 1") 
        team_1_policy_strategies = PolicyStrategy.objects.filter(strategy=team_1.strategyid)
        
        price_obj = Price.objects.get(team=team_1)
        price_obj.price = decimal.Decimal(5.00)
        x,y = price_obj.getAndSetCustomersAndSales()
        price_obj.save()

        for strat in team_1_policy_strategies:
            strat.chosen_option = 1
            strat.save()
        self.assertAlmostEqual(
            numberOfProductsSold(team_1),
            decimal.Decimal(0.0450508118)*decimal.Decimal(numCustomers(team_1)),
            places=4)
        
        for strat in team_1_policy_strategies:
            strat.chosen_option = 2
            strat.save()
        
        x,y = price_obj.getAndSetCustomersAndSales()
        price_obj.save()
        self.assertAlmostEqual(
            numberOfProductsSold(team_1), 
            decimal.Decimal(0.85)*decimal.Decimal(numCustomers(team_1)),
            places=4)
        
        for strat in team_1_policy_strategies:
            strat.chosen_option = 3
            strat.save()

        x,y = price_obj.getAndSetCustomersAndSales()
        price_obj.save()
        self.assertAlmostEqual(
            numberOfProductsSold(team_1), 
            decimal.Decimal(0.0563135147)*decimal.Decimal(numCustomers(team_1)),
            places=4)

    def test_total_cost_calculation(self):
        team_1 = Team.objects.get(team_name="Team 1") 
        team_1_policy_strategies = PolicyStrategy.objects.filter(strategy=team_1.strategyid)
        
        for strat in team_1_policy_strategies:
            strat.chosen_option = 1
            strat.save()
        self.assertEqual(float(dailyCost(team_1)),5.00)

        team_1_policy_strategies = PolicyStrategy.objects.filter(strategy=team_1.strategyid)
        
        for strat in team_1_policy_strategies:
            strat.chosen_option = 2
            strat.save()
        self.assertEqual(float(dailyCost(team_1)),10.00)

        team_1_policy_strategies = PolicyStrategy.objects.filter(strategy=team_1.strategyid)
        
        for strat in team_1_policy_strategies:
            strat.chosen_option = 3
            strat.save()
        self.assertEqual(float(dailyCost(team_1)),15.00)

    def test_productCost_calculation(self):
        team_1 = Team.objects.get(team_name="Team 1") 
        team_1_policy_strategies = PolicyStrategy.objects.filter(strategy=team_1.strategyid)
        
        for strat in team_1_policy_strategies:
            strat.chosen_option = 1
            strat.save()
        self.assertEqual(float(productCost(team_1)),1.00)

        team_1_policy_strategies = PolicyStrategy.objects.filter(strategy=team_1.strategyid)
        
        for strat in team_1_policy_strategies:
            strat.chosen_option = 2
            strat.save()
        self.assertEqual(float(productCost(team_1)),2.00)

        team_1_policy_strategies = PolicyStrategy.objects.filter(strategy=team_1.strategyid)
        
        for strat in team_1_policy_strategies:
            strat.chosen_option = 3
            strat.save()
        self.assertEqual(float(productCost(team_1)),3.00)

class TestPrice(TestCase):

    def setUp(self):
        # create objects for this test to use
        # django will check for this methods existance 
        # when running python manage.py test
        Simulator.objects.create(
            start=timezone.now(),
            end=timezone.now()+ timedelta(1),
            productName="Test Product",
            maxPrice=10.00,
            minPrice=1.00
            )
        YES.objects.create(user=User.objects.create(username="Staff 1"))
       
        School.objects.create(school_name="School 1", user=User.objects.create(username="School 1"))
        
        Team.objects.create(team_name="Team 1", schoolid=School.objects.get(school_name="School 1"), user=User.objects.create(username="Team 1"))
    
    def test_price_model_clean_min(self):
        'Test that the clean method enforces min prices boundary'
        team1 = Team.objects.get(team_name="Team 1")
        simulator = Simulator.objects.annotate(models.Max('id'))[0]
        team1_price = Price.objects.get(team=team1)
        team1_price.price = simulator.minPrice- decimal.Decimal(0.01)
        self.assertRaises(ValidationError,team1_price.clean)
    
    def test_price_model_clean_max(self):
        'Test that the max price boundary is enforced'
        team1 = Team.objects.get(team_name="Team 1")
        simulator = Simulator.objects.annotate(models.Max('id'))[0]
        team1_price = Price.objects.get(team=team1)
        team1_price.price = simulator.maxPrice+decimal.Decimal(0.01)
        self.assertRaises(ValidationError, team1_price.clean)

    def test_price_clean_valid(self):

        'Check that clean method saves data once it has updated parameters'
        team1 = Team.objects.get(team_name="Team 1")
        simulator = Simulator.objects.annotate(models.Max('id'))[0]
        team1_price = Price.objects.get(team=team1)

        team1_price.price= decimal.Decimal(5.00)
        team1_price.save()
        self.assertEqual(team1_price.price, decimal.Decimal(5.00))
        self.assertEqual(team1_price.price, Price.objects.get(team=team1).price)

class TestSchedule(TestCase):
    
    def test_schedule_start(self):
        noErr = True
        try:
            simulator = Simulator.objects.create(
                start=timezone.now(),
                end=timezone.now()+ timedelta(1),
                productName="Test Product",
                maxPrice=10.00,
                minPrice=1.00
            )
        except Exception as e:
            print(e)
            noErr = False

        self.assertTrue(noErr == True)

    def test_schedule_update(self):
        noErr = True
        simulator = Simulator.objects.create(
            start=timezone.now(),
            end=timezone.now()+ timedelta(1),
            productName="Test Product",
            maxPrice=10.00,
            minPrice=1.00
        )

        simulator.end += timedelta(1)

        noErr = True
        try:
            simulator.save()
        except Exception as e:
            print(e)
            noErr = False
        self.assertTrue(noErr==True)

class TestMarketEvent(TestCase):

    def setUp(self):
        # create objects for this test to use
        # django will check for this methods existance 
        # when running python manage.py test
        Simulator.objects.create(
            start=timezone.now(),
            end=timezone.now()+ timedelta(1),
            productName="Test Product",
            maxPrice=10.00,
            minPrice=1.00
            )
        YES.objects.create(user=User.objects.create(username="Staff 1"))
       
        School.objects.create(school_name="School 1", user=User.objects.create(username="School 1"))
        
        Team.objects.create(team_name="Team 1", schoolid=School.objects.get(school_name="School 1"), user=User.objects.create(username="Team 1"))
    
        
    def market_event_create(self):

        (obj,created) = MarketEvent.objects.get_or_create(
            simulator = Simulator.objects.annotate(models.Max('id'))[0],
            market_event_title = "Custom Title",
            market_event_text = "Custom Text"
        )
        self.assertTrue(created)

    def policy_event_create(self):

        (obj,created) = MarketEvent.objects.get_or_create(
            simulator = Simulator.objects.annotate(models.Max('id'))[0],
            market_event_title = "Custom Title",
            market_event_text = "Custom Text"
        )

        (policyEvent, created) = PolicyEvent.objects.get_or_create(
            market_event = obj,
            policy = Policy.objects.get(name=POLICIES[0]),
            low_cost = 2.0,
            low_customer = 5,
            low_sales = 2
        )

        self.assertTrue(created)

    def market_event_update(self):

        (obj,created) = MarketEvent.objects.get_or_create(
            simulator = Simulator.objects.annotate(models.Max('id'))[0],
            market_event_title = "Custom Title",
            market_event_text = "Custom Text"
        )

        cpy = obj
        cpy.market_event_title="Updated Title"
        cpy.save()

        self.assertNotEqual(cpy, obj)

        obj = MarketEvent.objects.get(
            simulator = Simulator.objects.annotate(models.Max('id'))[0],
            market_event_title = "Updated Title",
            market_event_text = "Custom Text"
        )
        self.assertEqual(cpy, obj)

    def get_market_events(self):

        for i in range(1,6):
            (obj,created) = MarketEvent.objects.get_or_create(
                simulator = Simulator.objects.annotate(models.Max('id'))[0],
                market_event_title = "Custom Title "+str(i),
                market_event_text = "Custom Text",
                valid_from = timezone.now(),
                valid_to = datetime.combine(timezone.now().date(), timedelta(1))
            )
        
        (obj,created) = MarketEvent.objects.get_or_create(
                simulator = Simulator.objects.annotate(models.Max('id'))[0],
                market_event_title = "Custom Title expected failure",
                market_event_text = "Custom Text",
                valid_from = timezone.now(),
                valid_to = datetime.combine(timezone.now().date(), time(0,0)-timedelta(2))
            )
        
        self.assertTrue(len(MarketEvent.get_current_events())==5)