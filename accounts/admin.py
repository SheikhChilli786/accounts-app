from django.contrib import admin
from . import models
# Register your models here.
@admin.register(models.Party)
class adminParty(admin.ModelAdmin):
    pass
@admin.register(models.Transaction)
class adminTransaction(admin.ModelAdmin):
    pass
@admin.register(models.Form)
class adminForm(admin.ModelAdmin):
    pass
@admin.register(models.Product)
class adminProduct(admin.ModelAdmin):
    pass
@admin.register(models.TradeItem)
class adminItems(admin.ModelAdmin):
    pass