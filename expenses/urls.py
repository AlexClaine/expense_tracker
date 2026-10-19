from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("expense/<uuid:expense_id>/edit/", views.edit_expense_view, name="edit_expense"),
    path("expense/<uuid:expense_id>/delete/", views.delete_expense_view, name="delete_expense"),

]
