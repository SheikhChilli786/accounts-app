from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import ProductConversion,Product,Transaction,Party

@receiver(pre_save,sender=ProductConversion)
def adjust_product_quantity_on_update(sender,instance,**kwargs):
    if instance.pk:
        previous_order = ProductConversion.objects.get(pk=instance.pk)
        quantity_difference = previous_order.quantity - int(instance.quantity)
        instance.product.quantity += quantity_difference
        instance.product.save()
    else:
        pass

@receiver(post_save,sender=ProductConversion)
def update_product_quantity_on_save(sender, instance, created, **kwargs):
    if created:
        instance.product.quantity -= int(instance.quantity)
        instance.product.save()

@receiver(post_delete, sender=ProductConversion)
def restore_product_quantity_on_delete(sender, instance, **kwargs):
    # Restore the product quantity when an order is deleted
    instance.product.quantity += int(instance.quantity)
    instance.product.save()

@receiver(post_save,sender=Transaction)
def call_get_balance_when_transaction_saved(sender,instance,created,**kwargs):
    if instance.party:
        instance.party.balance = instance.party.get_balance()
        instance.party.save()

@receiver(post_delete,sender=Transaction)
def call_get_balance_when_transaction_deleted(sender,instance,**kwargs):
    if instance.party:
        instance.party.balance = instance.party.get_balance()
        instance.party.save()