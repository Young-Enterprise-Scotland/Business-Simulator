from django.apps import AppConfig
from django.conf import settings
from .globals import init_cron_jobs_from_db


class SimulatorappConfig(AppConfig):
    name = 'simulatorApp'

    def ready(self) -> None:

        if settings.DEBUG:
            print("Restoring cronjobs")
        # retore scronjobs
        init_cron_jobs_from_db()
        return super().ready()
        