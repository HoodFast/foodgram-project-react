import django_filters

from recipes.models import Ingredient, Recipe


class IngredientSearchFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    author = django_filters.CharFilter()
    is_favorited = django_filters.NumberFilter(method='filter')
    is_in_shopping_cart = django_filters.NumberFilter(method='filter')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_in_shopping_cart', 'is_favorited']

    def filter(self, queryset, name, value):
        if name == 'is_favorited':
            recipes = (queryset.values_list(
                'id', flat=True).filter(is_favorited__startswith=value))
        elif name == 'is_in_shopping_cart':
            recipes = (queryset.values_list(
                'id', flat=True).filter(is_in_shopping_cart__startswith=value))
        if recipes:
            return queryset.filter(pk__in=recipes)
        return queryset.none()
