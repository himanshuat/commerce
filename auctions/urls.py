from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("newlisting", views.newlisting, name="newlisting"),
    path("comment/<int:id>", views.comment, name="comment"),
    path("bid/<int:id>", views.bid, name="bid"),
    path("close-auction/<int:id>", views.close_auction, name="close_auction"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:url>", views.category, name="category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("update-watchlist/<int:id>", views.update_watchlist, name="update_watchlist")
]
