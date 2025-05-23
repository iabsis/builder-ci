# Generated by Django 5.1.2 on 2024-11-13 10:02

import flow.validator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flow', '0004_method_description_alter_method_stop_on_failure'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flow',
            name='version_file',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='flow',
            name='version_regex',
            field=models.CharField(blank=True, help_text='Define regex with one capturing group.', max_length=150, null=True, validators=[flow.validator.validate_regex_pattern]),
        ),
    ]
