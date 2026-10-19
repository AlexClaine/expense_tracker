
from expenses.supabase_client import get_supabase_client


def refresh_supabase_session(request):
    """
    Refresh an expired Supabase access token using the
    refresh token stored in the Django session.
    """
    refresh_token = request.session.get("supabase_refresh_token")

    if not refresh_token:
        return False

    client = get_supabase_client()

    try:
        result = client.auth.refresh_session(refresh_token)

        if not result.session:
            return False

        request.session["supabase_access_token"] = (
            result.session.access_token
        )
        request.session["supabase_refresh_token"] = (
            result.session.refresh_token
        )

        return True

    except Exception as exc:
        print("SUPABASE TOKEN REFRESH FAILED:", repr(exc))
        return False


def get_user_expenses(access_token):
    """Retrieve expenses using the user's Supabase JWT."""
    client = get_supabase_client()
    client.postgrest.auth(access_token)

    response = (
        client.table("expenses")
        .select("*")
        .order("date", desc=True)
        .execute()
    )

    return response.data


def create_expense(access_token, user_id, expense_data):
    """Save an expense for the authenticated user."""
    client = get_supabase_client()
    client.postgrest.auth(access_token)

    record = {
        "user_id": user_id,
        "title": expense_data["title"].strip(),
        "amount": str(expense_data["amount"]),
        "currency": expense_data["currency"],
        "category": expense_data["category"],
        "date": expense_data["date"].isoformat(),
        "is_taxable": expense_data["is_taxable"],
    }

    response = (
        client.table("expenses")
        .insert(record)
        .execute()
    )

    return response.data

def get_user_expense(access_token, expense_id):
    """Fetch one expense, subject to the user's RLS permissions."""

    client = get_supabase_client()
    client.postgrest.auth(access_token)

    response =  (
        client.table("expenses")
        .select("*")
        .eq("id", str(expense_id))
        .limit(1)
        .execute()
    )

    return response.data[0] if response.data else None

def update_expense(access_token, expense_id, expense_data):
    """Update an existing expense."""
    client = get_supabase_client()
    client.postgrest.auth(access_token)

    record = {
        "title": expense_data["title"].strip(),
        "amount": str(expense_data["amount"]),
        "currency": expense_data["currency"],
        "category": expense_data["category"],
        "date": expense_data["date"].isoformat(),
        "is_taxable": expense_data["is_taxable"],
    }

    response = (
        client.table("expenses")
        .update(record)
        .eq("id", str(expense_id))
        .execute()
    )

    if not response.data:
        raise ValueError("Expense not found or access denied.")

    return response.data

def delete_expense(access_token, expense_id):
    """Delete an expense from the database."""
    client = get_supabase_client()
    client.postgrest.auth(access_token)

    response = (
        client.table("expenses")
        .delete()
        .eq("id", str(expense_id))
        .execute()
    )

    if not response.data:
        raise ValueError("Expense not found or access denied.")

    return response.data
