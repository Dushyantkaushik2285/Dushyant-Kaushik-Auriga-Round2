import csv
import io
import re
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher

from .models import Member, Payment


NAME_HEADERS = {
    "name",
    "member",
    "member_name",
    "person",
    "person_name",
    "contributor",
    "contributor_name",
}

AMOUNT_HEADERS = {
    "amount",
    "payment",
    "paid",
    "contribution",
    "contributed",
    "payment_amount",
}


def normalize_header(value):
    return re.sub(
        r"[^a-z0-9_]",
        "",
        str(value).strip().lower().replace(" ", "_"),
    )


def normalize_name(name):
    """
    Normalize a person's name for comparison.
    """

    name = str(name).strip().lower()

    name = re.sub(r"[^a-z0-9\s]", " ", name)

    name = re.sub(r"\s+", " ", name)

    return name.strip()


def display_name(name):
    """
    Convert a cleaned name into a readable display name.
    """

    return " ".join(
        word.capitalize()
        for word in str(name).strip().split()
    )


def parse_amount(value):
    """
    Parse common Indian currency formats.

    Examples:
        1500
        1500.00
        ₹1,500
        Rs. 1500
        INR 1,500
        1.5k
    """

    if value is None:
        raise ValueError("Amount is empty.")

    raw = str(value).strip().lower()

    if not raw:
        raise ValueError("Amount is empty.")

    raw = (
        raw.replace("₹", "")
        .replace("rs.", "")
        .replace("rs", "")
        .replace("inr", "")
        .replace(",", "")
        .strip()
    )

    multiplier = Decimal("1")

    if raw.endswith("k"):
        multiplier = Decimal("1000")
        raw = raw[:-1].strip()

    elif raw.endswith("l"):
        multiplier = Decimal("100000")
        raw = raw[:-1].strip()

    try:
        amount = Decimal(raw) * multiplier
    except InvalidOperation:
        raise ValueError(
            f"Invalid amount format: {value}"
        )

    if amount <= Decimal("0.00"):
        raise ValueError(
            "Amount must be greater than zero."
        )

    return amount.quantize(Decimal("0.01"))


def find_matching_member(pool, cleaned_name):
    """
    Find an existing member using normalized and
    conservative fuzzy name matching.

    Exact normalized names are preferred.
    Fuzzy matching is only used when confidence is high.
    """

    normalized = normalize_name(cleaned_name)

    members = list(pool.members.all())

    # Exact normalized match.
    for member in members:
        if normalize_name(member.name) == normalized:
            return member, False

    # Conservative fuzzy match.
    best_member = None
    best_score = 0

    for member in members:
        existing = normalize_name(member.name)

        score = SequenceMatcher(
            None,
            normalized,
            existing,
        ).ratio()

        if score > best_score:
            best_score = score
            best_member = member

    if best_member and best_score >= 0.88:
        return best_member, True

    return None, False


def detect_headers(fieldnames):
    """
    Identify which CSV columns represent name and amount.
    """

    if not fieldnames:
        raise ValueError(
            "CSV file does not contain a header row."
        )

    normalized = {
        normalize_header(field): field
        for field in fieldnames
    }

    name_column = None
    amount_column = None

    for header in NAME_HEADERS:
        if header in normalized:
            name_column = normalized[header]
            break

    for header in AMOUNT_HEADERS:
        if header in normalized:
            amount_column = normalized[header]
            break

    if not name_column:
        raise ValueError(
            "Could not find a name column. "
            "Use a column such as name or member."
        )

    if not amount_column:
        raise ValueError(
            "Could not find an amount column. "
            "Use a column such as amount or payment."
        )

    return name_column, amount_column


def import_contributions(pool, uploaded_file):
    """
    Clean and import a CSV contribution file.

    Returns an audit report containing:
        received
        imported
        duplicates
        merged
        rejected
        imported_rows
        merged_rows
        rejected_rows
    """

    content = uploaded_file.read()

    if isinstance(content, bytes):
        content = content.decode(
            "utf-8-sig",
            errors="replace",
        )

    reader = csv.DictReader(
        io.StringIO(content)
    )

    name_column, amount_column = detect_headers(
        reader.fieldnames
    )

    report = {
        "received": 0,
        "imported": 0,
        "duplicates": 0,
        "merged": 0,
        "rejected": 0,
        "imported_rows": [],
        "merged_rows": [],
        "rejected_rows": [],
    }

    seen_rows = set()

    for row_number, row in enumerate(
        reader,
        start=2,
    ):
        report["received"] += 1

        raw_name = row.get(name_column)
        raw_amount = row.get(amount_column)

        # Validate name.
        if not raw_name or not str(raw_name).strip():
            report["rejected"] += 1

            report["rejected_rows"].append(
                {
                    "row": row_number,
                    "name": raw_name or "",
                    "amount": raw_amount or "",
                    "reason": "Name is empty.",
                }
            )

            continue

        cleaned_name = display_name(raw_name)

        # Validate amount.
        try:
            amount = parse_amount(raw_amount)

        except ValueError as error:
            report["rejected"] += 1

            report["rejected_rows"].append(
                {
                    "row": row_number,
                    "name": cleaned_name,
                    "amount": raw_amount or "",
                    "reason": str(error),
                }
            )

            continue

        normalized_name = normalize_name(
            cleaned_name
        )

        # Exact duplicate row detection.
        duplicate_key = (
            normalized_name,
            amount,
        )

        if duplicate_key in seen_rows:
            report["duplicates"] += 1

            continue

        seen_rows.add(duplicate_key)

        # Find an existing member.
        member, was_merged = find_matching_member(
            pool,
            cleaned_name,
        )

        if member is None:
            member = Member.objects.create(
                pool=pool,
                name=cleaned_name,
            )

        elif was_merged:
            report["merged"] += 1

            report["merged_rows"].append(
                {
                    "row": row_number,
                    "source_name": cleaned_name,
                    "matched_name": member.name,
                }
            )

        # Historical imports intentionally bypass the
        # normal manual-payment target restriction.
        payment = Payment.objects.create(
            member=member,
            amount=amount,
        )

        report["imported"] += 1

        report["imported_rows"].append(
            {
                "row": row_number,
                "name": member.name,
                "amount": amount,
            }
        )

    return report