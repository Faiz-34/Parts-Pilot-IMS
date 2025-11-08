# yourapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

# Import inside function to avoid circular import problems
@receiver(post_save, sender='inventory.Sale')
def create_invoice_for_sale(sender, instance, created, **kwargs):
    if not created:
        return

    # Import models here to avoid circular import at module level
    from .models import Invoice

    # If an invoice for this sale already exists, do nothing
    if Invoice.objects.filter(sale=instance).exists():
        return

    Invoice.objects.create(
        sale=instance,
        customer_name=instance.customer.name if instance.customer else "",
        customer_phone=instance.phone or (instance.customer.phone if instance.customer else ""),
        override_product_name=instance.product.name if instance.product else "",
        override_unit_price=instance.unit_price or 0,
        override_quantity=instance.quantity_sold or 1,
        discount=instance.discount or 0,
        gst=instance.gst or 0,
        cash_received=instance.cash_received or 0,
    )
