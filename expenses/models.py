from django.db import models
from django.db.models import Sum, F

from .managers import GeneralManager

CURRENCY = '€'


class PaymentMethod(models.Model):
    title = models.CharField(unique=True, max_length=150)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '0. Payment Method'


class DefaultExpenseModel(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    date_expired = models.DateField()
    final_value = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    paid_value = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    is_paid = models.BooleanField(default=False)
    payment_method = models.ForeignKey(PaymentMethod, null=True, on_delete=models.SET_NULL)
    objects = models.Manager()
    my_query = GeneralManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.is_paid:
            self.paid_value = self.final_value
        else:
            self.paid_value = 0
        super(DefaultExpenseModel, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'

    tag_final_value.short_description = 'Value'

    def tag_is_paid(self):
        return 'Is Paid' if self.is_paid else 'Not Paid'

    tag_is_paid.short_description = 'Paid'

    @staticmethod
    def analysis(queryset):
        total_value = queryset.aggregate(Sum('final_value'))['final_value__sum'] if queryset else 0
        paid_value = queryset.filter(is_paid=False).aggregate(Sum('final_value'))['final_value__sum']\
            if queryset.filter(is_paid=False) else 0
        diff = total_value - paid_value
        category_analysis = queryset.values('category__title').annotate(total_value=Sum('final_value'),
                                                                       remaining=Sum(F('final_value')-F('paid_value'))
                                                                       ).order_by('remaining')
        return [total_value, paid_value, diff, category_analysis]

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        cate_name = request.GET.getlist('cate_name', None)
        paid_name = request.GET.getlist('paid_name', None)
        person_name = request.GET.getlist('person_name', None)

        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(category__id__in=cate_name) if cate_name else queryset
        queryset = queryset.filter(is_paid=True) if 'paid' == paid_name else queryset.filter(is_paid=False)\
            if 'not_paid' == paid_name else queryset
        if person_name:
            try:
                queryset = queryset.filter(person__id__in=person_name)
            except:
                queryset = queryset
        return queryset


class BillCategory(models.Model):
    title = models.CharField(unique=True, max_length=150)
    balance = models.DecimalField(default=0, max_digits=20, decimal_places=2)

    class Meta:
        verbose_name_plural = '1. Bill Category'

    def __str__(self):
        return self.title

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    tag_balance.short_description = 'Value'

    def update_category(self):
        queryset = self.bills.all()
        total_value = queryset.aggregate(Sum('final_value'))['final_value__sum'] if queryset else 0
        paid_value = queryset.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] \
            if queryset.filter(is_paid=True) else 0
        self.balance = total_value - paid_value
        self.save()


class Bill(DefaultExpenseModel):
    category = models.ForeignKey(BillCategory, null=True, on_delete=models.SET_NULL, related_name='bills')

    class Meta:
        verbose_name_plural = '2. Bills'
        ordering = ['-date_expired']

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f'{self.category.title} - {self.id}'
        super(Bill, self).save(*args, **kwargs)
        self.category.update_category()

    def tag_category(self):
        return f'{self.category}'


class PayrollCategory(models.Model):
    title = models.CharField(unique=True, max_length=150)
    balance = models.DecimalField(default=0, max_digits=20, decimal_places=2)

    class Meta:
        verbose_name_plural = '3. Payroll Category'

    def __str__(self):
        return self.title

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    tag_balance.short_description = 'Value'

    def update_category(self):
        queryset = self.category_payroll.all()
        total_value = queryset.aggregate(Sum('final_value'))['final_value__sum'] if queryset else 0
        paid_value = queryset.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] \
            if queryset.filter(is_paid=True) else 0
        self.balance = total_value - paid_value
        self.save()


class Person(models.Model):
    title = models.CharField(unique=True, max_length=150)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    balance = models.DecimalField(default=0, max_digits=20, decimal_places=2)

    class Meta:
        verbose_name_plural = '4. Persons'

    def __str__(self):
        return self.title

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    tag_balance.short_description = 'Value'

    def update_person(self):
        queryset = self.person_payroll.all()
        total_value = queryset.aggregate(Sum('final_value'))['final_value__sum'] if queryset else 0
        paid_value = queryset.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] \
            if queryset.filter(is_paid=True) else 0
        self.balance = total_value - paid_value
        self.save()


class Payroll(DefaultExpenseModel):
    person = models.ForeignKey(Person, null=True, on_delete=models.SET_NULL, related_name='person_payroll')
    category = models.ForeignKey(PayrollCategory, null=True, on_delete=models.SET_NULL, related_name='category_payroll')

    class Meta:
        verbose_name_plural = '5. Payroll'
        ordering = ['-date_expired']

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f'{self.person.title} - {self.id}'
        super(Payroll, self).save(*args, **kwargs)
        self.person.update_person()
        self.category.update_category()

    def tag_category(self):
        return f'{self.person} - {self.category}'


class GenericExpenseCategory(models.Model):
    title = models.CharField(unique=True, max_length=150)
    balance = models.DecimalField(default=0, max_digits=20, decimal_places=2)

    class Meta:
        verbose_name_plural = '6. Expense Category'

    def __str__(self):
        return self.title

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    tag_balance.short_description = 'Value'

    def update_category(self):
        queryset = self.category_expenses.all()
        total_value = queryset.aggregate(Sum('final_value'))['final_value__sum'] if queryset else 0
        paid_value = queryset.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] \
            if queryset.filter(is_paid=True) else 0
        self.balance = total_value - paid_value
        self.save()


class GenericExpense(DefaultExpenseModel):
    category = models.ForeignKey(GenericExpenseCategory, null=True, on_delete=models.SET_NULL,
                                 related_name='category_expenses')

    class Meta:
        verbose_name_plural = '7. Generic Expenses'
        ordering = ['-date_expired']

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f'{self.title}'
        super(GenericExpense, self).save(*args, **kwargs)
        self.category.update_category()

    def tag_category(self):
        return f'{self.category}'
