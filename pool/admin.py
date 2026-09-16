from django.contrib import admin

from .models import Pool, Member, Payment


@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    list_display = ("name", "target_amount", "created_at")


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "pool")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("member", "amount", "created_at")