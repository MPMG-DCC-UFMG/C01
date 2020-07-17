# Generated by Django 3.0.7 on 2020-07-03 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_auto_20200629_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crawlrequest',
            name='antiblock_mask_type',
            field=models.CharField(blank=True, choices=[('none', 'None'), ('ip', 'IP rotation'), ('user_agent', 'User-agent rotation'), ('cookies', 'Use cookies')], default='none', max_length=15, null=True),
        ),
    ]
