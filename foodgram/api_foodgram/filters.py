import django_filters 
from django.db.models import IntegerField, Value
from recipes.models import Recipes, Ingredients


class IngredientSearchFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredients
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    author = django_filters.CharFilter()
    is_favorited = django_filters.NumberFilter(method='filter')
    is_in_shopping_cart = django_filters.NumberFilter(method='filter')

    class Meta:
        model = Recipes
        fields = ['author', 'tags', 'is_in_shopping_cart', 'is_favorited']

    def filter(self, queryset, name, value):
        value = True if value == 1 else False
        recipe_ids = [
            recipe.pk for recipe in queryset if getattr(recipe, name) == value]
        if recipe_ids:
            return queryset.filter(pk__in=recipe_ids)
        return queryset.none()
