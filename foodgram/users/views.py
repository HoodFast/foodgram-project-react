from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import SAFE_METHODS, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from users.models import Subscription, User

from .serializers import (CreateUserSerializer, PasswordChangeSerializer,
                          SubscriptionCreateSerializer, SubscriptionSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Viewset для модели  User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ('list', 'create'):
            self.permission_classes = (AllowAny,)
        return super(UserViewSet, self).get_permissions()

    def get_object(self):
        return self.request.user


class ChangePasswordView(viewsets.ModelViewSet):
    serializer_class = PasswordChangeSerializer
    model = User

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(
                serializer.data.get("current_password")
            ):
                return Response(
                    {"current_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Подписка на автора"""

    def get_queryset(self):
        return User.objects.filter(subs__user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return SubscriptionSerializer
        return SubscriptionCreateSerializer

    def perform_destroy(self, instance, pk):
        author = get_object_or_404(
            User,
            pk=pk
        )
        object = get_object_or_404(
            Subscription,
            author=author,
            user=self.request.user
        )
        object.delete()
        return Response(status=HTTP_204_NO_CONTENT)
