# Generated by Django 4.2.5 on 2023-11-26 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0012_group_is_maintainer_can_add_to_savings'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='is_maintainer_can_add_own_transaction',
            field=models.BooleanField(default=False, verbose_name='Maintainer can add own transaction'),
        ),
    ]
