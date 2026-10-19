# Expense Tracker

A web application for tracking personal expenses, built with Django and Supabase. It supports multi-currency expenses, VAT calculations, category breakdowns, and currency conversion.

---

## Features

- User registration and login via Supabase Auth
- Add, edit, and delete expenses
- Automatic VAT calculation (16%) on taxable expenses
- Expense breakdown by category and currency
- Currency conversion to KES, USD, EUR, or GBP
- Session-based authentication with automatic token refresh

---

## Getting Started

### 1. Register an Account

- Visit the app and click **Sign Up**
- Enter your email address and a password (minimum 8 characters)
- Click **Create Account**

> **Important:** After registering, Supabase will send a confirmation email to the address you provided. You **must click the confirmation link** in that email before you can log in. Check your spam folder if you don't see it within a few minutes.

### 2. Log In

- Once your email is confirmed, go to the **Login** page
- Enter your email and password
- You will be redirected to your dashboard

### 3. Adding an Expense

On the dashboard, fill in the **Add an Expense** form:

| Field | Description |
|-------|-------------|
| Title | A short description of the expense |
| Amount | The expense amount (e.g. 1500.00) |
| Currency | KES, USD, EUR, or GBP |
| Category | Food, Transport, Utilities, Entertainment, Health, or Other |
| Date | The date the expense was incurred |
| Is Taxable | Check this if the expense is subject to 16% VAT |

Click **Save Expense** to record it.

### 4. Editing or Deleting an Expense

- In the **My Expenses** table, click **Edit** to update an expense
- Click **Delete** to permanently remove an expense (you will be asked to confirm)

### 5. Currency Conversion

- Use the **Expense Report Currency** section to view your combined expense total converted to a single currency
- Select a reporting currency and click **Convert Total**
- Your original expense records are not changed — this is for reporting only

### 6. Logging Out

- Click **Logout** to end your session securely

---

## Common Errors

### "No active session was returned"
You registered but haven't confirmed your email yet. Check your inbox (and spam folder) for a confirmation email from Supabase and click the link before trying to log in.

### "Login failed. Check your email and password."
Either the email or password is incorrect, or your email has not been confirmed yet. If you just registered, confirm your email first.

### "Registration failed. Check your details or try signing in if you already have an account."
An account with that email may already exist. Try logging in instead, or use a different email address.

### "Could not load expenses. Please try again."
Your session may have expired. Try logging out and logging back in. If the problem persists, the database connection may be temporarily unavailable.

### "Exchange rates are currently unavailable."
The currency conversion service could not fetch live exchange rates. Your expense records are unaffected — try converting again later.

---

## Tech Stack

- **Backend:** Django 6.1, Python 3.14
- **Database & Auth:** Supabase (PostgreSQL)
- **Deployment:** Vercel
- **Key packages:** `dj-database-url`, `python-decouple`, `supabase`, `psycopg2`
