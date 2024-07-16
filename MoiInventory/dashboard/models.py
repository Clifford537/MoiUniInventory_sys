from django.db import models

class Store(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    item_name = models.CharField(max_length=255)
    item_description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    remarks = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.item_name} ({self.store.name})'

class Transaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50)  # 'issue' or 'receive'
    quantity = models.PositiveIntegerField()
    date = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.transaction_type} - {self.product.item_name} ({self.quantity})'
