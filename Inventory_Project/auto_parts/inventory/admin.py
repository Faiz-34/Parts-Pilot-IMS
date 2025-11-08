from django.contrib import admin

admin.site.site_header = "PartsPilot IMS Admin"
admin.site.site_title = "PartsPilot IMS"
admin.site.index_title = "Welcome to PartsPilot Inventory Dashboard"


from django.contrib import admin
from .models import Product, Customer,Sale,Invoice,AccessCredential
# Register your models here

admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(Customer)
admin.site.register(Invoice)
admin.site.register(AccessCredential)
# admin.py
from .models import BusinessProfile

admin.site.register(BusinessProfile)


