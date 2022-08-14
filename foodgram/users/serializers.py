from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from users.models import User, Subscription
from recipes.models import Recipes
from django.shortcuts import get_object_or_404


class UserSerializer(serializers.ModelSerializer):
    """Сериалазер для модели User."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if (user.is_authenticated and obj.subs.filter(user=user).exists()):
            return True
        else:
            return False

    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password'))
        )
        return super().create(validated_data)


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериалазер для создания User."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {

            'password': {'write_only': True},
        }

    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password'))
        )
        return super().create(validated_data)


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=UserSerializer(read_only=True))
    author = UserSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ('author', 'user')

    def validate(self, data):
        id_author = self.context['view'].kwargs['pk']
        author = get_object_or_404(
                User,
                pk=id_author
            )
        user = self.context['request'].user
        if author == user:
            raise serializers.ValidationError(
                {'errors': ['Нельзя подписаться на самого себя']})
        if user.subscriptions.filter(author=author):
            raise serializers.ValidationError(
                {'errors': ['вы уже подписаны']})
        return data

    def create(self, validated_data):
        id_author = self.context['view'].kwargs['pk']
        author = get_object_or_404(
                User,
                pk=id_author
            )
        user = self.context['request'].user
        return Subscription.objects.create(user=user, author=author)


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscriptionSerializer(UserSerializer):
    recipes = RecipeShortSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class PasswordChangeSerializer(serializers.Serializer):
    model = User
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

