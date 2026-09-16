from decimal import Decimal

from .models import Pool


def calculate_settlements(pool: Pool):
    """
    Calculate member-to-member transfers and any required refunds.

    Positive balance = member paid more than their fair share.
    Negative balance = member paid less than their fair share.

    If the total collected amount is greater than the pool target,
    the excess amount is treated as a refund from the pool.
    """

    members = list(
        pool.members.prefetch_related("payments").all()
    )

    if not members:
        return {
            "transfers": [],
            "refunds": [],
            "overfunded_amount": Decimal("0.00"),
        }

    fair_share = pool.fair_share

    creditors = []
    debtors = []

    for member in members:
        paid = member.total_paid
        balance = paid - fair_share

        if balance > Decimal("0.00"):
            creditors.append(
                {
                    "member": member,
                    "amount": balance,
                }
            )

        elif balance < Decimal("0.00"):
            debtors.append(
                {
                    "member": member,
                    "amount": abs(balance),
                }
            )

    transfers = []

    creditor_index = 0
    debtor_index = 0

    # Match people who owe money with people who paid extra.
    while (
        creditor_index < len(creditors)
        and debtor_index < len(debtors)
    ):
        creditor = creditors[creditor_index]
        debtor = debtors[debtor_index]

        amount = min(
            creditor["amount"],
            debtor["amount"],
        )

        if amount > Decimal("0.00"):
            transfers.append(
                {
                    "from": debtor["member"],
                    "to": creditor["member"],
                    "amount": amount.quantize(
                        Decimal("0.01")
                    ),
                }
            )

        creditor["amount"] -= amount
        debtor["amount"] -= amount

        if creditor["amount"] <= Decimal("0.00"):
            creditor_index += 1

        if debtor["amount"] <= Decimal("0.00"):
            debtor_index += 1

    # Any creditor amount left after all debtors are settled
    # represents money collected above the target.
    refunds = []

    for creditor in creditors:
        if creditor["amount"] > Decimal("0.00"):
            refunds.append(
                {
                    "member": creditor["member"],
                    "amount": creditor["amount"].quantize(
                        Decimal("0.01")
                    ),
                }
            )

    overfunded_amount = max(
        pool.total_collected - pool.target_amount,
        Decimal("0.00"),
    )

    return {
        "transfers": transfers,
        "refunds": refunds,
        "overfunded_amount": overfunded_amount.quantize(
            Decimal("0.01")
        ),
    }