from django.db import models



# Create your models here.
class Márka(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return(self.name)

class bestseller(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return(self.name)

class Shoe(models.Model):
    name = models.CharField(max_length=200)
    price = models.CharField(max_length=200)
    created =  models.DateTimeField(auto_now_add=True)
    rendszerezes = models.DecimalField(max_digits = 10, decimal_places = 1, null=True)
    cég =  models.CharField(max_length=200, null=True)
    image = models.CharField(max_length=200)
    image_2 = models.CharField(max_length=200)
    link = models.CharField(max_length=200, null=True)
    akcios_ár = models.CharField(max_length=200)


    def __str__(self):
        return self.name

