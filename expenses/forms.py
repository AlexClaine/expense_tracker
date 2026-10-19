from django import forms

class SignupForm(forms.Form):
    email = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput(), min_length=8,)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=8,)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error(
                "confirm_password",
                "Passwords do not match!",
            )

            return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


CURRENCY_CHOICES = [
    ("USD", "USD"),
    ("EUR", "EUR"),
    ("GBP", "GBP"),
    ("KES", "KES"),
]

CATEGORY_CHOICES = [
    ("food", "Food"),
    ("transport", "Transport"),
    ("utilities", "Utilities"),
    ("entertainment", "Entertainment"),
    ("health", "Health"),
    ("other", "Other"),
]


class ExpenseForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label="Expense title",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. Office stationery",
        }),
    )

    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        label="Amount",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "step": "0.01",
            "placeholder": "0.00",
        }),
    )

    currency = forms.ChoiceField(
        choices=[
            ("KES", "KES - Kenyan Shilling"),
            ("USD", "USD - US Dollar"),
            ("EUR", "EUR - Euro"),
            ("GBP", "GBP - British Pound"),
        ],
        initial="KES",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    category = forms.ChoiceField(
        choices=[
            ("Food", "Food"),
            ("Transport", "Transport"),
            ("Office Supplies", "Office Supplies"),
            ("Utilities", "Utilities"),
            ("Rent", "Rent"),
            ("Other", "Other"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date"}
        ),
    )

    is_taxable = forms.BooleanField(
        required=False,
        label="This expense is taxable",
    )
