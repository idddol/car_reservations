from django.db import models


class User(models.Model):
    name = models.CharField(max_length=45)
    email = models.EmailField(max_length=45, unique=True)
    password = models.CharField(max_length=45)

    def __str__(self):
        return self.name


class Admin(models.Model):
    name = models.CharField(max_length=45)
    email = models.EmailField(max_length=45, unique=True)
    password = models.CharField(max_length=45)

    def __str__(self):
        return self.name


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
