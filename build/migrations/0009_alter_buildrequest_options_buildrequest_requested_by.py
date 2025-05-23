# Generated by Django 5.1.2 on 2024-11-09 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('build', '0008_alter_build_meta_alter_buildrequest_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='buildrequest',
            options={'ordering': ['-updated_at']},
        ),
        migrations.AddField(
            model_name='buildrequest',
            name='requested_by',
            field=models.SlugField(blank=True, null=True),
        ),
    ]
