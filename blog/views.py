from django.utils import timezone
from django.shortcuts import render
from .models import Car, Booking, Payment, User

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password


from .permissions import IsSelfOrAdmin, IsAdminOrReadOnly, IsOwnerCanEditOnly
from .serializers import CarSerializer, BookingSerializer, PaymentSerializer, UserSerializer


# Создание новой машины
def create_car(brand, model, year, description, price, categories):
    car = Car.objects.create(
        brand=brand,
        model=model,
        year_of_release=year,
        description=description,
        price=price
    )
    car.categories.set(categories)
    return car

# Получение всех доступных машин
def get_available_cars():
    return Car.objects.all()

# Бронирование машины
def book_car(user_id, car_id, start_date, end_date):
    user = User.objects.get(id=user_id)
    car = Car.objects.get(id=car_id)
    rental_days = (end_date - start_date).days
    rental_cost = car.price * rental_days

    booking = Booking.objects.create(
        user=user,
        car=car,
        order_date=timezone.now().date(),
        order_status='pending',
        rental_start_date=start_date,
        rental_end_date=end_date,
        rental_cost=rental_cost
    )
    return booking

# Отмена бронирования
def cancel_booking(booking_id):
    booking = Booking.objects.get(id=booking_id)
    booking.order_status = 'canceled'
    booking.save()
    return booking

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdminUser()]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [IsAuthenticated(), IsSelfOrAdmin()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), IsSelfOrAdmin()]
        return [IsAuthenticated()]

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsAdminOrReadOnly]

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()  # ← ОБЯЗАТЕЛЬНО
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()  # админ видит всё
        return Booking.objects.filter(user=user)  # обычный юзер — только свои

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()  # ← ОБЯЗАТЕЛЬНО router.register(..., ViewSet) пытается получить basename из queryset.model А если queryset = ... не задан — он не знает, как это сделать
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsOwnerCanEditOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()  # админ видит всё
        return Payment.objects.filter(booking__user=user)  # только свои платежи


#---------------------------Вьюшка для регистрации пользователя---------------------------


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                email=serializer.validated_data['email'],
                name=serializer.validated_data['name'],
                password=request.data['password']
            )
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#---------------------------Вьюшка для смены пароля пользователя---------------------------

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password_repeat = request.data.get('new_password_repeat')

        # Проверка наличия всех полей
        if not all([old_password, new_password, new_password_repeat]):
            return Response({'detail': 'All fields are required'}, status=400)

        # Проверка текущего пароля
        if not check_password(old_password, user.password):
            return Response({'detail': 'Old password is incorrect'}, status=400)

        # Проверка совпадения новых паролей
        if new_password != new_password_repeat:
            return Response({'detail': 'New passwords do not match'}, status=400)

        # Проверка длины
        if len(new_password) < 8:
            return Response({'detail': 'New password must be at least 8 characters long'}, status=400)

        # Сохраняем
        user.set_password(new_password)
        user.save()

        return Response({'detail': 'Password updated successfully'}, status=200)

#---------------------------Вьюшка для логаута пользователя---------------------------

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out"}, status=205)
        except Exception as e:
            return Response({"detail": "Invalid token"}, status=400)