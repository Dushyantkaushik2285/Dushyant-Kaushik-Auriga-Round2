from decimal import Decimal

from django.test import TestCase

from .models import Member, Payment, Pool
from .services import calculate_settlements


class FairShareTests(TestCase):

    def setUp(self):
        self.pool = Pool.objects.create(
            name="Test Farewell",
            target_amount=Decimal("6000.00"),
        )

        self.dushyant = Member.objects.create(
            pool=self.pool,
            name="Dushyant",
        )

        self.rahul = Member.objects.create(
            pool=self.pool,
            name="Rahul",
        )

        self.priya = Member.objects.create(
            pool=self.pool,
            name="Priya",
        )

        self.modi = Member.objects.create(
            pool=self.pool,
            name="Modi",
        )

    def test_fair_share(self):
        self.assertEqual(
            self.pool.fair_share,
            Decimal("1500.00"),
        )

    def test_member_balance(self):
        Payment.objects.create(
            member=self.dushyant,
            amount=Decimal("2000.00"),
        )

        self.assertEqual(
            self.dushyant.balance,
            Decimal("500.00"),
        )

    def test_settlement_between_members(self):
        Payment.objects.create(
            member=self.dushyant,
            amount=Decimal("2000.00"),
        )

        Payment.objects.create(
            member=self.rahul,
            amount=Decimal("1000.00"),
        )

        Payment.objects.create(
            member=self.priya,
            amount=Decimal("2000.00"),
        )

        Payment.objects.create(
            member=self.modi,
            amount=Decimal("1000.00"),
        )

        result = calculate_settlements(self.pool)

        transfers = result["transfers"]

        self.assertEqual(len(transfers), 2)

        amounts = sorted(
            transfer["amount"]
            for transfer in transfers
        )

        self.assertEqual(
            amounts,
            [
                Decimal("500.00"),
                Decimal("500.00"),
            ],
        )

    def test_overpayment_refund(self):
        Payment.objects.create(
            member=self.dushyant,
            amount=Decimal("3000.00"),
        )

        Payment.objects.create(
            member=self.modi,
            amount=Decimal("5500.00"),
        )

        result = calculate_settlements(self.pool)

        self.assertEqual(
            result["overfunded_amount"],
            Decimal("2500.00"),
        )

        self.assertEqual(
            len(result["refunds"]),
            1,
        )

        self.assertEqual(
            result["refunds"][0]["member"],
            self.modi,
        )

        self.assertEqual(
            result["refunds"][0]["amount"],
            Decimal("2500.00"),
        )