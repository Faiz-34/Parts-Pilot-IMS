import calendar
from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from auto_parts import settings
from .models import Product, Customer, Sale, Invoice
from django.db.models import Sum, Count, F , Q
from .forms import ProductForm,CustomerForm,CreateSaleForm
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from .pdf import render_to_pdf
from django.contrib.auth.forms import UserCreationForm
from decimal import Decimal, InvalidOperation
import uuid
from django.template.loader import get_template
from xhtml2pdf import pisa
from inventory.models import AccessCredential
from django.contrib import messages


def access_gate_view(request):
    message = ''

    if request.method == 'POST':
        user_id = request.POST.get('user_id', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            cred = AccessCredential.objects.get(user_id__iexact=user_id, password=password)
            
            # ✅ Session flags set karo
            request.session['authenticated'] = True
            request.session['user_id'] = cred.user_id
            
            return redirect('dashboard')
        except AccessCredential.DoesNotExist:
            message = '❌ Invalid credentials. Please try again.'

    return render(request, 'access_gate.html', {'message': message})




def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def intro_view(request):
    return render(request, 'intro.html')


from django.db.models import Sum, Count, F
from django.utils.timezone import now
from datetime import timedelta
import calendar

def dashboard_view(request):
    # 🔐 Access Gate Check
    if not request.session.get('authenticated'):
        return redirect('access_gate')

    # 📊 Dashboard Metrics
    total_stock = Product.objects.aggregate(total=Sum('quantity'))['total'] or 0
    total_revenue = Sale.objects.aggregate(total=Sum('total_price'))['total'] or 0
    total_sales = Sale.objects.count()

    current_month = now().month
    current_year = now().year

    revenue_this_month = Sale.objects.filter(
    created_at__month=current_month,
    created_at__year=current_year
      ).aggregate(total=Sum('total_price'))['total'] or 0
    monthly_sales = Sale.objects.filter(created_at__month=current_month).count()

    # 📆 Monthly Sales Data for Chart
    months = [calendar.month_abbr[i] for i in range(1, 13)]
    monthly_sales_data = []
    for i in range(1, 13):
        count = Sale.objects.filter(created_at__year=current_year, created_at__month=i).count()
        monthly_sales_data.append(count)

    # 📦 Stock & Invoice
    low_stock = Product.objects.filter(quantity__lt=F('reorder_level'))
    low_stock_count = low_stock.count()

    recent_sales = Sale.objects.filter(created_at__gte=now() - timedelta(days=7)).order_by('-created_at')[:10]

    top_customers = Customer.objects.annotate(
        total_orders=Count('sale'),
        total_spent=Sum('sale__total_price')
    ).order_by('-total_spent')[:5]

    paid_invoice_count = Invoice.objects.filter(status='Paid').count()
    unpaid_invoice_count = Invoice.objects.filter(status='Unpaid').count()

    # 📦 Final Context
    context = {
        'total_stock': total_stock,
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'revenue_this_month': revenue_this_month,
        'monthly_sales': monthly_sales,
        'months': months,
        'monthly_sales_data': monthly_sales_data,
        'low_stock': low_stock,
        'low_stock_count': low_stock_count,
        'recent_sales': recent_sales,
        'top_customers': top_customers,
        'paid_invoices': paid_invoice_count,
        'unpaid_invoices': unpaid_invoice_count,
        'paid_invoice_count': paid_invoice_count,
        'unpaid_invoice_count': unpaid_invoice_count,
    }

    return render(request, 'dashboard.html', context)


from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from inventory.models import AccessCredential


# 📊 Dashboard View (Simple)

def dashboard(request):
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    total_sales = Sale.objects.count()
    total_revenue = Sale.objects.aggregate(total=Sum('total_price'))['total'] or 0
    current_year = timezone.now().year
    months = [calendar.month_abbr[i] for i in range(1,13)]
    monthly_revenue_data = []

    for i in range(1,13):
        total = Sale.objects.filter(date__year=current_year, date__month=i).aggregate(total=Sum('total_price'))['total'] or 0
        monthly_revenue_data.append(total)

    # 🔹 Recent Invoices (already present)
    recent_invoices = Invoice.objects.order_by('-date')[:5]

    # ✅ Recent Sales Table (latest 5 sales)
    recent_sales = Sale.objects.select_related('customer', 'product').order_by('-date')[:5]

    return render(request, 'dashboard.html', {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'recent_invoices': recent_invoices,
        'recent_sales': recent_sales,      # ✅ passed to template
        'months': months,
        'monthly_revenue_data': monthly_revenue_data,
        'revenue_this_month': Sale.objects.filter(date__month=timezone.now().month).aggregate(Sum('total_price'))['total_price__sum'] or 0,
    })                                 
     

# ➕ Add Product View
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # ✅ Redirect to product list or success page
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
import uuid
from .models import Product
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
import uuid
from .models import Product
from decimal import Decimal
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product  # Make sure your Product model is imported

def edit_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        sku = request.POST.get('sku', '').strip()
        price = request.POST.get('price', '0')
        quantity = request.POST.get('quantity', '0')
        reorder_level = request.POST.get('reorder_level', '0')

        if not name:
            messages.error(request, "❌ Product name is required.")
            return render(request, 'edit_product.html', {'product': product})

        try:
            price = Decimal(price)
            quantity = int(quantity)
            reorder_level = int(reorder_level)
        except:
            messages.error(request, "❌ Invalid numeric values.")
            return render(request, 'edit_product.html', {'product': product})

        if not sku:
            sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"

        product.name = name
        product.sku = sku
        product.price = price
        product.quantity = quantity
        product.reorder_level = reorder_level
        product.save()

        messages.success(request, "✅ Product updated successfully!")
        return redirect('product_list')

    return render(request, 'edit_product.html', {'product': product})

def delete_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('product_list')


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})



