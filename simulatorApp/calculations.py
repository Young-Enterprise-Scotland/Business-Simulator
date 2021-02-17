import decimal
from collections import defaultdict
from datetime import timedelta
from django.utils import timezone
from django.db import models
from .models import MarketAttributeType,\
     MarketAttributeTypeData,\
     Simulator,\
     Policy,\
     PolicyStrategy,\
     Team,\
     Strategy,\
     Price,\
     MarketEvent,\
     PolicyEvent,\
     MarketEntry
from django.conf import settings
from .globals import POLICIES, MARKET_ATTRIBUTE_TYPES


# Place calculations which are used at the end of the trading day here

def get_weighting_customers(policy,chosen_option, market_events):
    'Checks whether the number of customers is to be affected by a market event.'
    
    if len(market_events)>0:
        policies = market_events[0].get_new_policies().filter(policy=policy)
        if len(policies)>0:
            # use market event policy
            policy = policies[0]

    if(chosen_option==1):
        return policy.low_customer
    if chosen_option==2:
        return policy.med_customer
    else:
        return policy.high_customer

def get_weighting_sales(policy,chosen_option, market_events):
    'Checks whether the number of sales is to be affected by a market event.'
    if len(market_events)>0:
        policies = market_events[0].get_new_policies().filter(policy=policy)
        if len(policies)>0:
            # use market event policy
            policy = policies[0]
    if(chosen_option==1):
        return policy.low_sales
    if chosen_option==2:
        return policy.med_sales
    else:
        return policy.high_sales

def get_weighting_cost(policy,chosen_option, market_events):
    'Checks whether the cost is to be affected by a market event.'
    if len(market_events)>0:
        policies = market_events[0].get_new_policies().filter(policy=policy)
        if len(policies)>0:
            # use market event policy
            policy = policies[0]
    if(chosen_option==1):
        return policy.low_cost
    if chosen_option==2:
        return policy.med_cost
    else:
        return policy.high_cost

def numCustomers(teamobject):
    'Calculate the number of customers a team recieves based on their policy stratagy'

    policystrategies = PolicyStrategy.objects.filter(strategy=teamobject.strategyid)

    # initalise total_customers to be the minimum number of customers
    price_obj = Price.objects.get(team=teamobject)
    price_obj.getAndSetCustomersAndSales()
    total_customers = price_obj.customers

    market_events = MarketEvent.get_current_events()
    for ps in policystrategies:
        total_customers += get_weighting_customers(ps.policy, ps.chosen_option, market_events)
        
    return total_customers

def numberOfProductsSold(teamobject):

    policystrategies = PolicyStrategy.objects.filter(strategy=teamobject.strategyid)

    price_obj = Price.objects.get(team=teamobject)
    price_obj.getAndSetCustomersAndSales()
    cum_sales = decimal.Decimal(price_obj.efctOnSales)
    
    market_events = MarketEvent.get_current_events()
    for ps in policystrategies:
        cum_sales *= decimal.Decimal(get_weighting_sales(ps.policy, ps.chosen_option, market_events))
    return cum_sales*decimal.Decimal(numCustomers(teamobject))

def dailyCost(teamobject):
    'Calculates a teams daily cost based on their policy choices'

    policystrategies = PolicyStrategy.objects.filter(strategy=teamobject.strategyid)
    total_cost = decimal.Decimal(0)

    market_events = MarketEvent.get_current_events()
    for ps in policystrategies:
        total_cost += get_weighting_cost(ps.policy, ps.chosen_option, market_events)        
    return total_cost

def productCost(teamobject):
    'Calculates the cost of a product'
    
    policystrategies = PolicyStrategy.objects.filter(
        strategy=teamobject.strategyid, 
        # select 'quality of raw materials' and 'appearance of packaging' Policies 
        policy__in=Policy.objects.filter(name__in=POLICIES[2:4])
    )
    total_cost = decimal.Decimal(0)

    market_events = MarketEvent.get_current_events()
    for ps in policystrategies:
        total_cost += get_weighting_cost(ps.policy, ps.chosen_option, market_events)  
        
    return total_cost

def profit(teamobject):
    price_obj = Price.objects.get(team=teamobject)
    return (price_obj.price - productCost(teamobject)) * numberOfProductsSold(teamobject)

def netProfit(teamobject):

    length_trading_day = Simulator.objects.all().order_by('-id')[0].lengthOfTradingDay

    # get the previous netprofit value if exists
    previous_profits = MarketAttributeTypeData.objects.filter(
        marketAttributeType=MarketAttributeType.objects.get(label=MARKET_ATTRIBUTE_TYPES[6]), #select net profit attribute
        marketEntryId = MarketEntry.objects.get(strategyid=teamobject.strategyid)
    ).order_by('-id')
    
    if len(previous_profits)>0:
        previous_profit = previous_profits[0].parameterValue
    else:
        previous_profit = 0

    return previous_profit + (profit(teamobject) - dailyCost(teamobject))

def sizeOfMarket():
    total_prods_sold = 0
    for each in Team.objects.all():
        total_prods_sold += numberOfProductsSold(each)
    return total_prods_sold

def marketShare(teamobject, sizeofmarket=None):
    'allow size of market to be passed in so it is not recalculated many times'
    if not sizeofmarket:
        sizeofmarket = sizeOfMarket()
    if sizeofmarket == 0:
        return 0
    return (numberOfProductsSold(teamobject)/sizeofmarket)*100

def assignLeaderboardPositions(team_net_profit_list):

    schools_collection = defaultdict(lambda:[])

    # sort teams by netprofit descending (highest attribute value is first)
    team_net_profit_list = sorted(team_net_profit_list, key=lambda idx:idx[1],reverse=True)
    for i in range(len(team_net_profit_list)):
        team = team_net_profit_list[i][0]
        team.leaderboard_position = i+1
        team.save()
        schools_collection[team.schoolid].append(team)

    count = 0
    for school, team_arr in schools_collection.items():
        team_arr = sorted(team_arr, key=lambda team:team.leaderboard_position)
        for i,team in enumerate(team_arr):
            team.school_position = i+1
            team.save()
    return



    




    
