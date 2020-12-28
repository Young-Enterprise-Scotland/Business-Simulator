from django.test import TestCase
from datetime import timedelta
from django.utils import timezone

# Create your tests here.
from .models import *
from .globals import POLICIES
from .calculations import num_customers

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
            minPrice=2.50
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

        Simulator.objects.create(start=timezone.now(),end=timezone.now()+ timedelta(1),productName="Test Product",maxPrice=10.00,minPrice=2.50)

        MarketAttributeType.objects.create(label="Price")
        MarketAttributeType.objects.create(label="Market Share")
        MarketAttributeType.objects.create(label="Profit")

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
            minPrice=2.50
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

    def test_num_customers_calculation(self):
        # Test that the number of customers  
        # allocated is correct
        team_1 = Team.objects.get(team_name="Team 1") 
        team_1_policy_strategies = PolicyStrategy.objects.filter(strategy=team_1.strategyid)
        
        for strat in team_1_policy_strategies:
            strat.chosen_option = 1
            strat.save()
        self.assertEqual(num_customers(team_1),10)

        team_1_policy_strategies = PolicyStrategy.objects.filter(strategy=team_1.strategyid)
        
        for strat in team_1_policy_strategies:
            strat.chosen_option = 2
            strat.save()
        self.assertEqual(num_customers(team_1),30)

        team_1_policy_strategies = PolicyStrategy.objects.filter(strategy=team_1.strategyid)
        
        for strat in team_1_policy_strategies:
            strat.chosen_option = 3
            strat.save()
        self.assertEqual(num_customers(team_1),20)
        


        

