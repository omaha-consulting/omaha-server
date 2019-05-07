# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0006_auto_20151209_1040'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackDescription',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('feedback.feedback',),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='page_url',
            field=models.CharField(max_length=2048, null=True, blank=True),
        ),
    ]
