from datetime import timedelta
import time
from django.db import models

from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler


def process_teams():

    # move import to method to solve circular imports issue
    # not elegent however a suggested solution to this issue.
    # Reference:
    # https://stackoverflow.com/questions/26379026/resolving-circular-imports-in-celery-and-django
    from .calculations import num_customers, number_of_products_sold, daily_cost,product_cost
    from .models import Simulator
    
    print("Closing Market")
    simulation.marketOpen = False
    simulation.save()

    simulation.marketOpen = True
    simulation.save()
    print("Market Re-opened")
    


def start():
    from .models import Simulator

    simulation = Simulator.objects.annotate(models.Max('id'))[0]
    start = simulation.start
    end = simulation.end
    length = simulation.lengthOfTradingDay

    scheduler = BackgroundScheduler()
    scheduler.add_job(process_teams, 'cron', start_date=start, end_date=end, second=10)
    scheduler.start()