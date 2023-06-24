from django.db import models

# Create your models here.
class App(models.Model):

    nome = models.CharField(max_length=255)
    desc = models.TextField()
    client_id = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.nome