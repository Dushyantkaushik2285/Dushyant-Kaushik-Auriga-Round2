# Dushyant-Kaushik-Auriga-# FairShare – Farewell Gift Settlement

A Django-based web application for managing shared contributions toward a group gift or common pool.

The application calculates each member's fair share, tracks individual payments, shows who still owes money, and generates a simplified settlement plan. It also handles cases where a member contributes more than their fair share or when the pool becomes overfunded.

---

## Problem

A group of people wants to purchase a common gift.

For example:

- Target budget: ₹6,000
- 4 members
- Equal fair share: ₹1,500 each

In real situations, members may:

- Pay the full amount
- Pay partially
- Pay nothing
- Pay more than their fair share

The application should make it easy to understand the current state and calculate the final transfers required.

---

## Features

### Pool Management

- Create a pool with a custom name.
- Set any target amount.
- Calculate the fair share automatically based on the number of members.

### Member Management

- Add members to the pool.
- Display each member's contribution.
- Display each member's current balance.

### Payment Tracking

- Record payments against individual members.
- Support partial payments.
- Support extra payments.
- Maintain payment history through the database.

### Settlement Calculation

The application identifies:

- Members who need to pay.
- Members who should receive money.
- The amount each member should transfer.
- Overpayment/refund amounts when the pool exceeds its target.

### Automated Testing

The project includes tests covering:

- Fair-share calculation.
- Member balance calculation.
- Normal settlement.
- Overpayment/refund handling.

---

## Technology Stack

- Python
- Django
- SQLite
- Django Templates
- Tailwind CSS CDN
- HTML
- CSS
- JavaScript

---

## Project Structure

```text
Dushyant-Kaushik-Auriga-Round2/
│
├── manage.py
├── requirements.txt
├── README.md
├── REASONING.md
├── AI_LOGS.md
├── .gitignore
│
├── fairshare/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── pool/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── services.py
│   ├── urls.py
│   ├── tests.py
│   └── ...
│
├── templates/
│   └── pool/
│       ├── dashboard.html
│       ├── create_pool.html
│       ├── add_member.html
│       ├── record_payment.html
│       └── settlements.html
│
└── static/Round2