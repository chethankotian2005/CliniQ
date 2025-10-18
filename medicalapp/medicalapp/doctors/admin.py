from django.contrib import admin
from .models import Doctor, DoctorSchedule, DoctorLeave
from django import forms
from django.core.mail import send_mail
from django.contrib import messages

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'employee_id', 'specialization', 'department', 'is_available', 'is_active', 'total_patients_seen']
    list_filter = ['specialization', 'department', 'is_available', 'is_active', 'created_at']
    search_fields = ['name', 'employee_id', 'phone_number', 'email', 'license_number']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at', 'last_active', 'total_patients_seen']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'employee_id', 'phone_number', 'email')
        }),
        ('Professional Information', {
            'fields': ('specialization', 'license_number', 'years_of_experience', 'qualification')
        }),
        ('Department & Availability', {
            'fields': ('department', 'is_available', 'is_active')
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time', 'lunch_start', 'lunch_end')
        }),
        ('Statistics', {
            'fields': ('total_patients_seen', 'average_consultation_time'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_active'),
            'classes': ('collapse',)
        }),
    )
    actions = ['approve_doctors']

    # Show doctor schedules inline for easy editing
    inlines = []

    def approve_doctors(self, request, queryset):
        """Admin action to approve selected doctors and activate their user accounts"""
        count = 0
        for doctor in queryset:
            activated_any = False
            changed_fields = []

            # Activate doctor record if needed
            if not doctor.is_active:
                doctor.is_active = True
                changed_fields.append('is_active')

            # When approving, mark as available by default
            if not doctor.is_available:
                doctor.is_available = True
                if 'is_available' not in changed_fields:
                    changed_fields.append('is_available')

            if changed_fields:
                doctor.save(update_fields=changed_fields)
                activated_any = True

            # Activate linked user account if needed
            if doctor.user and not doctor.user.is_active:
                doctor.user.is_active = True
                doctor.user.save(update_fields=['is_active'])
                activated_any = True

            if activated_any:
                # Send notification email (best-effort)
                try:
                    send_mail(
                        subject='Your CliniQ account has been approved',
                        message=f'Hello {doctor.name},\n\nYour CliniQ doctor account has been approved by the admin team. You can now login to the portal.\n\nRegards,\nCliniQ Team',
                        from_email=None,
                        recipient_list=[doctor.email],
                        fail_silently=True,
                    )
                except Exception:
                    # don't block approval if email fails
                    pass

                count += 1

        self.message_user(request, f"Approved {count} doctor(s) and activated their user accounts.", level=messages.SUCCESS)
    approve_doctors.short_description = 'Approve selected doctors and activate accounts'


class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = '__all__'
        widgets = {
            'start_time': forms.TimeInput(attrs={'class': 'timewheel', 'autocomplete': 'off'}),
            'end_time': forms.TimeInput(attrs={'class': 'timewheel', 'autocomplete': 'off'}),
            'lunch_start': forms.TimeInput(attrs={'class': 'timewheel', 'autocomplete': 'off'}),
            'lunch_end': forms.TimeInput(attrs={'class': 'timewheel', 'autocomplete': 'off'}),
        }

    class Media:
        css = {
            'all': ('admin/time_wheel.css',)
        }
        js = ('admin/time_wheel.js',)

    def clean(self):
        cleaned = super().clean()
        from datetime import datetime
        import datetime as _dt

        # Helper: parse time-like inputs and convert 'now' -> IST current time
        def normalize_time(val):
            if val in (None, ''):
                return None
            # If already a time object, return
            if hasattr(val, 'hour') and hasattr(val, 'minute'):
                return val
            s = str(val).strip().lower()
            if s == 'now':
                # compute IST current time
                try:
                    from zoneinfo import ZoneInfo
                    ist = ZoneInfo('Asia/Kolkata')
                    now_dt = datetime.now(tz=ist)
                except Exception:
                    try:
                        import pytz
                        ist = pytz.timezone('Asia/Kolkata')
                        now_dt = datetime.now(tz=ist)
                    except Exception:
                        now_dt = datetime.now()
                return _dt.time(now_dt.hour, now_dt.minute, now_dt.second)

            # Try parsing common formats
            for fmt in ('%H:%M:%S', '%H:%M'):
                try:
                    parsed = datetime.strptime(s, fmt).time()
                    return parsed
                except Exception:
                    pass

            # Last resort: let Django form field validation handle it (raise)
            return val

        for field_name in ('start_time', 'end_time', 'lunch_start', 'lunch_end'):
            if field_name in self.fields:
                raw = cleaned.get(field_name)
                cleaned[field_name] = normalize_time(raw)

        return cleaned


class DoctorScheduleInline(admin.TabularInline):
    model = DoctorSchedule
    form = DoctorScheduleForm
    extra = 1
    fields = ('weekday', 'start_time', 'end_time', 'lunch_start', 'lunch_end', 'is_available')


# Re-register DoctorAdmin to include inline and on-duty column
admin.site.unregister(Doctor)


@admin.register(Doctor)
class DoctorAdminWithSchedule(DoctorAdmin):
    inlines = [DoctorScheduleInline]
    list_display = ['name', 'employee_id', 'specialization', 'department', 'is_available', 'is_active', 'on_duty_now', 'total_patients_seen']

    def on_duty_now(self, obj):
        try:
            return obj.is_on_duty()
        except Exception:
            return False
    on_duty_now.boolean = True
    on_duty_now.short_description = 'On Duty Now'

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'get_weekday_display', 'start_time', 'end_time', 'is_available']
    list_filter = ['weekday', 'is_available']
    search_fields = ['doctor__name']
    ordering = ['doctor', 'weekday']

@admin.register(DoctorLeave)
class DoctorLeaveAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'leave_type', 'start_date', 'end_date', 'is_approved', 'created_at']
    list_filter = ['leave_type', 'is_approved', 'start_date', 'created_at']
    search_fields = ['doctor__name', 'reason']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
