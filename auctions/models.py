from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"


class Category(models.Model):
    name = models.CharField(max_length=32, null=False, blank=False)
    image = models.URLField(null=True, blank=True)

    @property
    def url(self):
        return "-".join(self.name.split(" "))

    def __str__(self):
        return f"{self.name}"


class Listing(models.Model):
    creator = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="listings", null=True, blank=True
    )
    title = models.CharField(max_length=150, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    price = models.IntegerField(null=False, blank=False)
    image = models.URLField(null=False, blank=False)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=True, blank=True
    )
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    value = models.IntegerField(null=False, blank=False)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, null=False, blank=False, related_name="bids"
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.value} on {self.listing} by {self.bidder}"


class Comment(models.Model):
    content = models.TextField(max_length=120, null=False, blank=False)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="comments", null=True, blank=True
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content}\n by {self.user} on {self.listing}"


class Watchlist(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="watchlist",
        null=False,
        blank=False,
    )

    def __str__(self):
        return f"{self.user} | {self.listing}"
