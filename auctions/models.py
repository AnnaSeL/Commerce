from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError

class User(AbstractUser):
    listings = models.ManyToManyField('Listing', blank=True, related_name="listings")

class Listing(models.Model):
    CATEGORIES_CHOICES = [
        ('Fashion', 'Fashion'),
        ('Toys', 'Toys'),
        ('Electronics', 'Electronics'),
        ('Home', 'Home'),
        ('Sports', 'Sports'),
        ('Beauty', 'Beauty'),
        ('Health', 'Health'),
    ]
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=250, blank=True)
    price = models.FloatField()
    image = models.CharField(max_length=200, blank=True)
    category = models.CharField(
        max_length=11,
        choices=CATEGORIES_CHOICES,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    open = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="winner")

    def __str__(self):
        return self.title


class Bid(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f'{self.amount} by {self.owner}'
    
    def clean(self):
        if self.amount < self.listing.price:
            raise ValidationError("Bid amount must be at least the listing's price.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f'By {self.author} on {self.listing}'