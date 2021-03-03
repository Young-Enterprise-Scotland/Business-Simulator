#
# File to define global functions, variables for general use
#
from django.conf import settings


def init_cron_jobs_from_db():
    'Restores previous cronjobs.\
    Allows cron jobs to persist over server restarts'
    from .models import CalculationCronJobs,\
                        MarketEventCronJobs, \
                        SimulatorEndCronJobs

    for job in CalculationCronJobs.objects.all():
        job.save()
    for job in MarketEventCronJobs.objects.all():
        job.save()
    for job in SimulatorEndCronJobs.objects.all():
        job.save()
    
    if settings.DEBUG:
        from .models import scheduler
        scheduler.print_jobs()
        print("Scheduler state:",scheduler.state)
    return 

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

POLICIES = [
        "Market Research & Product Development",
        "Quality of Raw Materials",
        "Appearance of Packaging",
        "Physical Position in Market",
        "Size of Unit",
        "Internal Appearance",
        "Targeted Online Adverts",
        "Physical Print (flyers/posters)",
        "Newspaper Advert"
    ]

MARKET_ATTRIBUTE_TYPES = [
    "Product Cost",
    "Daily Cost",
    "Price",
    "Number of Customers",
    "Number of Products Sold",
    "Profit",
    "Net Profit",
    "Size of Market",
    "Market Share"
]