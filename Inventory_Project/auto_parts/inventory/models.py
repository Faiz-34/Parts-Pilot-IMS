from django.db import models
from decimal import Decimal

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


from decimal import Decimal
from django.db import models

class Sale(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=False)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=False)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    product_name = models.CharField(max_length=100, blank=True, null=True)

    phone = models.CharField(max_length=15, blank=True)

    quantity_sold = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'))
    cash_received = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    status = models.CharField(
        max_length=10,
        choices=[('Pending', 'Pending'), ('Invoiced', 'Invoiced')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ Correct indentation here
    def save(self, *args, **kwargs):
        # store snapshot of names at time of sale
        if self.customer:
            self.customer_name = self.customer.name
        elif not self.customer_name:
            self.customer_name = "Deleted Customer"

        if self.product:
            self.product_name = self.product.name
        elif not self.product_name:
            self.product_name = "Deleted Product"

        # calculate total price with discount and GST
        base = self.unit_price * self.quantity_sold
        after_discount = base - (base * self.discount / 100)
        gst_amount = after_discount * self.gst / 100
        self.total_price = after_discount + gst_amount

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name or 'No Product'} - {self.customer_name or 'No Customer'}"


from decimal import Decimal
from django.db import models

class Invoice(models.Model):
    sale = models.OneToOneField('Sale', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice')
    invoice_no = models.CharField(max_length=20, unique=True, blank=True, null=True)

    customer_name = models.CharField(max_length=100, blank=True, null=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)

    override_product_name = models.CharField(max_length=150, blank=True, null=True)
    override_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    override_quantity = models.PositiveIntegerField(default=1)

    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'))
    cash_received = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    override_balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
        ('Partial', 'Partial'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # ✅ Check if invoice is new

        # 🧩 Step 1: Copy data from Sale → Invoice only when created
        if is_new and self.sale:
            self.override_product_name = getattr(self.sale.product, 'name', '') if self.sale.product else ''
            self.override_unit_price = getattr(self.sale.product, 'price', Decimal('0.00')) if self.sale.product else Decimal('0.00')
            self.override_quantity = getattr(self.sale, 'quantity_sold', 1)
            self.customer_name = getattr(self.sale, 'customer_name', '')
            self.customer_phone = getattr(self.sale, 'customer_phone', '')

        # 🧩 Step 2: Calculate total safely
        unit_price = self.override_unit_price or Decimal('0')
        quantity = self.override_quantity or 0
        discount = self.discount or 0
        gst = self.gst or 0

        base = unit_price * quantity
        after_discount = base - (base * discount / 100)
        gst_amount = after_discount * gst / 100
        self.total = round(after_discount + gst_amount, 2)

        super().save(*args, **kwargs)

        # 🧩 Step 3: Generate invoice number after first save (so self.id is available)
        if not self.invoice_no:
            self.invoice_no = f"INV{self.id:05d}"
            super().save(update_fields=['invoice_no'])

    def __str__(self):
        return self.invoice_no or f"Invoice #{self.pk}"




class AccessCredential(models.Model):
    user_id = models.CharField(max_length=50)
    password = models.CharField(max_length=50)  # You can hash this later

    def __str__(self):
        return self.user_id



# models.py
class BusinessProfile(models.Model):
    name = models.CharField(max_length=100, default="Auto Parts Inventory")
    phone = models.CharField(max_length=15, default="+91-9876543210")
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name