from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("auctions/<int:bidid>", views.listingpage, name="listingpage"),
    path("watchlist/<str:username>", views.watchlistpage, name = "watchlistpage"),
    path("added", views.addwatchlist, name = "addwatchlist"),
    path("delete", views.deletewatchlist, name = "deletewatchlist"),
    path("bidlist", views.bid, name="bid"),
    path("comments", views.allcomments, name="allcomments"),
    path("win_ner", views.win_ner, name="win_ner"),
    path("winnings", views.winnings, name="winnings"),
    path("cat_list", views.cat_list, name="cat_list"),
    path("categories/<str:category_name>", views.cat, name="cat"),
    path("profile", views.profile, name='profile'),
    path("order/<int:bid_id>/", views.order, name='order'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('download_invoice/<int:orderID>/<int:bidID>/', views.download_invoice_view, name='download_invoice'),
    path('already_ordered/', already_ordered, name='already_ordered'),
]

