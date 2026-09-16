# FairShare — Farewell Gift Contribution & Settlement App

## Overview

FairShare is a Django web application for managing group contributions toward a shared target, such as a farewell gift.

The application handles uneven payments, calculates each member's fair share and balance, and produces a simple settlement list showing who should pay whom.

It also supports importing historical contributions from a messy CSV file. The importer cleans common currency formats, normalizes names, detects duplicate rows, performs conservative fuzzy matching for likely name variations, rejects invalid rows, and produces an audit report.

## Features

- Create and manage multiple contribution pools
- Switch between pools
- Add members to a pool
- Record manual payments
- Calculate equal fair share automatically
- Calculate member balances
- Generate simple member-to-member settlements
- Detect and display overfunding/refunds
- Import historical contributions from CSV
- Clean common currency formats such as `₹1,500`, `Rs. 1500`, `INR 1500`, and `1.5k`
- Normalize names
- Detect duplicate rows
- Perform conservative fuzzy name matching
- Reject invalid rows
- Generate an import audit report

## Example

For a target of ₹6,000 and four members:

```text
Fair share = ₹6,000 / 4
           = ₹1,500
```

If contributions are:

```text
Dushyant → ₹2,000
Rahul    → ₹1,000
Priya    → ₹2,000
Modi     → ₹1,000
```

Balances are:

```text
Dushyant → +₹500
Rahul    → -₹500
Priya    → +₹500
Modi     → -₹500
```

A possible settlement is:

```text
Rahul → Dushyant ₹500
Modi → Priya ₹500
```

## Overfunding

If the target is ₹6,000 but ₹8,500 has been collected:

```text
Overfunded = ₹8,500 - ₹6,000
           = ₹2,500
```

The excess is represented as a refund rather than another member debt.

## Messy CSV Import

Example:

```csv
name,amount
Dushyant,1500
Rahul Sharma,"₹1,000"
Rahul Sharm,500
PRIYA,1.2k
Modi,Rs. 2000
Wrong Person,abc
,1000
```

The importer processes every row dynamically.

It:

1. Validates the name
2. Parses the amount
3. Normalizes the name
4. Checks for duplicate rows
5. Finds an existing member
6. Uses conservative fuzzy matching when appropriate
7. Creates a new member if no reliable match exists
8. Creates the payment
9. Reports imported, merged, duplicate, and rejected rows

The application does not contain a hardcoded list of members.

## Tech Stack

- Python
- Django
- SQLite
- Django Templates
- Tailwind CSS CDN

## Project Structure

```text
Dushyant-Kaushik-Auriga-Round2/
├── README.md
├── REASONING.md
├── AI_LOGS.md
├── requirements.txt
├── manage.py
├── fairshare/
├── pool/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── importers.py
│   ├── services.py
│   ├── urls.py
│   └── tests.py
└── templates/
    └── pool/
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

For GitHub Codespaces:

```bash
python manage.py runserver 0.0.0.0:8000
```

## Testing

Run:

```bash
python manage.py check
python manage.py test
```

The test suite covers fair-share calculation, member balances, settlement transfers, and overpayment/refund handling.

## Design Decisions

### Django

Django provides routing, ORM, forms, validation, templates, testing, and the admin interface in one framework.

### SQLite

SQLite keeps the assessment self-contained and easy to run.

### Separate importer

`pool/importers.py` is responsible for cleaning and importing external CSV data.

`pool/services.py` is responsible for balance and settlement calculations.

This means imported and manually entered payments can use the same settlement logic.

### Conservative name matching

Name similarity cannot guarantee that two records belong to the same person. Therefore, fuzzy matching uses a high confidence threshold instead of aggressively merging names.

## Assumptions

- All members of a pool have an equal fair share.
- A member can make multiple payments.
- Historical imports may cause a pool to become overfunded.
- Manual payments cannot exceed the remaining target.
- Duplicate detection without a transaction ID has limitations.
- The current importer detects identical normalized name + amount rows within the uploaded file.
- A production system should use transaction IDs or similar identifiers for stronger duplicate detection.

## Future Improvements

- Transaction IDs
- Stronger duplicate detection
- Import history and rollback
- Review workflow for uncertain name matches
- Bulk database operations
- Asynchronous processing for very large files
- Authentication and authorization
- PostgreSQL
- Stronger audit logging

## Author

Dushyant Kaushik

Auriga IT Placement Drive 2026 — Round 2 Build Assessment
