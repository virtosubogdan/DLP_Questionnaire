# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizes', '0003_auto_20150303_1432'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('quiz', 'sequence_number')]),
        ),
    ]
