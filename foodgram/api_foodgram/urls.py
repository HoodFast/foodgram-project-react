from django.urls import path, include
from rest_framework.routers import SimpleRouter
from users.views import (
    UserViewSet,
    ChangePasswordView,
    SubscriptionViewSet,
)
from .views import (
    TagsViewSet,
    RecipesViewSet,
    IngredientsViewSet,
)

router = SimpleRouter()
router.register(r'tags', TagsViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'users', UserViewSet)
router.register(r'recipes', RecipesViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/set_password/', ChangePasswordView.as_view(
        {'post': 'update'}), name='set_password'
    ),
    path('', include('djoser.urls.authtoken')),
    path('users/subscriptions/', SubscriptionViewSet.as_view({'get': 'list'})),
    path('users/<int:pk>/subscribe/', SubscriptionViewSet.as_view(
        {'post': 'create', 'delete': 'perform_destroy'}
        ),),
    path('', include(router.urls)),
]
