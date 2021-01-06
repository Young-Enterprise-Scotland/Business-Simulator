from datetime import timedelta
import time
from django.db import models

from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler

scheduler_global = None

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

    days    = int(length/(24*3600))
    hours   = int((length%(24*3600))/3600)
    minutes = int((length%(24*3600*3600))/60)
    seconds = int((length%(24*3600*3600*60))/60)
    
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
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_teams, 'cron', start_date=start, end_date=end, id="calculate", day=days, hour=hours, minute=minutes, second=seconds)
    scheduler.start()
    scheduler_global = scheduler 


def update():

    global scheduler_global
    
    # Update sheduler when simulator is updated
    if scheduler_global is not None:
        scheduler_global.remove_job("calculate")
    start()
    
