from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product, Customer




def say_hello(request):
    customers = Customer.objects.order_by('-first_name')
    return render(request, 'hello.html', {'name': 'Mazwin', 'customers': customers})

# Create your views here.
