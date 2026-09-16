1. Problem Understanding

The application manages a shared contribution pool where multiple people contribute toward a common target.

The challenge is that members may contribute different amounts.

For example:

Target = ₹6,000
Members = 4
Fair share = ₹1,500

One member may pay ₹2,000, another ₹1,000, another ₹0, and another ₹3,000.

The application therefore calculates how much each member has contributed compared with their fair share.

The later requirement adds historical contribution import. The historical data can be messy, so it must be cleaned before it affects balances.

2. Data Model

The application uses three main models:

Pool
  ↓
Member
  ↓
Payment

Pool

Stores the pool name, target amount, and creation time.

Member

Belongs to a specific pool and stores the member name.

Payment

Represents an individual contribution and stores the member, amount, and creation time.

3. Why Store Payments Individually?

Payments are stored as individual records instead of storing only a final balance.

For example:

Dushyant
₹1,000
₹500
₹500

Total:

₹2,000

This gives the application a clear source of truth and allows balances to be recalculated from payment history.

Imported and manually entered payments can therefore use the same calculation logic.

4. Fair Share

The fair share is:

target amount / number of members

Example:

₹6,000 / 4 = ₹1,500

The calculation is dynamic, so adding a member automatically changes the fair share.

5. Balance

For every member:

balance = total paid - fair share

Interpretation:

positive → creditor
negative → debtor
zero     → settled

6. Settlement Algorithm

The settlement service separates members into creditors and debtors.

A creditor has a positive balance.

A debtor has a negative balance.

The algorithm repeatedly matches a debtor with a creditor and transfers:

minimum(debtor outstanding,
        creditor outstanding)

Both outstanding amounts are reduced after each transfer.

This creates a simple settlement list without requiring every member to pay every other member.

7. Overfunding

If total collected exceeds the target, the excess is treated as a refund.

Example:

Target = ₹6,000
Collected = ₹8,500
Overfunded = ₹2,500

The unmatched positive amount can therefore be shown as a refund from the pool.

8. Multiple Pools

The application supports multiple pools.

Each pool has its own members, payments, balances, and settlements.

The active pool ID is stored in the Django session.

Creating a new pool makes it the active pool.

9. Manual Payment Validation

Manual payments are checked against the remaining target on the server.

This prevents users from recording more than the remaining amount through the normal payment form.

The HTML maximum is only a UI convenience; server-side validation remains the actual enforcement.

Historical imports intentionally bypass this restriction because historical data may legitimately show overfunding.

10. Messy CSV Import

The importer treats the CSV requirement as a data-cleaning pipeline.

It does not rely on a hardcoded list of members.

The process is:

CSV
 ↓
Read row
 ↓
Validate name
 ↓
Parse amount
 ↓
Normalize name
 ↓
Detect duplicate
 ↓
Find member
 ↓
High-confidence match?
 ├── Yes → use existing member
 └── No  → create new member
 ↓
Create payment
 ↓
Add result to audit report

11. Name Normalization

Names are:

trimmed

converted to lowercase for comparison

stripped of punctuation

normalized for repeated whitespace

For example:

" RAHUL-SHARMA "

becomes:

"rahul sharma"

If an exact normalized match is not found, conservative fuzzy matching is used.

A high threshold is intentional because similar names do not necessarily represent the same person.

12. Amount Parsing

The importer supports common formats:

1500       → 1500.00
₹1,500     → 1500.00
Rs. 1500   → 1500.00
INR 1500   → 1500.00
1.5k       → 1500.00
1l         → 100000.00

Python Decimal is used for monetary values to avoid typical floating-point precision problems.

13. Duplicate Detection

The current importer identifies duplicate rows within the uploaded file using:

normalized name + parsed amount

This catches obvious duplicates such as:

Dushyant,1500
DUSHYANT,"₹1,500"

However, without a transaction identifier, two identical-looking records cannot always be proven to be duplicates.

A production system should use a transaction ID, date, source ID, or another unique identifier.

14. Invalid Rows

Invalid rows do not stop the whole import.

Examples:

Wrong Person,abc
,1000

These rows are rejected and the report records their row number and reason.

15. Import Report

The importer produces:

Received
Imported
Duplicates
Merged
Rejected

It also provides row-level details.

This makes the cleaning process transparent and auditable.

16. Separation of Responsibilities

pool/importers.py handles:

CSV
 ↓
Clean
 ↓
Validate
 ↓
Deduplicate
 ↓
Match members
 ↓
Create payments

pool/services.py handles:

Payments
 ↓
Balances
 ↓
Settlements
 ↓
Refunds

All valid contributions eventually become normal Payment records, so the same settlement engine can process manual and imported contributions.

17. Testing Strategy

The core tests cover:

Fair-share calculation

Member balance calculation

Settlement transfers

Overpayment/refund calculation

Importer tests should cover:

valid rows

currency formats

shorthand amounts

duplicates

fuzzy name matches

invalid amounts

missing names

18. Trade-offs

The implementation prioritizes clarity and maintainability.

Django and SQLite keep the project easy to run.

The settlement algorithm is simple and understandable.

Fuzzy matching is conservative to reduce incorrect identity merges.

The importer processes rows dynamically instead of relying on predefined members.

19. Future Improvements

For a production system:

transaction IDs

stronger duplicate detection

import history

rollback support

review workflow for uncertain name matches

bulk database operations

asynchronous processing

authentication and permissions

PostgreSQL

stronger audit logging

20. Final Architecture

                    User
                      │
             ┌────────┴────────┐
             │                 │
             ▼                 ▼
      Manual Payments      CSV Import
             │                 │
             │          Clean / Validate
             │                 │
             │          Match / Deduplicate
             │                 │
             └────────┬────────┘
                      │
                      ▼
                   Payments
                      │
                      ▼
                Balance Logic
                      │
                      ▼
              Settlement Service
                 /                          ▼            ▼
           Transfers       Refunds

The key design principle is that all valid contributions eventually become Payment records, allowing the same balance and settlement logic to work regardless of where the contribution originated.