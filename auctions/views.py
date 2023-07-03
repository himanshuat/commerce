from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import *


def index(request):
    return render(
        request,
        "auctions/index.html",
        {"listings": Listing.objects.filter(winner=None)},
    )


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def categories(request):
    return render(
        request, "auctions/categories.html", {"categories": Category.objects.all()}
    )


def category(request, url):
    name = " ".join(url.split("-"))
    category = Category.objects.get(name=name)
    return render(
        request,
        "auctions/category.html",
        {
            "category": category,
            "listings": Listing.objects.filter(category=category),
        },
    )


def listing(request, id):
    listing = Listing.objects.get(pk=id)

    if request.user.is_authenticated:
        onwatch = Watchlist.objects.filter(listing=listing, user=request.user)
    else:
        onwatch = []
    
    if len(listing.bids.all()) > 0:
        latest_bid = listing.bids.get(value=listing.price)
    else:
        latest_bid = None
    
    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listing,
            "creator": listing.creator == request.user,
            "latest_bid": latest_bid,
            "bidscount": len(listing.bids.all()),
            "comments": listing.comments.all(),
            "watchlist_text": "Remove from watchlist"
            if len(onwatch) > 0
            else "Add to watchlist",
        },
    )


@login_required(login_url="login")
def newlisting(request):
    if request.method == "POST":
        data = request.POST

        title = data["title"]
        price = data["price"]
        category = data["category"]
        image = data["image"]
        description = data["description"]

        messages = []
        if not (0 < len(title) <= 150):
            messages.append("Title: length should be 1-150 characters long")
        if price == "" or int(price) < 1:
            messages.append("Price: Required and should be a positive integer")
        if category != "" and len(Category.objects.filter(pk=category)) == 0:
            messages.append("Category: Choose a valid category")
        if not image:
            messages.append("Image Link: Required")
        if not description:
            messages.append("Description: Required")

        if len(messages) == 0:
            new_listing = Listing(
                title=title, price=int(price), image=image, description=description
            )
            if category != "":
                new_listing.category = Category.objects.get(pk=category)
            new_listing.save()

            return redirect("listing", id=new_listing.pk)
        else:
            return render(
                request,
                "auctions/newlisting.html",
                {
                    "categories": Category.objects.all(),
                    "messages": messages,
                    "data": data,
                },
            )
    else:
        return render(
            request, "auctions/newlisting.html", {"categories": Category.objects.all()}
        )


@login_required(login_url="login")
@require_POST
def comment(request, id):
    listing = Listing.objects.get(pk=id)
    comment = Comment(
        content=request.POST["content"], user=request.user, listing=listing
    )
    comment.save()
    return redirect("listing", id=id)


@login_required(login_url="login")
@require_POST
def bid(request, id):
    listing = Listing.objects.get(pk=id)
    value = int(request.POST["value"])
    listing.price = value
    listing.save()
    bid = Bid(value=value, bidder=request.user, listing=listing)
    bid.save()
    return redirect("listing", id=id)


@login_required(login_url="login")
@require_POST
def close_auction(request, id):
    listing = Listing.objects.get(pk=id)
    winning_bid = Bid.objects.filter(listing=listing, value=listing.price)[0]
    listing.winner = winning_bid.bidder
    listing.save()
    return redirect("listing", id=id)


@login_required(login_url="login")
def watchlist(request):
    watchlist = request.user.watchlist.all()
    return render(
        request,
        "auctions/watchlist.html",
        {"listings": [item.listing for item in watchlist]},
    )


@login_required(login_url="login")
@require_POST
def update_watchlist(request, id):
    listing = Listing.objects.get(pk=id)
    onwatch = Watchlist.objects.filter(listing=listing, user=request.user)

    if len(onwatch) == 0:
        add = Watchlist(listing=listing, user=request.user)
        add.save()
    else:
        onwatch.delete()

    return redirect("listing", id=id)
