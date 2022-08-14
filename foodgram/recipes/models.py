from django.db import models

from users.models import User


class Ingredients(models.Model):
    name = models.CharField(
        'name',
        unique=True,
        max_length=150,
    )
    measurement_unit = models.CharField(
        'единицы измерения',
        max_length=150,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}'


class CountIngredients(models.Model):
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='count_ingredients'
    )
    amount = models.FloatField('Колличество')

    class Meta:
        verbose_name = 'Колличество ингридиента в рецепте'
        verbose_name_plural = 'Колличество ингридиента в рецепте'

    def __str__(self):
        return f'{self.ingredient}'


class Tags(models.Model):
    name = models.CharField(
        'name',
        unique=True,
        max_length=150,
    )
    color = models.CharField(
        'Цветовой HEX-код',
        unique=True,
        max_length=7,
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Удобочитаемая метка URL',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name}'


class Recipes(models.Model):
    """Модель для рецептов"""
    tags = models.ManyToManyField(
        Tags,
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        CountIngredients,
        related_name='recipes',
    )
    name = models.CharField(
        'name',
        max_length=200,
    )
    image = models.ImageField('Изображение', blank=True)
    text = models.TextField('Рецепт')
    cooking_time = models.PositiveIntegerField('Время приготовления')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pk',)

    def __str__(self):
        return f'{self.name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    favorites_recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorites')

    class Meta:
        verbose_name = 'Подписка на рецепт'
        verbose_name_plural = 'Подписка на рецепты'

    def __str__(self):
        return f'{self.favorites_recipes}, {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    shopping_recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopping_cart')

    class Meta:
        verbose_name = 'Рецепты в избранном'
        verbose_name_plural = 'Рецепты в избранном'

    def __str__(self):
        return f'{self.shopping_recipes}, {self.user}'
