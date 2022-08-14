from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.forms import CustomUserCreationForm, PasswordChangeForm
from users.models import Subscription, User

from .models import (CountIngredients, Favorite, Ingredients, Recipes,
                     ShoppingCart, Tags)


@admin.register(ShoppingCart)
class ShoppingCart(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(User)
class UserAdmin(UserAdmin):
    form = PasswordChangeForm
    add_form = CustomUserCreationForm
    list_filter = ('email', 'username')
    fieldsets = (
        (None, {'fields': (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )}),
        ('Permissions', {'fields': ('role',)})
    )
    add_fieldsets = (
        (None, {
            'fields': (
                'email', 'username', 'first_name', 'last_name', 'password1',
                'password2'
            )
        }),
    )
    search_fields = ('email', 'username')
    ordering = ('id', 'email', 'username',)
    empty_value_display = '-пусто-'


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_filter = ('name', 'author', 'tags',)
    readonly_fields = ('added_in_favorites',)
    empty_value_display = '-пусто-'

    def added_in_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Ingredients)
class IngridientsAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(CountIngredients)
class CountIngridientsAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
