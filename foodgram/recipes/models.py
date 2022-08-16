from django.db import models
from users.models import User


class Ingredient(models.Model):
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


class CountIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='count_ingredients'
    )
    amount = models.PositiveIntegerField('Колличество')

    class Meta:
        verbose_name = 'Колличество ингредиента в рецепте'
        verbose_name_plural = 'Колличество ингредиента в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'amount'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.ingredient}'


class Tag(models.Model):
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


class Recipe(models.Model):
    """Модель для рецептов"""
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        CountIngredient,
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
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe}, {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe}, {self.user}'
