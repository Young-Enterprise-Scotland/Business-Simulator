from datetime import timedelta
import time
from django.db import models

from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler


scheduler_global = None

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
    from .calculations import   num_customers,          \
                                number_of_products_sold,\
                                daily_cost,product_cost
    from django.db import models
    from .models import Simulator
    

    simulation = Simulator.objects.annotate(models.Max('id'))[0]
    start = simulation.start
    end = simulation.end
    length = simulation.lengthOfTradingDay
    print("Closing Market")
    simulation.marketOpen = False
    simulation.save()

    simulation.marketOpen = True
    simulation.save()
    print("Market Re-opened")
    


def start(simulation=None):
    # start scheduler when simulator is created/updated

    # avoid circular imports
    from .models import Simulator
    global scheduler_global

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
    print(f"\nTotal seconds: {length}")    
    print(f"Setting up a schedule every {days}days {hours}hours {minutes}minutes {seconds}seconds\n")
    

    # temp fix until seconds to days calculation works
    scheduler.add_job(process_teams, 'cron', start_date=start, end_date=end, id="calculate", day=days, hour=hours, minute=minutes, second=seconds)
    scheduler_global = scheduler 
    


def update():

    global scheduler_global
    
    # Update sheduler when simulator is updated
    if scheduler_global is not None:
        scheduler_global.remove_job("calculate")
    start()
    

scheduler = BackgroundScheduler()
scheduler.start()