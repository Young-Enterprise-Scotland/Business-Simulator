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
        if ps.chosen_option == 1: #low option
            total_customers += ps.policy.low_customer
        elif ps.chosen_option == 2: # med option
            total_customers += ps.policy.med_customer 
        elif ps.chosen_option == 3: # high option
            total_customers += ps.policy.high_customer
        
    if DEBUG:
        print("total customers:\n",total_customers)
    return total_customers