from typing import Any
from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from tags.models import TaggedItem
from . import models
from django.urls import reverse
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')
        ]
    
    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)



class TagInline(GenericTabularInline):
    model = TaggedItem
    autocomplete_fields = ['tag']

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['title____istartswith']
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    actions = ['clear_inventory']
    inlines = [TagInline]
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 10
    list_select_related = ['collection']

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'
    
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated.',
            messages.ERROR
        )
        

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    list_per_page = 10
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 2

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer']


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['featured_product']
    list_display = ['title', 'products_count']
    search_fields = ['title']


    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (reverse('admin:store_product_changelist')
               + '?'
               + urlencode({
                   'collection__id': str(collection.id)
               }))
        return format_html('<a href="{}">{}</a>',url, collection.products_count)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )



# Register your models here.
