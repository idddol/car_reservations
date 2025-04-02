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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    order_date = models.DateField()
    order_status = models.CharField(max_length=45)
    rental_start_date = models.DateField()
    rental_end_date = models.DateField()
    rental_cost = models.IntegerField()

    def __str__(self):
        return f"Booking {self.id} by {self.user}"


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount = models.IntegerField()
    payment_method = models.CharField(max_length=45)
    payment_status = models.CharField(max_length=45)

    def __str__(self):
        return f"Payment {self.id} - {self.payment_status}"
