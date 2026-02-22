from django.urls import path
from . import views

urlpatterns = [
    path("", views.user_login, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.create_profile, name="create_profile"),
    path("receipt/", views.create_receipt, name="create_receipt"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.register, name="register"),
    path("fund-wallet/", views.fund_wallet, name="fund_wallet"),

]

