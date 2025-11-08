from django.urls import path
from . import views
from .views import invoice_detail
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.intro_view, name='intro'),
    path('access/', views.access_gate_view, name='access_gate'),
    path('dashboard/', views.dashboard_view, name='dashboard'),   # 📊 Dashboard
    path('customers/', views.customer_list, name='customer_list'),    # 👥 Customer List
    path('low-stock/', views.low_stock_list_view, name='low_stock_list'),
    path('search/', views.global_search, name='global_search'),


    # Product Queries

    path('products/add/', views.add_product, name='add_product'),       #for add Product
    path('products/', views.product_list, name='product_list'),       # 📦 Product List
    path('products/edit/<int:pk>/', views.edit_product_view, name='product_edit'),   #update
    path('products/delete/<int:pk>/', views.delete_product_view, name='product_delete'),  # ✅ Delete
    path('products/<int:pk>/', views.product_detail_view, name='product_detail'),  # ✅ Detail
    path('products/reorder/<int:id>/', views.product_reorder, name='product_reorder'),


    #Customer Queries

    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer_view, name='add_customer'),
    path('customers/edit/<int:pk>/', views.edit_customer_view, name='edit_customer'),
    path('customers/delete/<int:pk>/', views.delete_customer_view, name='delete_customer'),
    path('customers/<int:pk>/', views.customer_detail_view, name='customer_detail'),


    #Invoice Queries
    path('invoices/', views.invoice_list, name='invoice_list'),       # 🧾 Invoice List
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:invoice_id>/edit/', views.edit_invoice, name='edit_invoice'),
    path('invoice/<int:pk>/pdf/', views.invoice_pdf_view, name='invoice_pdf') ,
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:invoice_id>/mark-paid/', views.mark_invoice_paid, name='mark_invoice_paid'),
    path('invoice/<int:invoice_id>/delete/', views.delete_invoice, name='delete_invoice'),




    path('sales/update/<int:sale_id>/', views.update_sale_view, name='update_sale'),
    path('sales/delete/<int:sale_id>/',views.delete_sale, name='delete_sale'),
    path('sale/', views.create_sale_view, name='create_sale'),  # ✅ Match view name          # 🛒 Create Sale
    path('sales/', views.sale_list_view, name='sale_list'),           # 📈 Sales List
    path('sales/export/', views.export_sales_csv, name='export_sales_csv'),

]





    


