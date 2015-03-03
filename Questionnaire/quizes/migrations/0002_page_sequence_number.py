# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='sequence_number',
            field=models.IntegerField(default=1, unique=True),
            preserve_default=True,
        ),
    ]
