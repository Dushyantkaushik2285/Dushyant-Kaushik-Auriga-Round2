from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    ContributionImportForm,
    MemberForm,
    PaymentForm,
    PoolForm,
)
from .importers import import_contributions
from .models import Pool
from .services import calculate_settlements


def get_active_pool(request):
    """
    Return the pool currently selected by the user.

    If no pool is selected, use the most recently created pool.
    """

    pool_id = request.session.get("active_pool_id")

    if pool_id:
        pool = Pool.objects.filter(id=pool_id).first()

        if pool:
            return pool

    return Pool.objects.order_by("-created_at").first()


def dashboard(request):
    pool = get_active_pool(request)

    members = []

    if pool:
        members = list(
            pool.members.prefetch_related("payments").all()
        )

    pools = Pool.objects.order_by("-created_at")

    return render(
        request,
        "pool/dashboard.html",
        {
            "pool": pool,
            "members": members,
            "pools": pools,
        },
    )


def create_pool(request):
    if request.method == "POST":
        form = PoolForm(request.POST)

        if form.is_valid():
            pool = form.save()

            request.session["active_pool_id"] = pool.id

            return redirect("dashboard")

    else:
        form = PoolForm()

    return render(
        request,
        "pool/create_pool.html",
        {
            "form": form,
        },
    )


def switch_pool(request, pool_id):
    pool = get_object_or_404(Pool, id=pool_id)

    request.session["active_pool_id"] = pool.id

    return redirect("dashboard")


def add_member(request):
    pool = get_active_pool(request)

    if not pool:
        return redirect("create_pool")

    if request.method == "POST":
        form = MemberForm(request.POST)

        if form.is_valid():
            member = form.save(commit=False)
            member.pool = pool
            member.save()

            return redirect("dashboard")

    else:
        form = MemberForm()

    return render(
        request,
        "pool/add_member.html",
        {
            "form": form,
            "pool": pool,
        },
    )


def record_payment(request):
    pool = get_active_pool(request)

    if not pool:
        return redirect("create_pool")

    if request.method == "POST":
        form = PaymentForm(request.POST)

        form.fields["member"].queryset = pool.members.all()

        if form.is_valid():
            payment = form.save(commit=False)

            if payment.member.pool_id != pool.id:
                form.add_error(
                    "member",
                    "Invalid member selected.",
                )

            else:
                remaining = (
                    pool.target_amount
                    - pool.total_collected
                )

                if remaining <= 0:
                    form.add_error(
                        "amount",
                        "The pool is already fully funded. "
                        "No more payments are required.",
                    )

                elif payment.amount > remaining:
                    form.add_error(
                        "amount",
                        f"Only ₹{remaining:.2f} is remaining "
                        "to reach the target.",
                    )

                else:
                    payment.save()
                    return redirect("dashboard")

    else:
        form = PaymentForm()
        form.fields["member"].queryset = pool.members.all()

    return render(
        request,
        "pool/record_payment.html",
        {
            "form": form,
            "pool": pool,
        },
    )


def import_contributions_view(request):
    pool = get_active_pool(request)

    if not pool:
        return redirect("create_pool")

    if request.method == "POST":
        form = ContributionImportForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                report = import_contributions(
                    pool,
                    form.cleaned_data["file"],
                )

                return render(
                    request,
                    "pool/import_report.html",
                    {
                        "pool": pool,
                        "report": report,
                    },
                )

            except (ValueError, UnicodeDecodeError) as error:
                form.add_error(
                    "file",
                    str(error),
                )

    else:
        form = ContributionImportForm()

    return render(
        request,
        "pool/import_contributions.html",
        {
            "form": form,
            "pool": pool,
        },
    )


def settlements(request):
    pool = get_active_pool(request)

    if not pool:
        return redirect("create_pool")

    settlement_data = calculate_settlements(pool)

    return render(
        request,
        "pool/settlements.html",
        {
            "pool": pool,
            "transfers": settlement_data["transfers"],
            "refunds": settlement_data["refunds"],
            "overfunded_amount": settlement_data[
                "overfunded_amount"
            ],
        },
    )