from django.contrib import admin
from .models import Cart, CartItem, Favorite, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    autocomplete_fields = ('pharmacy_medicine',)
    fields = ('pharmacy_medicine', 'quantity')
    verbose_name = "Позиция"
    verbose_name_plural = "Позиции"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'items_count', 'total_price_display')
    search_fields = ('user__username', 'user__email')
    inlines = [CartItemInline]

    def items_count(self, obj):
        return obj.items.count()

    items_count.short_description = "Позиций"

    def total_price_display(self, obj):
        return obj.total_price()

    total_price_display.short_description = "Сумма"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'pharmacy_medicine', 'quantity', 'line_total')
    autocomplete_fields = ('cart', 'pharmacy_medicine')
    search_fields = ('cart__user__username', 'pharmacy_medicine__medicine__name', 'pharmacy_medicine__pharmacy__name')

    def line_total(self, obj):
        return obj.total_price()

    line_total.short_description = "Итого"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'medicine', 'created_at')
    search_fields = ('user__username', 'medicine__name')
    autocomplete_fields = ('user', 'medicine')
    list_filter = ('created_at',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ('pharmacy_medicine',)
    fields = ('pharmacy_medicine', 'quantity', 'price_at_purchase')
    readonly_fields = ('price_at_purchase',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pharmacy', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'pharmacy', 'created_at')
    search_fields = ('user__username', 'pharmacy__name')
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'total_price', 'status_updated_at', 'created_at', 'updated_at')

    # убираем total_price из формы редактирования
    exclude = ('total_price',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'pharmacy_medicine', 'quantity', 'price_at_purchase', 'line_total')
    autocomplete_fields = ('order', 'pharmacy_medicine')
    readonly_fields = ('price_at_purchase',)

    def line_total(self, obj):
        return obj.total_price()

    line_total.short_description = "Итого"


    # total_price заказа будет только для чтения (автоматически считается); руками его вводить/редактировать нельзя.