# 📦 Product List View
def product_list(request):
    products = Product.objects.all()
    return render(request, "product_list.html", {"products": products})

# 👥 Customer List View
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "customer_list.html", {"customers": customers})

def add_customer_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'add_customer.html', {'form': form})


def edit_customer_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        return redirect('customer_list')
    return render(request, 'edit_customer.html', {'form': form, 'customer': customer})


def delete_customer_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('customer_list')

def customer_detail_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customer_detail.html', {'customer': customer})


# 🧾 Invoice List View



def invoice_list(request):
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')

    # 🔹 Efficient Query — prefetch related models
    invoices = Invoice.objects.select_related('sale__customer', 'sale__product').order_by('-created_at')

    # 🔹 Apply Status Filter
    if status_filter:
        invoices = invoices.filter(status__iexact=status_filter)

    # 🔹 Apply Search Filter (case-insensitive)
    if query:
        invoices = invoices.filter(
            Q(invoice_no__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(customer_phone__icontains=query) |
            Q(override_product_name__icontains=query) |
            Q(sale__customer__name__icontains=query) |
            Q(sale__customer__phone__icontains=query) |
            Q(sale__product__name__icontains=query)
        )

    context = {
        'invoices': invoices,
        'status_filter': status_filter,
        'query': query,
    }

    return render(request, 'invoice_list.html', context)

# 🧾 Invoice Detail View
from .models import BusinessProfile

def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    profile = BusinessProfile.objects.first()
    sale = getattr(invoice, 'sale', None)

    # Prefer override fields (always exist even if sale deleted)
    product_name = invoice.override_product_name or (sale.product.name if sale and sale.product else "")
    unit_price = invoice.override_unit_price or (sale.product.price if sale and sale.product else Decimal('0.00'))
    quantity = invoice.override_quantity or (sale.quantity_sold if sale else 0)
    subtotal = unit_price * quantity

    if not sale:
        messages.info(request, "ℹ️ Sale record deleted. Showing stored invoice data.")

    return render(request, 'invoice_detail.html', {
        'invoice': invoice,
        'profile': profile,
        'sale': sale,
        'subtotal': subtotal,
        'product_name': product_name,
        'unit_price': unit_price,
        'quantity': quantity,
    })



def safe_decimal(value, default='0'):
    try:
        return Decimal(value.strip() or default)
    except:
        return Decimal(default)


def edit_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    sale = getattr(invoice, 'sale', None)
    customer = getattr(sale, 'customer', None) if sale else None
    product = getattr(sale, 'product', None) if sale else None

    if request.method == "POST":
        # ✅ Update invoice fields manually
        invoice.customer_name = request.POST.get('customer_name', '').strip()
        invoice.customer_phone = request.POST.get('customer_phone', '').strip()
        invoice.override_product_name = request.POST.get('product', '').strip()
        invoice.override_unit_price = safe_decimal(request.POST.get('price', '0'))
        invoice.override_quantity = int(request.POST.get('quantity', '1'))
        invoice.discount = safe_decimal(request.POST.get('discount', '0'))
        invoice.gst = safe_decimal(request.POST.get('gst', '0'))
        invoice.cash_received = safe_decimal(request.POST.get('cash_received', '0'))
        invoice.override_balance_due = safe_decimal(request.POST.get('balance_due', '0'))
        invoice.status = request.POST.get('status', 'Unpaid')

        # ✅ Total auto-calculate via model.save()
        invoice.save()

        messages.success(request, f"✅ Invoice {invoice.invoice_no or invoice.id} updated successfully!")
        return redirect('invoice_list')

    # ✅ Autofill fallback (if invoice fields are empty)
    context = {
        'invoice': invoice,
        'sale': sale,
        'customer': customer,
        'product': product,
        'prefilled_name': invoice.customer_name or (customer.name if customer else ''),
        'prefilled_phone': invoice.customer_phone or (customer.phone if customer else ''),
        'prefilled_product': invoice.override_product_name or (product.name if product else ''),
        'prefilled_price': invoice.override_unit_price or (product.price if product else 0),
        'prefilled_quantity': invoice.override_quantity or (sale.quantity_sold if sale else 1),
        'prefilled_total': invoice.total or invoice.total or (sale.total_price if sale else 1),
    }

    return render(request, 'edit_invoice.html', context)




def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice.delete()
    return redirect('invoice_list')

from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
import os

def invoice_pdf_view(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo.png')

    context = {
        'invoice': invoice,
        'logo_path': logo_path,
    }

    html = render_to_string('invoice_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_no}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("PDF generation failed")
    return response


# 📋 Sale List View
def sale_list_view(request):
    sales = Sale.objects.all().order_by('-id')
    return render(request, 'sale_list.html', {'sales': sales})

# ✅ Sale Success View
def sale_success(request):
    return render(request, 'sale_success.html')

from .models import Sale, Customer, Product, Invoice
from decimal import Decimal
import uuid


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Sale, Customer, Product, Invoice
from .forms import CreateSaleForm




from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Sale, Customer, Product, Invoice

def create_sale_view(request):
    if request.method == 'POST':
        # 🔹 Form data
        customer_name = request.POST.get('customer')
        product_name = request.POST.get('product_name')
        phone = request.POST.get('phone')
        quantity = int(request.POST.get('quantity') or 0)
        price = float(request.POST.get('price') or 0)
        gst = float(request.POST.get('gst') or 0)
        discount = float(request.POST.get('discount') or 0)
        cash_received = float(request.POST.get('cash_received') or 0)
        status = request.POST.get('status')

        # 🔹 Sync customer
        customer, _ = Customer.objects.get_or_create(name=customer_name, defaults={'phone': phone})

        # 🔹 Sync product with price
        product, created = Product.objects.get_or_create(name=product_name, defaults={'price': price})
        if not created and product.price is None:
            product.price = price
            product.save()

        # 🔹 Calculate total
        subtotal = price * quantity
        discounted = subtotal - (subtotal * discount / 100)
        gst_amount = discounted * gst / 100
        total_price = discounted + gst_amount

        # 🔹 Create sale
        sale = Sale.objects.create(
            customer=customer,
            product=product,
            phone=phone,
            quantity_sold=quantity,
            unit_price=price,
            gst=gst,
            discount=discount,
            cash_received=cash_received,
            total_price=total_price,
            status=status
        )

        # 🔹 Generate invoice number
        last_invoice = Invoice.objects.order_by('id').last()
        new_number = 1
        if last_invoice and last_invoice.invoice_no and last_invoice.invoice_no.startswith("INV"):
            try:
                new_number = int(last_invoice.invoice_no.replace("INV", "")) + 1
            except:
                new_number = 1

        # 🔹 Create or reuse existing invoice
        invoice, created = Invoice.objects.get_or_create(
            sale=sale,
            defaults={
                'invoice_no': f"INV{new_number:04d}",
                'customer_name': customer.name,
                'customer_phone': phone,
                'override_product_name': product.name,
                'override_unit_price': price,
                'override_quantity': quantity,
                'discount': discount,
                'gst': gst,
                'cash_received': cash_received,
                'total_price': total_price,
                'status': 'Unpaid',
            }
        )

        if created:
            messages.success(request, f"✅ Sale created successfully! Invoice: {invoice.invoice_no}")
        else:
            messages.warning(request, f"⚠️ Invoice already existed for this sale: {invoice.invoice_no}")

        return redirect('sale_list')

    return render(request, 'create_sale.html')




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
import uuid
from .models import Sale, Customer, Product

def update_sale_view(request, sale_id):
    sale = get_object_or_404(Sale, pk=sale_id)

    if request.method == "POST":
        customer_name = request.POST.get('customer', '').strip()
        product_name = request.POST.get('product', '').strip()
        status_value = request.POST.get('status', '').strip()

        try:
            quantity_sold = int(request.POST.get('quantity_sold', 0))
        except ValueError:
            quantity_sold = 0

        try:
            unit_price = Decimal(request.POST.get('price', '0'))
        except:
            unit_price = Decimal('0')

        # 🔍 Lookup or Create Customer
        customer = Customer.objects.filter(name__iexact=customer_name).first()
        if not customer:
            customer = Customer.objects.create(name=customer_name)

        # 🔍 Lookup or Create Product
        product = Product.objects.filter(name__iexact=product_name).first()
        if not product:
            sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
            product = Product.objects.create(name=product_name, price=unit_price, sku=sku)
        else:
            # ✅ Update product price if changed
            if product.price != unit_price:
                product.price = unit_price
                product.save()

        # 🔐 Stock check (optional)
        if hasattr(product, 'stock') and quantity_sold > product.stock:
            messages.error(request, f"❌ Not enough stock for {product.name}.")
        else:
            # ✅ Update Sale
            sale.customer = customer
            sale.product = product
            sale.quantity_sold = quantity_sold
            sale.status = status_value if status_value in ['Pending', 'Invoiced'] else 'Pending'
            sale.total_price = unit_price * quantity_sold
            sale.save()

            messages.success(request, "✅ Sale updated successfully!")
            return redirect('sale_list')

    return render(request, 'edit_sale.html', {'sale': sale})


def delete_sale(request, sale_id):
    sale = get_object_or_404(Sale, pk=sale_id)
    sale.delete()
    messages.success(request, "✅ Sale deleted successfully!")
    return redirect('sale_list')


# ⚠️ Low Stock View
def low_stock_list_view(request):
    low_stock = Product.objects.filter(quantity__lt=F('reorder_level'))
    return render(request, 'low_stock_list.html', {'low_stock': low_stock})

def mark_invoice_paid(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice.status = 'Paid'
    invoice.save()
    return redirect('invoice_list')


import csv
def export_sales_csv(request):
    sales = Sale.objects.select_related('customer', 'product').order_by('-created_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Customer', 'Product', 'Quantity', 'Price', 'Total'])

    for sale in sales:
        writer.writerow([
            sale.created_at.strftime('%d-%m-%Y'),
            sale.customer.name,
            sale.product.name,
            sale.quantity_sold,
            sale.product.price,
            sale.total_price
        ])

    return response

from django.shortcuts import render
from django.db.models import Q
from .models import Product, Customer, Invoice, Sale

def global_search(request):
    query = request.GET.get('q', '').strip()

    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(sku__icontains=query) |
        Q(description__icontains=query)
    )

    customers = Customer.objects.filter(
        Q(name__icontains=query) |
        Q(email__icontains=query) |
        Q(phone__icontains=query)
    )

    invoices = Invoice.objects.filter(
        Q(invoice_no__icontains=query) |
        Q(sale__customer__name__icontains=query)
    )

    sales = Sale.objects.filter(
        Q(product__name__icontains=query) |
        Q(customer__name__icontains=query)
    )

    context = {
        'query': query,
        'products': products,
        'customers': customers,
        'invoices': invoices,
        'sales': sales,
    }
    return render(request, 'global_search.html', context)


def product_reorder(request):
    # your logic here
    return render(request, 'product_reorder.html')


