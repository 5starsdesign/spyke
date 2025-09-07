from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0003_add_lat_lng_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="exchangeoffer",
            name="slug",
            field=models.SlugField(max_length=200, unique=True, blank=True),
        ),
    ]
