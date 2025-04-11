from rest_framework import serializers
from .models import Car, Booking, Payment, User


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


from rest_framework import serializers
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'name']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False  # Необязателен при обновлении
            },
            'email': {'required': False},
            'username': {'required': False},
            'name': {'required': False}
        }

    def create(self, validated_data):
        # Создание пользователя с хешированием пароля
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Хеширование пароля при обновлении (если он передан)
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)

    def to_representation(self, instance):
         # Убираем пароль из любого ответа API
         representation = super().to_representation(instance)
         representation.pop('password', None)
         return representation