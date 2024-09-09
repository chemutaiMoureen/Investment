from django.contrib import admin
from .models import InvestmentAccount, AccountMembership, Transaction

# Register the other models
admin.site.register(InvestmentAccount)
admin.site.register(AccountMembership)
admin.site.register(Transaction)
