# Generated migration for teleappointment functionality

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0004_labfacility_labtest_labfacilityimage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='queue',
            name='appointment_type',
            field=models.CharField(
                choices=[('in_person', 'In-Person Appointment'), ('telemedicine', 'Telemedicine Appointment')], 
                default='in_person', 
                help_text='Type of appointment - in-person or telemedicine', 
                max_length=20
            ),
        ),
        migrations.CreateModel(
            name='TeleAppointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting_url', models.URLField(blank=True, help_text='Video call meeting URL', null=True)),
                ('meeting_id', models.CharField(blank=True, help_text='Meeting ID for the video call', max_length=100, null=True)),
                ('meeting_password', models.CharField(blank=True, help_text='Meeting password if required', max_length=50, null=True)),
                ('platform', models.CharField(
                    choices=[
                        ('zoom', 'Zoom'), 
                        ('google_meet', 'Google Meet'), 
                        ('microsoft_teams', 'Microsoft Teams'), 
                        ('webrtc', 'WebRTC (Browser-based)'), 
                        ('other', 'Other')
                    ], 
                    default='webrtc', 
                    max_length=20
                )),
                ('scheduled_start_time', models.DateTimeField(help_text='Scheduled start time for the video call')),
                ('actual_start_time', models.DateTimeField(blank=True, null=True)),
                ('actual_end_time', models.DateTimeField(blank=True, null=True)),
                ('patient_device_info', models.JSONField(blank=True, default=dict, help_text="Patient's device and browser info")),
                ('connection_quality', models.CharField(
                    blank=True, 
                    choices=[
                        ('excellent', 'Excellent'), 
                        ('good', 'Good'), 
                        ('fair', 'Fair'), 
                        ('poor', 'Poor')
                    ], 
                    max_length=20, 
                    null=True
                )),
                ('pre_call_instructions', models.TextField(
                    default='Please ensure you have a stable internet connection and are in a quiet, private space for your appointment.', 
                    help_text='Instructions sent to patient before the call'
                )),
                ('technical_notes', models.TextField(blank=True, help_text='Technical notes or issues during the call')),
                ('reminder_sent_at', models.DateTimeField(blank=True, null=True)),
                ('meeting_link_sent_at', models.DateTimeField(blank=True, null=True)),
                ('tele_status', models.CharField(
                    choices=[
                        ('scheduled', 'Scheduled'), 
                        ('ready', 'Ready to Start'), 
                        ('in_progress', 'Video Call in Progress'), 
                        ('completed', 'Completed'), 
                        ('cancelled', 'Cancelled'), 
                        ('no_show', 'Patient No Show'), 
                        ('technical_issue', 'Technical Issue')
                    ], 
                    default='scheduled', 
                    max_length=20
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('queue_entry', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE, 
                    related_name='tele_appointment', 
                    to='patients.queue'
                )),
            ],
            options={
                'ordering': ['scheduled_start_time'],
            },
        ),
    ]