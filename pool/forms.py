from decimal import Decimal

from django import forms

from .models import Member, Payment, Pool


class PoolForm(forms.ModelForm):
    class Meta:
        model = Pool
        fields = ["name", "target_amount"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full border rounded-lg px-4 py-2",
                    "placeholder": "e.g. Farewell Gift",
                }
            ),
            "target_amount": forms.NumberInput(
                attrs={
                    "class": "w-full border rounded-lg px-4 py-2",
                    "placeholder": "e.g. 6000",
                    "min": "0.01",
                    "step": "0.01",
                }
            ),
        }

    def clean_target_amount(self):
        amount = self.cleaned_data["target_amount"]

        if amount <= Decimal("0.00"):
            raise forms.ValidationError(
                "Target amount must be greater than zero."
            )

        return amount


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["name"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full border rounded-lg px-4 py-2",
                    "placeholder": "Enter member name",
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if not name:
            raise forms.ValidationError(
                "Member name cannot be empty."
            )

        return name


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["member", "amount"]

        widgets = {
            "member": forms.Select(
                attrs={
                    "class": "w-full border rounded-lg px-4 py-2",
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "w-full border rounded-lg px-4 py-2",
                    "placeholder": "Enter amount",
                    "min": "0.01",
                    "step": "0.01",
                }
            ),
        }

    def clean_amount(self):
        amount = self.cleaned_data["amount"]

        if amount <= Decimal("0.00"):
            raise forms.ValidationError(
                "Payment amount must be greater than zero."
            )

        return amount


class ContributionImportForm(forms.Form):
    file = forms.FileField(
        label="Contribution CSV",
        help_text="Upload a CSV containing a name/member column and an amount/payment column.",
        widget=forms.ClearableFileInput(
            attrs={
                "class": (
                    "w-full border border-gray-300 rounded-lg "
                    "px-4 py-3 bg-white"
                ),
                "accept": ".csv,text/csv",
            }
        ),
    )

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]

        filename = uploaded_file.name.lower()

        if not filename.endswith(".csv"):
            raise forms.ValidationError(
                "Please upload a CSV file."
            )

        if uploaded_file.size == 0:
            raise forms.ValidationError(
                "The uploaded CSV file is empty."
            )

        if uploaded_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "The CSV file must be smaller than 5 MB."
            )

        return uploaded_file