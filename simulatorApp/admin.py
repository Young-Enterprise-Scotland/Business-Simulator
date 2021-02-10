from django.contrib import admin
from django.conf import settings
from .models import CalculationCronJobs, MarketEventCronJobs, Simulator, \
                    YES, \
                    School, \
                    Team, \
                    Policy, \
                    PolicyEvent, \
                    PolicyStrategy, \
                    MarketEvent, \
                    PopupEvent, \
                    SimulatorEndCronJobs, \
                    PriceEffects

# Register your models here.
# If app not registered then
# it will not appear on the
# back of site admin panel!

admin.site.register(Simulator)
admin.site.register(YES)
admin.site.register(School)
admin.site.register(Team)
# Hide these objects so admins
# cannot interact with them and cause 
# issues
#admin.site.register(Strategy)
#admin.site.register(MarketEntry)
#admin.site.register(MarketAttributeType)
#admin.site.register(MarketAttributeTypeData)
admin.site.register(Policy)
#admin.site.register(Price)
#admin.site.register(PriceEffects)
admin.site.register(PolicyStrategy)
admin.site.register(MarketEvent)
admin.site.register(PolicyEvent)
admin.site.register(PopupEvent)
admin.site.register(SimulatorEndCronJobs)
admin.site.register(CalculationCronJobs)
admin.site.register(MarketEventCronJobs)
admin.site.site_header = "Young Enterprise Scotland Admin Panel"

