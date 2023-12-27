from django.db import models

from reko.producer.models import Producer


class Order(models.Model):
    producer = models.ForeignKey("producer.Producer", on_delete=models.CASCADE)
    occasion = models.ForeignKey("occasion.Occasion", on_delete=models.CASCADE)
    location = models.ForeignKey("occasion.Location", on_delete=models.PROTECT)

    order_number = models.PositiveIntegerField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()

    note = models.TextField(blank=True)

    class Meta:
        unique_together = ["producer", "occasion", "order_number"]

    def __str__(self):
        return self.full_order_number()

    def generate_order_number(self):
        # Take an exclusive lock on this producer
        Producer.objects.filter(pk=self.producer.pk).select_for_update()

        try:
            last_order_number = (
                self.producer.order_set.filter(occasion=self.occasion)
                .order_by("-order_number")[:1]
                .get()
                .order_number
            )
        except Order.DoesNotExist:
            last_order_number = 0

        self.order_number = last_order_number + 1

    def total_price(self):
        return sum(
            order_product.amount * order_product.price
            for order_product in self.orderproduct_set.all()
        )

    def full_order_number(self):
        return f"{self.location.code}{self.order_number}"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    product = models.ForeignKey("producer.Product", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
