from django.contrib import admin
from .models import Category, Product, Customer, Supplier, StationeryItem, Sale, SaleItem, Debt, Expenditure

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Supplier)
admin.site.register(StationeryItem)
admin.site.register(Sale)
admin.site.register(SaleItem)
admin.site.register(Debt)
admin.site.register(Expenditure)
