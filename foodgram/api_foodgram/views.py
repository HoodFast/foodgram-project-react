import io

from django.db.models import Sum
from django.db.models.expressions import Exists, OuterRef, Value
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredients, Recipes, ShoppingCart, Tags
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import AuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientsSerializer,
                          RecipesCreateSerializer, RecipesSerializer,
                          ShoppingCartSerializer, TagsSerializer)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    filter_class = RecipeFilter
    pagination_class = None
    serializer_class = TagsSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    path_name = 'shopping_recipes__ingredients__ingredient__name'
    path_measurement_unit = (
        'shopping_recipes__ingredients__ingredient__measurement_unit'
    )
    path_amount = 'shopping_recipes__ingredients__amount'
    filterset_class = RecipeFilter
    filter_backends = [DjangoFilterBackend, ]
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = [AuthorOrReadOnly, ]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Recipes.objects.annotate(
                is_favorited=Exists(Favorite.objects.filter(
                    user=user, favorites_recipes=OuterRef('id'))
                ),
                is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                    user=user, shopping_recipes=OuterRef('id'))
                )).select_related('author', )
        else:
            return Recipes.objects.annotate(
                is_favorited=Value(False), is_in_shopping_cart=Value(False))

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesSerializer
        return RecipesCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticatedOrReadOnly],
        url_path='favorite'
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipes, pk=pk)
        user = request.user
        if request.method == 'POST':
            favorite_recipe, created = Favorite.objects.get_or_create(
                user=user, favorites_recipes=recipe
            )
            if created is True:
                serializer = FavoriteSerializer()
                return Response(
                    serializer.to_representation(instance=favorite_recipe),
                    status=status.HTTP_201_CREATED
                )
        if request.method == 'DELETE':
            Favorite.objects.filter(
                user=user,
                favorites_recipes=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticatedOrReadOnly, ]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipes, pk=pk)
        user = request.user
        if request.method == 'POST':
            recipe, created = ShoppingCart.objects.get_or_create(
                user=user, shopping_recipes=recipe
            )
            if created is True:
                serializer = ShoppingCartSerializer()
                return Response(
                    serializer.to_representation(instance=recipe),
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Рецепт уже в корзине покупок'},
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            ShoppingCart.objects.filter(
                user=user, shopping_recipes=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        x_position = 50
        y_position = 800
        shopping_cart = ShoppingCart.objects.all().filter(
            user=self.request.user
        ).select_related('shopping_recipes')
        ingredients = (
            shopping_cart.values(self.path_name, self.path_measurement_unit)
            .order_by(self.path_name).annotate(total=Sum(self.path_amount))
        )
        indent = 20
        p.drawString(x_position, y_position, 'Cписок покупок:')
        for ingredient in ingredients:
            p.drawString(
                x_position, y_position - indent,
                f'{ingredient[self.path_name]}'
                f' ({ingredient[self.path_measurement_unit]})'
                f' — {ingredient["total"]}\r\n')
            y_position -= 15
            if y_position <= 50:
                p.showPage()
                y_position = 800
        p.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='shopping_cart.pdf'
        )


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    pagination_class = None
    serializer_class = IngredientsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = IngredientSearchFilter
