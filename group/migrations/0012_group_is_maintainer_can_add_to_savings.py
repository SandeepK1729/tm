# Generated by Django 4.2.5 on 2023-11-26 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0011_alter_group_name_alter_group_savings_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='is_maintainer_can_add_to_savings',
            field=models.BooleanField(default=False, verbose_name='Maintainer can add to savings'),
        ),
    ]
