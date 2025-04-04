import os
import django
import random
import sys
from faker import Faker
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CarReservations.settings")
django.setup()

from cars.models import User, Category, Car, Booking, Payment

fake = Faker('ru_RU')

def clear_data():
    print("Удаляю старые данные...")
    Payment.objects.all().delete()
    Booking.objects.all().delete()
    Car.objects.all().delete()
    Category.objects.all().delete()
    User.objects.all().delete()
    print("Очистка завершена")

def generate_data():
    print("Генерация тестовых данных...")

    CATEGORY_NAMES = ["Эконом", "Премиум", "Седан", "Универсал", "Кроссовер", "Внедорожник", "Минивэн"]
    categories = []
    for cat_name in CATEGORY_NAMES:
        cat = Category.objects.create(
            name=cat_name,
            description=f"{cat_name} класс автомобилей"
        )
        categories.append(cat)

    users = []
    for _ in range(10):
        user = User.objects.create_user(
            email=fake.unique.email(),
            name=fake.name(),
            password="test1234"
        )
        users.append(user)

    BRANDS_MODELS = {
        "Toyota": ["Camry", "Corolla", "RAV4"],
        "BMW": ["X5", "3 Series", "5 Series"],
        "Kia": ["Rio", "Sportage", "Ceed"],
        "Hyundai": ["Elantra", "Solaris", "Tucson"],
        "Mercedes": ["C-Class", "E-Class", "GLA"],
        "Volkswagen": ["Golf", "Passat", "Tiguan"],
    }

    cars = []
    for _ in range(15):
        brand = random.choice(list(BRANDS_MODELS.keys()))
        model = random.choice(BRANDS_MODELS[brand])
        price = random.randint(1500, 6000)

        car = Car.objects.create(
            brand=brand,
            model=model,
            year_of_release=str(random.randint(2015, 2023)),
            description=fake.text(max_nb_chars=100),
            price=price,
        )
        car.categories.set(random.sample(categories, k=random.randint(1, 2)))
        cars.append(car)

    bookings = []
    for _ in range(20):
        user = random.choice(users)
        car = random.choice(cars)
        start_date = fake.date_between(start_date='-30d', end_date='today')
        rental_days = random.randint(1, 10)
        end_date = start_date + timedelta(days=rental_days)
        cost = car.price * rental_days

        booking = Booking.objects.create(
            user=user,
            car=car,
            order_date=start_date - timedelta(days=1),
            order_status=random.choice(['в обработке', 'подтверждено', 'отменено']),
            rental_start_date=start_date,
            rental_end_date=end_date,
            rental_cost=cost
        )
        bookings.append(booking)

    for booking in bookings:
        Payment.objects.create(
            booking=booking,
            payment_date=booking.order_date + timedelta(days=1),
            amount=booking.rental_cost,
            payment_method=random.choice(['карта', 'наличные', 'онлайн']),
            payment_status=random.choice(['оплачено', 'не оплачено'])
        )

    print("Тестовые данные успешно созданы!")

if __name__ == "__main__":
    if "clear" in sys.argv:
        clear_data()
    elif "fill" in sys.argv:
        clear_data()
        generate_data()
    else:
        print("python fill_test_data.py clear  — удалить все тестовые данные\n  python fill_test_data.py fill   — удалить и заполнить тестовыми данными")
