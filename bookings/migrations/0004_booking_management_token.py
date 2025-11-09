import uuid
from django.db import migrations, models


def populate_management_tokens(apps, schema_editor):
    Booking = apps.get_model('bookings', 'Booking')
    for booking in Booking.objects.all():
        booking.management_token = uuid.uuid4()
        booking.save(update_fields=['management_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0003_alter_booking_attendee_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='management_token',
            field=models.UUIDField(editable=False, null=True),
        ),
        migrations.RunPython(populate_management_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='booking',
            name='management_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]

