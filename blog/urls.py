from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarViewSet, BookingViewSet, PaymentViewSet, UserViewSet, RegisterView, ChangePasswordView, LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'cars', CarViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Регистрация и JWT
    path('register/', RegisterView.as_view(), name='register'), # регистрация пользователя
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # логин + получение JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # обновление access-токена
    path('change-password/', ChangePasswordView.as_view(), name='change-password'), #смена пароля юзера
    path('logout/', LogoutView.as_view(), name='logout'), #выход из системы пользователя
]