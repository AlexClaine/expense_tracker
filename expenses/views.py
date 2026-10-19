from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from supabase_auth.errors import AuthApiError
from .forms import SignupForm, LoginForm, ExpenseForm
from .auth_service import register_user, login_user, logout_user
from rest_framework.exceptions import APIException
from expenses.services import (get_user_expenses, get_user_expense, refresh_supabase_session, update_expense, delete_expense,)
from .services import create_expense
from expenses.calculations import calculate_expense_totals
from expenses.currency_service import convert_expenses
import requests

# Create your views here.

@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            try:
                result = register_user(
                    form.cleaned_data["email"],
                    form.cleaned_data["password"],
                )

                if result.session:
                    request.session.cycle_key()
                    request.session["supabase_access_token"] = (
                        result.session.access_token
                    )
                    request.session["supabase_refresh_token"] = (
                        result.session.refresh_token
                    )
                    request.session["user_id"] = result.user.id
                    request.session["user_email"] = result.user.email

                    return redirect("dashboard")

                messages.success(
                    request,
                    "Account created. Check your email to confirm "
                    "your account, then sign in.",
                )
                return redirect("login")

            except AuthApiError:
                messages.error(
                    request,
                    "Registration failed. Check your details or try "
                    "signing in if you already have an account.",
                )

    else:
        form = SignupForm()

    return render(request, "auth/signup.html", {"form": form})

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            try:
                result = login_user(
                    form.cleaned_data["email"],
                    form.cleaned_data["password"],
                )

                if not result.session:
                    messages.error(
                        request,
                        "No active session was returned. Check whether "
                        "email confirmation is required.",
                    )
                else:
                    request.session.cycle_key()
                    request.session["supabase_access_token"] = (
                        result.session.access_token
                    )
                    request.session["supabase_refresh_token"] = (
                        result.session.refresh_token
                    )
                    request.session["user_id"] = result.user.id
                    request.session["user_email"] = result.user.email

                    return redirect("dashboard")

            except AuthApiError:
                messages.error(
                    request,
                    "Login failed. Check your email and password.",
                )

    else:
        form = LoginForm()

    return render(request, "auth/login.html", {"form": form})



@require_http_methods(["GET", "POST"])
def dashboard_view(request):
    access_token = request.session.get("supabase_access_token")
    user_id = request.session.get("user_id")

    if not access_token or not user_id:
        return redirect("login")

    if request.method == "POST":
        form = ExpenseForm(request.POST)

        if form.is_valid():
            try:
                create_expense(
                    access_token,
                    user_id,
                    form.cleaned_data,
                )
                messages.success(request, "Expense saved successfully!")
                return redirect("dashboard")

            except Exception as exc:
                if "JWT expired" in str(exc):
                    if refresh_supabase_session(request):
                        try:
                            create_expense(
                                request.session["supabase_access_token"],
                                user_id,
                                form.cleaned_data,
                            )
                            messages.success(
                                request, "Expense saved successfully!"
                            )
                            return redirect("dashboard")
                        except Exception as retry_exc:
                            print("EXPENSE SAVE RETRY FAILED:", repr(retry_exc))

                else:
                    print("EXPENSE SAVE FAILED:", repr(exc))

                messages.error(
                    request,
                    "Could not save the expense. Please try again.",
                )
    else:
        form = ExpenseForm()

    try:
        expenses = get_user_expenses(
            request.session["supabase_access_token"]
        )
        expenses, category_summary, currency_summary = calculate_expense_totals(expenses)
        error = None

    except Exception as exc:
        print("EXPENSE LOADING ERROR:", repr(exc))
        if "JWT expired" in str(exc):
            if refresh_supabase_session(request):
                try:
                    expenses = get_user_expenses(
                        request.session["supabase_access_token"]
                    )
                    expenses, category_summary, currency_summary = calculate_expense_totals(expenses)
                    error = None
                except Exception as retry_exc:
                    print("EXPENSE LOADING RETRY FAILED:", repr(retry_exc))
                    expenses, category_summary, currency_summary = [], {}, {}
                    error = "Could not load expenses. Please try again."
            else:
                return redirect("login")
        else:
            expenses, category_summary, currency_summary = [], {}, {}
            error = "Could not load expenses. Please try again."

    reporting_currency = request.GET.get("report_currency", "KES").upper()
    allowed_currencies = {"KES", "USD", "EUR", "GBP"}
    if reporting_currency not in allowed_currencies:
        reporting_currency = "KES"

    converted_expenses, converted_total, conversion_error = [], None, None
    try:
        converted_expenses, converted_total = convert_expenses(expenses, reporting_currency)
    except (requests.RequestException, KeyError, ValueError) as conv_exc:
        print("CURRENCY CONVERSION FAILED:", repr(conv_exc))
        conversion_error = (
            "Exchange rates are currently unavailable. "
            "Your original expenses have not been changed."
        )

    return render(
        request,
        "dashboard.html",
        {
            "user_email": request.session.get("user_email", ""),
            "expenses": expenses,
            "form": form,
            "category_summary": category_summary,
            "currency_summary": currency_summary,
            "reporting_currency": reporting_currency,
            "converted_expenses": converted_expenses,
            "converted_total": converted_total,
            "conversion_error": conversion_error,
            "error": error,
        },
    )




