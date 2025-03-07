from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)  # New image field
    views = models.IntegerField(default=0)
    free_views_remaining = models.IntegerField(default=100)  # 100 free views
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['views', 'free_views_remaining']),
        ]
        
    def __str__(self):
        return self.title

class Package(models.Model):
    name = models.CharField(max_length=50)  # e.g., BID @49, BID @99
    price = models.DecimalField(max_digits=6, decimal_places=2)
    extra_views = models.IntegerField()  # Views granted by package

    def __str__(self):
        return self.name

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)  # Credits (max 1,00,000)

    def save(self, *args, **kwargs):
        if self.balance > 100000:
            self.balance = 100000
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} ₹ {self.balance}"

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.IntegerField()  # Positive for earn, negative for spend
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.Wallet} {self.amount}"
    
