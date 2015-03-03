# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizes', '0002_page_sequence_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='sequence_number',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
    ]
