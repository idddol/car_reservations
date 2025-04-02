from django.core.management.base import BaseCommand
from blog.models import User, Category, Car, Booking, Payment
from django.utils import timezone
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Заполнить базу данных тестовыми данными'

    def handle(self, *args, **kwargs):
        # Очистка текущих данных
        Payment.objects.all().delete()
        Booking.objects.all().delete()
        Car.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()

        # Пользователи
        users = []
        for i in range(1, 6):
            user = User.objects.create_user(
                email=f'user{i}@example.com',
                name=f'User{i}',
                password='password123'
            )
            users.append(user)

        # Категории
        categories = ['Economy', 'Business', 'Luxury', 'SUV']
        category_objs = []
        for cat in categories:
            category_objs.append(Category.objects.create(name=cat, description=f'{cat} cars'))

        # Автомобили
        cars = []
        brands = ['Toyota', 'BMW', 'Mercedes', 'Audi', 'Kia']
        for i in range(10):
            car = Car.objects.create(
                brand=random.choice(brands),
                model=f'Model-{i}',
                year_of_release=str(2010 + i),
                description='A comfortable car',
                price=random.randint(50, 300)
            )
            car.categories.add(random.choice(category_objs))
            cars.append(car)

        # Бронирования и платежи
        statuses = ['confirmed', 'pending', 'canceled']
        methods = ['card', 'cash', 'crypto']
        for i in range(15):
            user = random.choice(users)
            car = random.choice(cars)
            start_date = timezone.now().date() + timedelta(days=random.randint(1, 10))
            end_date = start_date + timedelta(days=random.randint(1, 7))
            booking = Booking.objects.create(
                user=user,
                car=car,
                order_date=timezone.now().date(),
                order_status=random.choice(statuses),
                rental_start_date=start_date,
                rental_end_date=end_date,
                rental_cost=car.price * (end_date - start_date).days
            )
            Payment.objects.create(
                booking=booking,
                payment_date=timezone.now().date(),
                amount=booking.rental_cost,
                payment_method=random.choice(methods),
                payment_status='completed'
            )

        self.stdout.write(self.style.SUCCESS('База данных заполнена успешно!'))
