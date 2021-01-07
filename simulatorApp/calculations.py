from datetime import timedelta
from django.utils import timezone
import decimal

from .models import Simulator, Policy, PolicyStrategy, Team, Strategy, Price
from BusinessSimulator.settings import DEBUG
from .globals import POLICIES

# Place calculations which are used at the end of the trading day here
#
#

#startdate=timezone.now()-timedelta(days=1),enddate=timezone.now()

def num_customers(teamobject):
    'Calculate the number of customers a team recieves based on their policy stratagy'

    policystrategies = PolicyStrategy.objects.filter(strategy=teamobject.strategyid)
    
    # initalise total_customers to be the minimum number of customers
    

    price_obj = Price.objects.get(team=teamobject)
    price_obj.getAndSetCustomersAndSales()
    total_customers = price_obj.customers

    for ps in policystrategies:
        if ps.chosen_option == 1: # low option
            total_customers += ps.policy.low_customer
        elif ps.chosen_option == 2: # med option
            total_customers += ps.policy.med_customer 
        elif ps.chosen_option == 3: # high option
            total_customers += ps.policy.high_customer
    
    return total_customers

def number_of_products_sold(teamobject):

    policystrategies = PolicyStrategy.objects.filter(strategy=teamobject.strategyid)

    price_obj = Price.objects.get(team=teamobject)
    price_obj.getAndSetCustomersAndSales()
    cum_sales = decimal.Decimal(price_obj.efctOnSales)
    for ps in policystrategies:
        if ps.chosen_option == 1: # low option
            cum_sales *= decimal.Decimal(ps.policy.low_sales)
        elif ps.chosen_option == 2: # med option
            cum_sales *= decimal.Decimal(ps.policy.med_sales)
        elif ps.chosen_option == 3: # high option
            cum_sales *= decimal.Decimal(ps.policy.high_sales)
    return cum_sales*decimal.Decimal(num_customers(teamobject))

def daily_cost(teamobject):
    'Calculates a teams daily cost based on their policy choices'

    policystrategies = PolicyStrategy.objects.filter(strategy=teamobject.strategyid)
    total_cost = decimal.Decimal(0)

    for ps in policystrategies:
        if ps.chosen_option == 1: # low option
            total_cost += ps.policy.low_cost
        elif ps.chosen_option == 2: # med option
            total_cost += ps.policy.med_cost 
        elif ps.chosen_option == 3: # high option
            total_cost += ps.policy.high_cost
        
    return total_cost

def product_cost(teamobject):
    'Calculates the cost of a product'
    
    policystrategies = PolicyStrategy.objects.filter(
        strategy=teamobject.strategyid, 
        # select 'quality of raw materials' and 'appearance of packaging' Policies 
        policy__in=Policy.objects.filter(name__in=POLICIES[2:4])
        )
    total_cost = decimal.Decimal(0)

    for ps in policystrategies:
        if ps.chosen_option == 1: # low option
            total_cost += ps.policy.low_cost
        elif ps.chosen_option == 2: # med option
            total_cost += ps.policy.med_cost 
        elif ps.chosen_option == 3: # high option
            total_cost += ps.policy.high_cost
        
    return total_cost

def profit(teamobject):
    price_obj = Price.objects.get(team=teamobject)
    return (price_obj.price - product_cost(teamobject)) * number_of_products_sold(teamobject)

def net_profit(teamobject):
    return profit(teamobject) - daily_cost(teamobject)

def size_of_market():
    total_prods_sold = 0
    for each in Team.objects.all():
        total_prods_sold += number_of_products_sold(each)
    return total_prods_sold

def market_share(teamobject):
    return number_of_products_sold(teamobject)/size_of_market()
