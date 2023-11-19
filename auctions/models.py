# models.py

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class auctionlist(models.Model):
    user = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    desc = models.TextField()
    starting_bid = models.IntegerField()
    image_url = models.CharField(max_length=228, default=None, blank=True, null=True)
    category = models.CharField(max_length=64)
    active_bool = models.BooleanField(default=True)


class bids(models.Model):
    user = models.CharField(max_length=30)
    listingid = models.IntegerField()
    bid = models.IntegerField()


class comments(models.Model):
    user = models.CharField(max_length=64)
    comment = models.TextField()
    listingid = models.IntegerField()


class watchlist(models.Model):
    watch_list = models.ForeignKey(auctionlist, on_delete=models.CASCADE)
    user = models.CharField(max_length=64)


class winner(models.Model):
    bid_win_list = models.ForeignKey(auctionlist, on_delete=models.CASCADE)
    user = models.CharField(max_length=64, default=None)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    address = models.TextField()
    name = models.CharField(max_length=255)
    email = models.EmailField()

    # Добавляем поле ForeignKey для связи с Bid
    bid = models.ForeignKey(bids, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Order #{self.id} - {self.product_name} - {self.user.username}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    address = models.TextField()
    name = models.CharField(max_length=255)
    email = models.EmailField()