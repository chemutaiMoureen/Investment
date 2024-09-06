# investment_app/admin.py
from django.contrib import admin
from .models import User, InvestmentAccount, AccountMembership, Transaction

admin.site.register(User)
admin.site.register(InvestmentAccount)
admin.site.register(AccountMembership)
admin.site.register(Transaction)
