from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (CountIngredient, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.serializers import RecipeShortSerializer, UserSerializer


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class CountIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = CountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class CountIngredientsCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.FloatField()

    class Meta:
        model = CountIngredient
        fields = ('id', 'amount')


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class RecipesSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True)
    ingredients = CountIngredientsSerializer(many=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
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
        return (
            user.is_authenticated
            and Favorite.objects.filter(
                recipe=obj.id, user=user
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(
                recipe=obj, user=user
            ).exists()
        )


class RecipesCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = CountIngredientsCreateSerializer(many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше 1')
        return cooking_time

    def validation_unique(self, value, name):
        list = []
        for i in value:
            if i in list:
                raise serializers.ValidationError(
                    f'Вы добавили несколько одинаковых {name}'
                )
            else:
                list.append(i)

    def validate_ingredients(self, ingredients):
        self.validation_unique(ingredients, 'ингредиента')
        if not ingredients:
            raise serializers.ValidationError(
                'Укажите хотя бы один ингредиент')
        return ingredients

    def validate_tags(self, tags):
        self.validation_unique(tags, 'тега')
        if not tags:
            raise serializers.ValidationError(
                'Укажите хотя бы один тэг')
        return tags

    def create_ingredients(self, ingredients, recipe):
        obj = []
        for ingredient in ingredients:
            ingredient_obj = get_object_or_404(Ingredient, pk=ingredient['id'])
            exist = CountIngredient.objects.filter(
                ingredient=ingredient_obj,
                amount=ingredient['amount']
            ).exists()
            if exist:
                item = CountIngredient.objects.get(
                    ingredient=ingredient_obj,
                    amount=ingredient['amount']
                )
                recipe.ingredients.add(item)
            else:
                item = CountIngredient(
                    ingredient=ingredient_obj,
                    amount=ingredient['amount']
                )
                obj.append(item)
        if obj:
            bulk_items = CountIngredient.objects.bulk_create(obj)
            # как то bulk_create скорее усложнил код, либо я не понял как им пользоваться
            for i in bulk_items:
                recipe.ingredients.add(i)
        return recipe

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        return self.create_ingredients(ingredients, recipe)

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            instance.tags.clear()
            tags = validated_data.pop('tags')
            instance.tags.set(tags)
        ingredients = self.context['request'].data['ingredients']
        if ingredients:
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=UserSerializer(read_only=True))
    recipe = RecipeShortSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=UserSerializer(read_only=True))
    recipe = RecipeShortSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')
