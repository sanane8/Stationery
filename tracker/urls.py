from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Stationery items
    path('stationery/', views.stationery_list, name='stationery_list'),
    path('stationery/<int:pk>/', views.stationery_detail, name='stationery_detail'),
    path('stationery/create/', views.create_stationery_item, name='create_stationery_item'),
    
    # Sales
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/create/', views.create_sale, name='create_sale'),
    path('sales/<int:sale_id>/add-item/', views.add_sale_item, name='add_sale_item'),
    
    # Debts
    path('debts/', views.debts_list, name='debts_list'),
    path('debts/<int:pk>/', views.debt_detail, name='debt_detail'),
    path('debts/create/', views.create_debt, name='create_debt'),
    path('debts/<int:debt_id>/payment/', views.add_payment, name='add_payment'),
    
    # Customers
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/create/', views.create_customer, name='create_customer'),
]
