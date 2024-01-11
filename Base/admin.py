from django.contrib import admin
from .models import StockDetail
from . import models
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
# Register your models here.
admin.site.register(StockDetail)
admin.site.register(models.Profile)
class AccountInline(admin.StackedInline):
	model= models.UserAccount
	can_delete = False
	verbose_name_plural = 'Account'

class CustomizedUserAdmin (UserAdmin):
	inlines = (AccountInline, )

admin.site.unregister(User)
admin.site.register(User, CustomizedUserAdmin)
admin.site.register(models.news)
admin.site.register(models.UserAccount)