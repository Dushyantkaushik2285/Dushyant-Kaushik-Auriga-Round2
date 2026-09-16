from django.db import models


class Pool(models.Model):
    name = models.CharField(max_length=200)
    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()

    @property
    def fair_share(self):
        if self.member_count == 0:
            return self.target_amount

        return self.target_amount / self.member_count

    @property
    def total_collected(self):
        return sum(
            payment.amount
            for member in self.members.all()
            for payment in member.payments.all()
        )

    @property
    def remaining_amount(self):
        remaining = self.target_amount - self.total_collected
        return max(remaining, 0)


class Member(models.Model):
    pool = models.ForeignKey(
        Pool,
        on_delete=models.CASCADE,
        related_name="members"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    @property
    def total_paid(self):
        return sum(
            payment.amount
            for payment in self.payments.all()
        )

    @property
    def balance(self):
        return self.total_paid - self.pool.fair_share


class Payment(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.name} - ₹{self.amount}"