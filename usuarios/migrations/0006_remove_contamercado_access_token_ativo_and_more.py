# Generated by Django 4.2.2 on 2023-06-21 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0005_alter_contamercado_conta_utilizada'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contamercado',
            name='access_token_ativo',
        ),
        migrations.RemoveField(
            model_name='contamercado',
            name='conta_utilizada',
        ),
        migrations.AddField(
            model_name='contamercado',
            name='status_account',
            field=models.BooleanField(default=True, verbose_name='Conta ativa'),
        ),
    ]
