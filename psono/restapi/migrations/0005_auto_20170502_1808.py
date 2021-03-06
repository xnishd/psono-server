# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 18:08
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0004_auto_20170423_1701'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='device_description',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='token',
            name='device_fingerprint',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='token',
            name='id',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
        ),
    ]
