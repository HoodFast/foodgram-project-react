from rest_framework import serializers
from users.serializers import UserSerializer, RecipeShortSerializer
from recipes.models import (
    Tags,
    Ingredients,
    Recipes,
    CountIngredients,
    Favorite,
    ShoppingCart
)
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'


class CountIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = CountIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class CountIngredientsCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.FloatField()

    class Meta:
        model = CountIngredients
        fields = ('id', 'amount')


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug',)


class RecipesSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True)
    ingredients = CountIngredientsSerializer(many=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if ( 
            user.is_authenticated and
            Favorite.objects.filter(favorites_recipes=obj.id, user=user)
        ):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if (
            user.is_authenticated and
            ShoppingCart.objects.filter(shopping_recipes=obj, user=user)
        ):
            return True
        return False


class RecipesCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all(),
    )
    ingredients = CountIngredientsCreateSerializer(many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipes
        fields = '__all__'

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше 1')
        return cooking_time

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Укажите хотя бы один ингредиент')
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Укажите хотя бы один тэг')
        return tags

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredients,
                pk=ingredient['id']
            )
            count_ingredient, _ = CountIngredients.objects.get_or_create(
                ingredient=current_ingredient,
                amount=ingredient['amount']
            )
            recipe.ingredients.add(count_ingredient)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            instance.tags.clear()
            tags = validated_data.pop('tags')
            instance.tags.set(tags)
        ingredients = self.context['request'].data['ingredients']
        if ingredients:
            instance.ingredients.clear()
            for ingredient in ingredients:
                current_ingredient = get_object_or_404(
                    Ingredients,
                    pk=ingredient['id']
                )
                count_ingredient, _ = CountIngredients.objects.get_or_create(
                    ingredient=current_ingredient,
                    amount=ingredient['amount']
                )
                instance.ingredients.add(count_ingredient)
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=UserSerializer(read_only=True))
    favorites_recipes = RecipeShortSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('favorites_recipes', 'user')


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=UserSerializer(read_only=True))
    shopping_recipes = RecipeShortSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('shopping_recipes', 'user')
