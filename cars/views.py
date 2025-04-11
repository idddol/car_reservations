from django.utils import timezone
from django.shortcuts import render
from rest_framework.permissions import IsAdminUser

from cars.models import Car, Booking, Payment, User
from rest_framework import viewsets
from .serializers import CarSerializer, BookingSerializer, PaymentSerializer, UserSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model


User = get_user_model()
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


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
