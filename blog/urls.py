from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CarViewSet, BookingViewSet, PaymentViewSet, UserViewSet, RegisterView, ChangePasswordView,
                    LogoutView,register_page, login_page, profile_page, cars_page, booking_page, payment_page, delete_booking)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

router = DefaultRouter()
router.register(r'cars', CarViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [

    #API
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'), # регистрация пользователя
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # логин + получение JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # обновление access-токена
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'), #проверка валидности access-токена
    path('change-password/', ChangePasswordView.as_view(), name='change-password'), #смена пароля юзера
    path('logout/', LogoutView.as_view(), name='logout'), #выход из системы пользователя

    # HTML-страницы
    path('site/register/', register_page, name='register-page'),
    path('site/login/', login_page, name='login-page'),
    path('site/profile/', profile_page, name='profile-page'),
    path('site/cars/', cars_page, name='cars-page'),
    path('site/booking/<int:car_id>/', booking_page, name='booking-page'),
    path('site/payment/<int:booking_id>/', payment_page, name='payment-page'),
    path('site/booking/<int:booking_id>/delete/', delete_booking, name='delete-booking'),

    path('users/me/', UserViewSet.as_view({'get': 'me'})),
]
