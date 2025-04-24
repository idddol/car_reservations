from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Поле email обязательно к заполнению')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)  # хэширование пароля
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=45)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

class Category(models.Model):
    name = models.CharField(max_length=45)
    description = models.TextField()

    def __str__(self):
        return self.name


class Car(models.Model):
    brand = models.CharField(max_length=45)
    model = models.CharField(max_length=45)
    year_of_release = models.CharField(max_length=45)
    description = models.TextField()
    price = models.IntegerField()
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return f"{self.brand} {self.model}"


class Booking(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    order_date = models.DateField()
    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default= 'pending'  # Статус по умолчанию
    )
    rental_start_date = models.DateField()
    rental_end_date = models.DateField()
    rental_cost = models.IntegerField()

    def __str__(self):
        return f"Booking {self.id} by {self.user}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('uncompleted', 'Uncompleted'),
        ('completed', 'Completed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('crypto', 'Crypto'),
    ]

    booking = models.ForeignKey(
        'Booking',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    payment_date = models.DateField(auto_now_add=True)
    amount = models.IntegerField(blank=True, null=True)
    payment_method = models.CharField(
        max_length=45,
        choices=PAYMENT_METHOD_CHOICES
    )
    payment_status = models.CharField(
        max_length=45,
        choices=PAYMENT_STATUS_CHOICES,
        default='uncompleted'
    )

    def save(self, *args, **kwargs):
        # Автоматически устанавливаем сумму из бронирования
        if not self.amount and self.booking:
            self.amount = self.booking.rental_cost
        super().save(*args, **kwargs)

    def str(self):
        return f"Payment {self.id} - {self.payment_status}"
