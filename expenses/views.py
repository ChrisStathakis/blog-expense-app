from django.shortcuts import render, get_list_or_404
from django.views.generic import TemplateView
from .models import *


class HomepageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)

        bills = Bill.my_query.get_queryset().this_year()
        payrolls = Payroll.my_query.get_queryset().this_year()
        expenses = GenericExpense.my_query.get_queryset().this_year()
        context.update({'bills': bills,
                        'payroll': payrolls,
                        'expenses': expenses
                        })
        return context