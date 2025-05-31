# blog/serializers.py

# blog/serializers.py

from rest_framework import serializers
from .models import Car, Booking, Payment, User, CarImage
from django.utils import timezone

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'image_url', 'car']

class CarSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = '__all__'

class CarShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['brand', 'model']

class BookingWriteSerializer(serializers.ModelSerializer):
    car = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all())

    class Meta:
        model = Booking
        fields = '__all__'
        extra_kwargs = {
            'order_date': {'required': False},
            'order_status': {'required': False},
            'rental_cost': {'required': False},
            'user': {'required': False},
        }

    def validate(self, data):
        start_date = data['rental_start_date']
        end_date = data['rental_end_date']
        if start_date >= end_date:
            raise serializers.ValidationError("Арендовать автомобиль можно на срок, составляющий минимум 1 день.")
        return data

    def create(self, validated_data):
        validated_data['order_date'] = timezone.now().date()
        validated_data['order_status'] = 'pending'
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user

        car = validated_data.get('car')
        start_date = validated_data['rental_start_date']
        end_date = validated_data['rental_end_date']
        days = (end_date - start_date).days
        validated_data['rental_cost'] = car.price * days

        return super().create(validated_data)


class BookingReadSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        extra_kwargs = {
            'payment_date': {'required': False},
            'amount': {'required': False},
            'payment_status': {'required': False},
        }

    def validate_booking(self, value):
        # Проверяем, что бронирование принадлежит текущему пользователю
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("Вы можете создавать платежи только для своих бронирований")
        return value

    def create(self, validated_data):
        # Устанавливаем текущую дату как order_date
        validated_data['payment_date'] = timezone.now().date()

        # Устанавливаем статус, только если он явно не передан из запроса
        if 'payment_status' not in validated_data:
            validated_data['payment_status'] = 'uncompleted'
        validated_data['amount'] = validated_data['booking'].rental_cost

        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'is_staff']

