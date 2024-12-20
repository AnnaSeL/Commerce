from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create/", views.create, name="create"),
    path("categories/", views.categories, name="categories"),
    path("categories/<str:name>", views.category, name="category"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("<int:listing_id>/add_to_watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("<int:listing_id>/closed", views.close_listing, name="close_listing"),
    path("won_lots/", views.won_lots, name="won_lots"),
]