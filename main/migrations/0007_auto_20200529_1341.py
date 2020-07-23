# Generated by Django 2.2.12 on 2020-05-29 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20200522_1217'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawlrequest',
            name='cookies_file',
            field=models.FileField(blank=True, max_length=20, null=True, upload_to=None),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='delay_secs',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='delay_type',
            field=models.CharField(blank=True, choices=[('random', 'Random'), ('fixed', 'Fixed')], max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='img_url',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='img_xpath',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='ip_type',
            field=models.CharField(blank=True, choices=[('tor', 'Tor'), ('proxy', 'Proxy')], max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='max_reqs_per_ip',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='max_reuse_rounds',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='persist_cookies',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='proxy_list',
            field=models.FileField(blank=True, max_length=20, null=True, upload_to=None),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='reqs_per_user_agent',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='sound_url',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='sound_xpath',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='tor_password',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='user_agents_file',
            field=models.FileField(blank=True, max_length=20, upload_to=None),
        ),
        migrations.AlterField(
            model_name='crawlrequest',
            name='captcha',
            field=models.CharField(choices=[('none', 'None'), ('image', 'Image'), ('sound', 'Sound')], default='1', max_length=15),
        ),
    ]