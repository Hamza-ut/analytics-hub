from django.contrib import admin
from .models import StrainQCConfig, StrainQCResult

admin.site.register(StrainQCConfig)
admin.site.register(StrainQCResult)
