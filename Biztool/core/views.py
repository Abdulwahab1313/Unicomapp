from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from .models import Wallet, BusinessProfile, Receipt
from .forms import BusinessProfileForm, ReceiptForm, ReceiptItemFormSet

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.forms import UserCreationForm

from decimal import Decimal
from .models import Transaction




@login_required
def dashboard(request):
    # If profile not filled, redirect to profile page
    profile = getattr(request.user,"businessprofile", None)
    if profile is None or not profile.brand_name:
        return redirect("create_profile")
    wallet = request.user.wallet
    return render(request, "core/dashboard.html", {"wallet": wallet})


@login_required
def create_profile(request):
    profile = request.user. businessprofile
    if request.method == "POST":
        form = BusinessProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = BusinessProfileForm(instance=profile)

    return render(request, "core/create_profile.html", {"form": form})


@login_required
def create_receipt(request):
    wallet = Wallet.objects.get(user=request.user)
    profile = BusinessProfile.objects.get(user=request.user)

    if request.method == "POST":
        form = ReceiptForm(request.POST)
        formset = ReceiptItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():

            if wallet.balance < 20:
                messages.error(request, "Insufficient balance")
                return redirect("dashboard")

            wallet.balance -= 20
            wallet.save()

            receipt = form.save(commit=False)
            receipt.user = request.user
            receipt.save()

            items = formset.save(commit=False)
            total_amount = 0

            for item in items:
                if item.product_name:
                    item.receipt = receipt
                    item.save()
                    total_amount += item.quantity * item.price

            # Generate PDF
            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = "attachment; filename=receipt.pdf"

            doc = SimpleDocTemplate(response)
            elements = []
            styles = getSampleStyleSheet()

            # Brand info
            elements.append(Paragraph(profile.brand_name, styles["Title"]))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph(f"Address:{profile.location}", styles["Normal"]))
            elements.append(Paragraph(f"Email:{profile.email}", styles["Normal"]))
            elements.append(Paragraph(f"phone:{profile.phone_number}", styles ["Normal"]))
            elements.append(Spacer(1, 0.3 * inch))

            # Customer info
            elements.append(Paragraph(f"Customer: {receipt.customer_name}", styles["Normal"]))
            elements.append(Spacer(1, 0.3 * inch))

            # Items table
            data = [["Product", "Qty", "Price", "Description", "Total"]]
            for item in receipt.items.all():
                data.append([
                    item.product_name,
                    item.quantity,
                    str(item.price),
                    item.description if item.description else"",
                    str(item.quantity * item.price)
                ])
            data.append(["", "", "Grand Total", str(total_amount)])

            table = Table(data)
            table.setStyle([("GRID", (0,0), (-1,-1), 1, colors.black)])
            elements.append(table)

            doc.build(elements)
            return response

    else:
        form = ReceiptForm()
        formset = ReceiptItemFormSet()

    return render(request, "core/create_receipt.html", {
        "form": form,
        "formset": formset
    })


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "core/login.html", {"form": form})


@login_required
def user_logout(request):
    logout(request)
    return redirect("login")



def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "core/register.html", {"form": form})




@login_required
def fund_wallet(request):
    if request.method == "POST":
        amount = request.POST.get("amount")

        if amount:
            wallet = request.user.wallet
            wallet.balance += Decimal(amount)
            wallet.save()

            Transaction.objects.create(
                user=request.user,
                amount=amount
            )

            return redirect("dashboard")

    return render(request, "core/fund_wallet.html")


import requests
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse


def initialize_payment(request):
    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": request.user.email,
        "amount": 2000,  # 20 naira = 2000 kobo
        "callback_url": "http://127.0.0.1:8000/payment/verify/"
    }

    response = requests.post(url, json=data, headers=headers)
    res_data = response.json()

    if res_data["status"]:
        return redirect(res_data["data"]["authorization_url"])
    else:
        return JsonResponse(res_data)


# URL
from django.urls import path
from .views import initialize_payment

urlpatterns = [
    path("pay/", initialize_payment, name="pay"),
]




