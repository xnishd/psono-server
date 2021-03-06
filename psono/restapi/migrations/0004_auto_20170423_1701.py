# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-23 17:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0003_auto_20170423_1250'),
    ]

    operations = [
        migrations.CreateModel(
            name='Yubikey_OTP',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('write_date', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
                ('yubikey_id', models.CharField(max_length=128, verbose_name='YubiKey ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='yubikey_otp', to='restapi.User')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='token',
            name='yubikey_otp_2fa',
            field=models.BooleanField(default=False, help_text='Specifies if Yubikey is required or not', verbose_name='Yubikey Required'),
        ),
        migrations.AlterField(
            model_name='google_authenticator',
            name='secret',
            field=models.CharField(max_length=256, verbose_name='secret as hex'),
        ),
    ]
