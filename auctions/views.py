from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from .models import *
from django.core.mail import send_mail
import random
import string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .models import Order, Bid

def generate_random_password():
    # Generate a random password of length 8
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse("Error rendering PDF", status=400)


def download_invoice_view(request, orderID, bidID):
    try:
        # Логика получения данных для инвойса
        print("Order ID:", orderID)
        print("Bid ID:", bidID)
        order = get_object_or_404(Order, id=orderID)
        bid = get_object_or_404(Bid, id=bidID)

        mydict = {
            'orderDate': order.order_date,
            'username': request.user,
            'customerEmail': order.email,
            'shipmentAddress': order.address,
            'orderStatus': "Processing",
            'bidAmount': bid.bid_amount,
        }

        # Отправка данных в шаблон и рендеринг
        return render(request, 'auctions/download_invoice.html', mydict)
    except Exception as e:
        # Логгирование ошибки или вывод в консоль для отладки
        print(f"Error in download_invoice_view: {e}")
        # Возвращение HttpResponse с информацией об ошибке
        return HttpResponse("Error processing your request", status=500)


def already_ordered(request):
    return render(request, 'auctions/already_ordered.html')

def order(request, bid_id):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        address = request.POST.get('address')
        name = request.POST.get('name')
        email = request.POST.get('email')
        bid_amnt = request.POST.get('bid_amnt')

        existing_order = Order.objects.filter(product_name=product_name, user=request.user)

        if existing_order.exists():
            return redirect('already_ordered')

        order = Order.objects.create(
            user=request.user,
            product_name=product_name,
            address=address,
            name=name,
            email=email,
        )
        order.save()

        bid = Bid.objects.create(
            user=request.user,
            listing_id=bid_id,  # Change from listingid to listing_id
            bid_amount=bid_amnt,
        )
        bid.save()

        return redirect('my_orders')

    bid = auctionlist.objects.get(pk=bid_id)
    return render(request, 'auctions/order.html', {'bid_id': bid_id, 'bid': bid})






def my_orders(request):
    user_orders = Order.objects.filter(user=request.user)

    # Добавим принты для отладки
    print("User Orders:", user_orders)

    return render(request, 'auctions/my_orders.html', {'user_orders': user_orders})





def index(request):
    return render(request, "auctions/index.html", {
        "a1": auctionlist.objects.filter(active_bool=True),
    })


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

@login_required(login_url='login')
def profile(request):
    return render(request, "auctions/profile.html", {
        "user": request.user
    })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = generate_random_password()
        send_mail(
            'Confirmation',
            f'Your password is: {password}',
            'settings.EMAIL_HOST_USER',
            [email],
            fail_silently=False)

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            user = authenticate(request, username=username, password=password)
            login(request, user)

            return HttpResponseRedirect(reverse("logout"))
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })

    return render(request, "auctions/register.html")


@login_required(login_url='login')
def create(request):
    if request.method == "POST":
        m = auctionlist()
        m.user = request.user.username
        m.title = request.POST["create_title"]
        m.desc = request.POST["create_desc"]
        m.starting_bid = request.POST["create_initial_bid"]
        m.image_url = request.POST["img_url"]
        m.category = request.POST["category"]
        # m = auctionlist(title = title, desc=desc, starting_bid = starting_bid, image_url = image_url, category = category)
        m.save()
        return redirect("index")
    return render(request, "auctions/create.html")


def listingpage(request, bidid):
    biddesc = auctionlist.objects.get(pk=bidid, active_bool=True)
    bids_present = bids.objects.filter(listingid=bidid)

    return render(request, "auctions/listingpage.html", {
        "list": biddesc,
        "comments": comments.objects.filter(listingid=bidid),
        "present_bid": minbid(biddesc.starting_bid, bids_present),
    })


@login_required(login_url='login')
def watchlistpage(request, username):
    # present_w = watchlist.objects.get(user = "username")
    list_ = watchlist.objects.filter(user=username)
    return render(request, "auctions/watchlist.html", {
        "user_watchlist": list_,
    })


