from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
    ('properties', '0001_initial'),
]


    operations = [
        migrations.AddField(
            model_name='exchangeofferimage',
            name='alt_text',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
