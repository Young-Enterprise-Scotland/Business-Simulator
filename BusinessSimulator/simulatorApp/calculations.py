from datetime import datetime, timedelta
from  .models import *
from BusinessSimulator.settings import DEBUG
# Place calculations which are used at the end of the trading day here
#
#

#startdate=timezone.now()-timedelta(days=1),enddate=timezone.now()

def num_customers(teamobject):
    'Calculate the number of customers a team recieves based on their policy stratagy'

    policystrategies = PolicyStrategy.objects.filter(strategy=teamobject.strategyid)
    total_customers = 0

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
    cum_sales = 1

    for ps in policystrategies:
        if ps.chosen_option == 1: # low option
            cum_sales *= ps.policy.low_sales
        elif ps.chosen_option == 2: # med option
            cum_sales *= ps.policy.med_sales 
        elif ps.chosen_option == 3: # high option
            cum_sales *= ps.policy.high_sales
    
    # YES allows for products to be non integer and rounded to 2dp
    return round(cum_sales*num_customers(teamobject),2)

def daily_cost(teamobject):

    policystrategies = PolicyStrategy.objects.filter(strategy=teamobject.strategyid)
    total_cost = 0

    for ps in policystrategies:
        if ps.chosen_option == 1: # low option
            total_cost += ps.policy.low_cost
        elif ps.chosen_option == 2: # med option
            total_cost += ps.policy.med_cost 
        elif ps.chosen_option == 3: # high option
            total_cost += ps.policy.high_cost
        
    return total_cost