@login_required(login_url='login')
def addwatchlist(request):
    nid = request.GET["listid"]

    # below line of code will select a table of watchlist that has my name, then
    # when we loop in this watchlist, there r two fields present, to browse watch_list
    # watch_list.id == auctionlist.id, similar for all

    list_ = watchlist.objects.filter(user=request.user.username)

    # when you below line, you shld convert id to int inorder to compare or else == wont work

    for items in list_:
        if int(items.watch_list.id) == int(nid):
            return watchlistpage(request, request.user.username)

    newwatchlist = watchlist(watch_list=auctionlist.objects.get(pk=nid), user=request.user.username)
    newwatchlist.save()
    # this message remains untill u reload
    messages.success(request, "Item added to watchlist")

    return listingpage(request, nid)


@login_required(login_url='login')
def deletewatchlist(request):
    rm_id = request.GET["listid"]
    list_ = watchlist.objects.get(pk=rm_id)

    # this message remains untill u reload
    messages.success(request, f"{list_.watch_list.title} is deleted from your watchlist.")
    list_.delete()

    # you cannot call a fuction  from views as a return value
    return redirect("index")


# this function returns minimum bid required to place a user's bid
def minbid(min_bid, present_bid):
    for bids_list in present_bid:
        if min_bid < int(bids_list.bid):
            min_bid = int(bids_list.bid)
    return min_bid


@login_required(login_url='login')
def bid(request):
    bid_amnt = request.GET["bid_amnt"]
    list_id = request.GET["list_d"]
    bids_present = bids.objects.filter(listingid=list_id)
    startingbid = auctionlist.objects.get(pk=list_id)
    min_req_bid = startingbid.starting_bid
    min_req_bid = minbid(min_req_bid, bids_present)

    if int(bid_amnt) > int(min_req_bid):
        mybid = bids(user=request.user.username, listingid=list_id, bid=bid_amnt)
        mybid.save()
        messages.success(request, "Bid Placed")
        return redirect("index")

    messages.warning(request, f"Sorry, {bid_amnt} is less. It should be more than {min_req_bid}$.")
    return listingpage(request, list_id)


# shows comments made by different user and allows to add comments
@login_required(login_url='login')
def allcomments(request):
    comment = request.GET["comment"]
    username = request.user.username
    list_id = request.GET["listid"]
    new_comment = comments(user=username, comment=comment, listingid=list_id)
    new_comment.save()
    return listingpage(request, list_id)


# shows message abt winner when bid is closed
def win_ner(request):
    bid_id = request.GET["listid"]
    bids_present = bids.objects.filter(listingid=bid_id)
    biddesc = auctionlist.objects.get(pk=bid_id, active_bool=True)
    max_bid = minbid(biddesc.starting_bid, bids_present)
    try:
        # checks if anyone other than list_owner win the bid
        winner_object = bids.objects.get(bid=max_bid, listingid=bid_id)
        winner_obj = auctionlist.objects.get(id=bid_id)
        win = winner(bid_win_list=winner_obj, user=winner_object.user)
        winners_name = winner_object.user

    except:
        # if no-one placed a bid, and if bid is closed by list_owner, owner wins the bid
        winner_obj = auctionlist.objects.get(starting_bid=max_bid, id=bid_id)
        win = winner(bid_win_list=winner_obj, user=winner_obj.user)
        winners_name = winner_obj.user

    # Check Django Documentary for Updating attributes based on existing fields.
    biddesc.active_bool = False
    biddesc.save()

    # saving winner details
    win.save()
    messages.success(request, f"{winners_name} won {win.bid_win_list.title}.")
    return redirect("index")


# checks winner
def winnings(request):
    try:
        your_win = winner.objects.filter(user=request.user.username)
    except:
        your_win = None

    return render(request, "auctions/winnings.html", {
        "user_winlist": your_win,
    })


# shows lists that are present in a specific category
def cat(request, category_name):
    category = auctionlist.objects.filter(category=category_name)
    return render(request, "auctions/index.html", {
        "a1": category,
    })


# shows all categories in which object is listed
def cat_list(request):
    # unlike filter that takes a values of object_name in model, to
    # display objectname use .values('name of section from your object')
    # and when you add distinct() along with it
    # it shows only unique names, omits duplicates

    category_present = auctionlist.objects.values('category').distinct()
    return render(request, "auctions/category.html", {
        "cat_list": category_present,
    })