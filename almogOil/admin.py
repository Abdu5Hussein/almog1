from django.contrib import admin
from .models import Measurement,Mainitem



# Import the User model inside a method to avoid circular imports
#def get_queryset(self, request):
##   return super().get_queryset(request).filter(...)

# Register your models here.
admin.site.register(Measurement)
admin.site.register(Mainitem)

