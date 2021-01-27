import time
from datetime import timedelta
from django.db import models
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from simulatorApp.calculations import marketShare, profit, sizeOfMarket
from simulatorApp.models import Team
from .models import MarketAttributeType, MarketAttributeTypeData, MarketEntry, Price, scheduler
from .globals import MARKET_ATTRIBUTE_TYPES

def secondsToDHMS(n: int)-> tuple: 
    '''
    Turn seconds into days hours minutes and seconds
    @return tuple of integers (day, hour, minute, second)
    Source:
    https://www.geeksforgeeks.org/converting-seconds-into-days-hours-minutes-and-seconds/
    Accessed 13/01/2021
    '''
    day = n // (24 * 3600) 
  
    n %= (24 * 3600) 
    hour = n // 3600
  
    n %= 3600
    minutes = n // 60
  
    n %= 60
    seconds = n 
    return (int(day),int(hour),int(minutes),int(seconds))


def process_teams():

    # move import to method to solve circular imports issue
    # not elegent however a suggested solution to this issue.
    # Reference:
    # https://stackoverflow.com/questions/26379026/resolving-circular-imports-in-celery-and-django
    from .calculations import   numCustomers,          \
                                numberOfProductsSold,  \
                                dailyCost,productCost, \
                                profit, netProfit,     \
                                sizeOfMarket, marketShare    
    from django.db import models
    from .models import Team, Simulator, Price, MarketEvent

    market_events = MarketEvent.get_current_events() 
    if settings.DEBUG:
        for event in market_events:
            print(event)


    simulation = Simulator.objects.annotate(models.Max('id'))[0]
    start = simulation.start
    end = simulation.end
    length = simulation.lengthOfTradingDay

    if settings.DEBUG:
        print(f"Closing Market {timezone.now()}")
    simulation.marketOpen = False
    simulation.save()

    # get all teams
    teams = Team.objects.all()
    # update attributes for each team
 
    size_of_market = sizeOfMarket()
    for team in teams:

        market_entry = MarketEntry.objects.get(strategyid=team.strategyid, simulator=simulation)
        num_of_products_sold = numberOfProductsSold(team)
        number_of_customers = numCustomers(team)
        daily_cost = dailyCost(team)
        product_cost = productCost(team)
        team_profit = profit(team)
        net_profit = netProfit(team)
        market_share = marketShare(team,sizeofmarket=size_of_market)
        price = Price.objects.get(team=team)

        #add product cost entry
        MarketAttributeTypeData.objects.create(
            marketEntryId = market_entry,
            marketAttributeType = MarketAttributeType.objects.get(label=MARKET_ATTRIBUTE_TYPES[0]),
            date = timezone.now(),
            parameterValue = product_cost
        )

        # add daily cost
        MarketAttributeTypeData.objects.create(
            marketEntryId = market_entry,
            marketAttributeType = MarketAttributeType.objects.get(label=MARKET_ATTRIBUTE_TYPES[1]),
            date = timezone.now(),
            parameterValue = daily_cost
        )

        # add price entry
        MarketAttributeTypeData.objects.create(
            marketEntryId = market_entry,
            marketAttributeType = MarketAttributeType.objects.get(label=MARKET_ATTRIBUTE_TYPES[2]),
            date = timezone.now(),
            parameterValue = price.price
        )

        # add number of customers entry
        MarketAttributeTypeData.objects.create(
            marketEntryId = market_entry,
            marketAttributeType = MarketAttributeType.objects.get(label=MARKET_ATTRIBUTE_TYPES[3]),
            date = timezone.now(),
            parameterValue = number_of_customers
        )

        # add number of products sold entry
        MarketAttributeTypeData.objects.create(
            marketEntryId = market_entry,
            marketAttributeType = MarketAttributeType.objects.get(label=MARKET_ATTRIBUTE_TYPES[4]),
            date = timezone.now(),
            parameterValue = num_of_products_sold
        )

        # add profit entry
        MarketAttributeTypeData.objects.create(
            marketEntryId = market_entry,
            marketAttributeType = MarketAttributeType.objects.get(label=MARKET_ATTRIBUTE_TYPES[5]),
            date = timezone.now(),
            parameterValue = team_profit
        )

        # add net profit entry
        MarketAttributeTypeData.objects.create(
            marketEntryId = market_entry,
            marketAttributeType = MarketAttributeType.objects.get(label=MARKET_ATTRIBUTE_TYPES[6]),
            date = timezone.now(),
            parameterValue = net_profit
        )

        # add size of market entry
        MarketAttributeTypeData.objects.create(
            marketEntryId = market_entry,
            marketAttributeType = MarketAttributeType.objects.get(label=MARKET_ATTRIBUTE_TYPES[7]),
            date = timezone.now(),
            parameterValue = size_of_market
        )

        # add market share entry
        MarketAttributeTypeData.objects.create(
            marketEntryId = market_entry,
            marketAttributeType = MarketAttributeType.objects.get(label=MARKET_ATTRIBUTE_TYPES[8]),
            date = timezone.now(),
            parameterValue = market_share
        )
        if settings.DEBUG:
            print(f"\nTeam:{team.team_name}\n Product Cost: {product_cost}\n Daily Cost:{daily_cost}\n Price:{price.price}\n Number of Customers:{number_of_customers}\n Number of Products Sold:{num_of_products_sold}\n Profit:{team_profit}\n Net Profit:{net_profit}\n Size of Market:{size_of_market}\n Market Share:{market_share}\n")

    simulation.marketOpen = True
    simulation.save()

    if settings.DEBUG:
        print(f"Market Re-opened {timezone.now()}")
    


def start(simulation=None):
    # start scheduler when simulator is created/updated
    # avoid circular imports
    from .models import Simulator

    if simulation is None:
        simulation = Simulator.objects.annotate(models.Max('id'))[0]
    
    start = simulation.start
    end = simulation.end
    length = simulation.lengthOfTradingDay.total_seconds()
    days, hours, minutes, seconds = secondsToDHMS(length)
    
    if(days==0):
        days='*'        # everyday
    if hours==0:
        hours='*'       # everyhour
    if minutes==0:
        minutes = '*'   # everyminute
    if seconds==0:
        seconds = '*'   # everysecond
    if settings.DEBUG:
        print(f"Setting up cronjob,{days}days {hours}hours {minutes}minutes {seconds}seconds.")
    scheduler.add_job(process_teams, 'cron', start_date=start, end_date=end, id="calculate", replace_existing=True, day=days, hour=hours, minute=minutes, second=seconds)
    
    

