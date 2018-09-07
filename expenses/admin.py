from django.contrib import admin
from .models import *


def action_paid(modeladmin, request, queryset):
    for ele in queryset:
        ele.is_paid=True
        ele.save()
action_paid.short_description = 'Multiple Paid'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass


@admin.register(BillCategory)
class BillCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'tag_balance']
    fields = ['title', ]
    search_fields = ['title', ]


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    save_as = True
    save_on_top = True
    list_display = ['date_expired', 'category', 'tag_final_value','payment_method', 'is_paid']
    list_filter = ['category', 'is_paid', 'date_expired', 'payment_method']
    search_fields = ['title', 'category__title']
    readonly_fields = ['paid_value']
    fields = ['category', 'payment_method', 'date_expired', 'is_paid', 'final_value', 'title', 'paid_value']
    actions = [action_paid, ]


@admin.register(PayrollCategory)
class PayrollCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'tag_balance']
    fields = ['title', ]
    search_fields = ['title', ]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['title', 'phone', 'tag_balance']
    fields = ['title', 'phone']
    search_fields = ['title', 'phone']


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['person', 'category', 'date_expired', 'tag_final_value', 'payment_method', 'is_paid']
    list_filter = ['category', 'person', 'is_paid', 'date_expired', 'payment_method']
    search_fields = ['title', 'person__title', 'category__title']
    fields = ['person', 'category', 'date_expired', 'is_paid', 'final_value', 'title', 'payment_method']
    actions = [action_paid, ]


@admin.register(GenericExpenseCategory)
class GenericExpenseCategoryCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'tag_balance']
    fields = ['title', ]
    search_fields = ['title', ]


@admin.register(GenericExpense)
class GenericExpenseAdmin(admin.ModelAdmin):
    list_display = ['category', 'date_expired', 'tag_final_value', 'is_paid', 'payment_method']
    list_filter = ['category', 'is_paid', 'date_expired', 'payment_method']
    search_fields = ['title', 'category__title']
    fields = ['category', 'date_expired', 'is_paid', 'final_value', 'title', 'payment_method']
    actions = [action_paid, ]