# def dashboard_view(request):
#     access_token = request.session.get("supabase_access_token")

#     if not access_token:
#         return redirect("login")
#     try:
#         expenses = get_user_expenses(access_token)

#         error = None
#     except Exception as exc:
#         print("EXPENSE LOADING ERROR:", repr(exc))
#     expenses = []
#     error = "Could not load expenses. Please try again."
#     return render(
#         request,
#         "dashboard.html",
#         {
#             "user_email": request.session.get("user_email", ""),
#             "expenses": expenses,
#             "error": error,
#         },
#     )

@require_http_methods(["POST"])
def logout_view(request):
    access_token = request.session.get("supabase_access_token")
    refresh_token = request.session.get("supabase_refresh_token")

    if access_token and refresh_token:
        try:
            logout_user(access_token, refresh_token)

        except Exception:
            pass
    
    request.session.flush()

    return redirect("login")



@require_http_methods(["GET", "POST"])
def edit_expense_view(request, expense_id):
    access_token = request.session.get("supabase_access_token")

    if not access_token:
        return redirect("login")

    try:
        expense = get_user_expense(access_token, expense_id)

        if expense is None:
            messages.error(request, "Expense not found.")
            return redirect("dashboard")

        if request.method == "POST":
            form = ExpenseForm(request.POST)

            if form.is_valid():
                try:
                    update_expense(
                        access_token,
                        expense_id,
                        form.cleaned_data,
                    )
                    messages.success(request, "Expense updated successfully!")
                    return redirect("dashboard")

                except Exception as exc:
                    if "JWT expired" in str(exc):
                        if refresh_supabase_session(request):
                            try:
                                update_expense(
                                    request.session["supabase_access_token"],
                                    expense_id,
                                    form.cleaned_data,
                                )
                                messages.success(
                                    request, "Expense updated successfully!"
                                )
                                return redirect("dashboard")
                            except Exception as retry_exc:
                                print("UPDATE RETRY FAILED:", repr(retry_exc))
                        else:
                            messages.error(
                                request, "Session expired. Please log in again."
                            )
                            return redirect("login")
                    else:
                        print("EXPENSE UPDATE FAILED:", repr(exc))

                    messages.error(request, "Could not update the expense.")
        else:
            form = ExpenseForm(initial={
                "title": expense["title"],
                "amount": expense["amount"],
                "currency": expense["currency"],
                "category": expense["category"],
                "date": expense["date"],
                "is_taxable": expense["is_taxable"],
            })

        return render(
            request,
            "expenses/edit_expense.html",
            {"form": form, "expense": expense},
        )

    except Exception as exc:
        print("EDIT EXPENSE ERROR:", repr(exc))
        messages.error(request, "Could not load this expense.")
        return redirect("dashboard")


@require_POST
def delete_expense_view(request, expense_id):
    access_token = request.session.get("supabase_access_token")

    if not access_token:
        return redirect("login")

    try:
        delete_expense(access_token, expense_id)
        messages.success(request, "Expense deleted successfully!")

    except Exception as exc:
        if "JWT expired" in str(exc):
            if refresh_supabase_session(request):
                try:
                    delete_expense(
                        request.session["supabase_access_token"],
                        expense_id,
                    )
                    messages.success(
                        request, "Expense deleted successfully!"
                    )
                except Exception as retry_exc:
                    print("DELETE RETRY FAILED:", repr(retry_exc))
                    messages.error(request, "Could not delete the expense.")
            else:
                messages.error(
                    request, "Session expired. Please log in again."
                )
                return redirect("login")
        else:
            print("EXPENSE DELETE FAILED:", repr(exc))
            messages.error(request, "Could not delete the expense.")

    return redirect("dashboard")
