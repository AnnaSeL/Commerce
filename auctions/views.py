from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core import validators

from .models import User, Listing, Bid, Comment

class NewListingForm(forms.Form):
    CATEGORIES_CHOICES = [
        ('Fashion', 'Fashion'),
        ('Toys', 'Toys'),
        ('Electronics', 'Electronics'),
        ('Home', 'Home'),
        ('Sports', 'Sports'),
        ('Beauty', 'Beauty'),
        ('Health', 'Health'),
    ]
    title = forms.CharField(max_length=40)
    description = forms.CharField(max_length=250, required=False)
    price = forms.FloatField()
    image = forms.CharField(max_length=200, initial="", required=False)
    category = forms.ChoiceField(choices=CATEGORIES_CHOICES)


class NewBidForm(forms.Form):
    amount = forms.FloatField()

    def __init__(self, *args, listing=None, **kwargs):
        super().__init__(*args, **kwargs)
        if listing:
            self.fields['amount'].widget.attrs['min'] = listing.price+0.1
            

class NewCommentForm(forms.Form):
    content = forms.CharField(max_length=200, label="", widget=forms.TextInput(attrs={'placeholder':'Add a comment...'}))


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


@login_required
def create(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            price = form.cleaned_data["price"]
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]
            listing = Listing.objects.create(title=title, description=description, price=price, image=image, category=category, owner = request.user)
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })
    return render(request, "auctions/create.html", {
        "form": NewListingForm()
    })


def categories(request):
    categories = [category[0] for category in Listing.CATEGORIES_CHOICES]
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category(request, name):
    listings = Listing.objects.filter(category=name)
    return render(request, "auctions/category.html", {
        "category": name,
        "listings": listings
    })


@login_required
def comment(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST" and request.user.is_authenticated and listing.open==True:
        form = NewCommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            comment = Comment.objects.create(author=request.user, content=content, listing=listing)
            comment.save()
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    form_comment = NewCommentForm()
    form_bid = NewBidForm(listing=listing)

    if request.method == "POST" and request.user.is_authenticated and listing.open:
        if "post_comment" in request.POST:
            form_comment = NewCommentForm(request.POST)
            if form_comment.is_valid():
                content = form_comment.cleaned_data["content"]
                comment = Comment.objects.create(author=request.user, content=content, listing=listing)
                comment.save()
                return HttpResponseRedirect(reverse("listing", args=[listing_id]))
            else:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "form_bid": form_bid,
                    "form_comment": form_comment,
                    "bids": Bid.objects.filter(listing=listing),
                    "comments": Comment.objects.filter(listing=listing),
                    "message": "Invalid comment."
                })
        
        elif "place_bid" in request.POST:
            form_bid = NewBidForm(request.POST, listing=listing)
            if form_bid.is_valid():
                amount = form_bid.cleaned_data['amount']
                if amount > listing.price:
                    bid = Bid.objects.create(owner=request.user, amount=amount, listing=listing)
                    bid.save()                
                    listing.price = amount
                    listing.save(update_fields=["price"])
                    return HttpResponseRedirect(reverse("listing", args=[listing_id]))
                else:
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "form_bid": form_bid,
                        "form_comment": form_comment,
                        "bids": Bid.objects.filter(listing=listing),
                        "comments": Comment.objects.filter(listing=listing),
                        "message": "Minimun value of the bid is current price."
                    })   
            else:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "form_comment": form_comment,
                    "form_bid": form_bid,
                    "bids": Bid.objects.filter(listing=listing),
                    "comments": Comment.objects.filter(listing=listing),
                    "message": "Invalid bid."
                })
    elif not listing.open:
        return render(request, "auctions/listing.html",{
            "listing": listing,
            "form_bid": form_bid,
            "form_comment": form_comment,
            "bids": Bid.objects.filter(listing=listing),
            "comments": Comment.objects.filter(listing=listing),
            "winner": listing.winner
        })
    return render(request, "auctions/listing.html",{
        "listing": listing,
        "form_bid": form_bid,
        "form_comment": form_comment,
        "bids": Bid.objects.filter(listing=listing),
        "comments": Comment.objects.filter(listing=listing)
    })


@login_required
def close_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if listing.open==True and listing.owner == request.user:
        listing.open = False
        if Bid.objects.filter(listing=listing):
            listing.winner = Bid.objects.filter(listing=listing).last().owner
        listing.save(update_fields=["open", "winner"])
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required
def won_lots(request):
    listings = Listing.objects.all().filter(winner=request.user)
    return render(request, "auctions/won_lots.html", {
        "listings": listings
    })


@login_required
def watchlist(request):
    listings = request.user.listings.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


@login_required
def add_to_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user = request.user
    if listing not in user.listings.all():
        user.listings.add(listing)
    else:
        user.listings.remove(listing)
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
