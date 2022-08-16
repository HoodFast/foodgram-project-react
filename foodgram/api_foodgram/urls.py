from django.urls import include, path
from rest_framework.routers import SimpleRouter

from users.views import ChangePasswordView, SubscriptionViewSet, UserViewSet
from .views import IngredientsViewSet, RecipesViewSet, TagsViewSet

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
    path('users/subscriptions/', SubscriptionViewSet.as_view(
        {'get': 'list'}), name='subscriptions'
    ),
    path('users/<int:pk>/subscribe/', SubscriptionViewSet.as_view(
        {'post': 'create', 'delete': 'perform_destroy'}),
        name='subscribe'
    ),
    path('', include(router.urls)),
]
