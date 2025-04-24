from rest_framework.decorators import action
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

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate


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

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

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
        booking = serializer.save(user=self.request.user)

        # Создаём платёж для этой брони
        Payment.objects.create(
            booking=booking,
            amount=booking.rental_cost,
            payment_method='card',
            payment_status='uncompleted'
        )


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



#---------------------------Страницы---------------------------
def register_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return redirect('register-page')

        user = User.objects.create_user(email=email, name=name, password=password)
        messages.success(request, 'Регистрация прошла успешно! Теперь войдите')
        return redirect('login-page')

    return render(request, 'blog/register.html')


def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            request.session['access'] = str(refresh.access_token)
            request.session['refresh'] = str(refresh)
            request.session['user_id'] = user.id
            return redirect('profile-page')
        else:
            messages.error(request, 'Неверный email или пароль')

    return render(request, 'blog/login.html')


def profile_page(request):
    return render(request, 'blog/profile.html')

def cars_page(request):
    cars = Car.objects.all()
    return render(request, 'blog/cars.html', {'cars': cars})


def booking_page(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'blog/booking.html', {'car': car})

def payment_page(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        payment = Payment.objects.get(booking=booking)
    except Payment.DoesNotExist:
        payment = None

    return render(request, 'blog/payment.html', {
        'booking_id': booking_id,
        'payment': payment
    })

def delete_booking(request, booking_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login-page')  # если не авторизован

    booking = get_object_or_404(Booking, id=booking_id)

    if booking.user.id != user_id:
        return redirect('profile-page')  # нельзя удалять чужую бронь

    if request.method == 'POST':
        booking.delete()  # удалит и платёж из-за on_delete=models.CASCADE
        return redirect('profile-page')