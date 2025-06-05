from django.contrib import admin
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Solicitor, Instruction, Document, Firm, ChatMessage
import logging
from django.core.mail import send_mail
from django.conf import settings  # ✅ Ensure settings are available

logger = logging.getLogger(__name__)

# ✅ Register Firm Model
@admin.register(Firm)
class FirmAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "contact_number", "state")
    search_fields = ("name", "contact_email", "contact_number")
    list_filter = ("state",)


# ✅ Register Solicitor Model
@admin.register(Solicitor)
class SolicitorAdmin(admin.ModelAdmin):
    list_display = ("instructing_solicitor", "get_firm_name", "office_phone", "mobile_phone", "profession")
    search_fields = ("instructing_solicitor", "firm__name")
    list_filter = ("firm",)

    def get_firm_name(self, obj):
        return obj.firm.name if obj.firm else "No Firm Assigned"
    get_firm_name.short_description = "Firm Name"


# ✅ Register Instruction Model
@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    list_display = ("file_reference", "purchaser_name", "property_address", "settlement_date", "status", "solicitor")
    search_fields = ("purchaser_name", "property_address", "seller_name", "file_reference")
    list_filter = ("status", "settlement_date", "solicitor")
    list_editable = ("status",)


# ✅ Register Document Model
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "instruction", "uploaded_at")
    search_fields = ("name", "instruction__file_reference")
    list_filter = ("uploaded_at",)


# ✅ Register Chat Messages in Admin
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("sender_name", "recipient_name", "message_preview", "timestamp", "reply_button")
    search_fields = ("sender__username", "recipient__username", "message")
    list_filter = ("timestamp",)
    ordering = ("-timestamp",)
    readonly_fields = ('is_read',)  # Make is_read read-only to prevent manual toggling

    def sender_name(self, obj):
        """Display sender name as 'Settlex' if admin sent the message."""
        return "Settlex (Admin)" if obj.sender.is_superuser else (obj.sender.get_full_name() or obj.sender.username)
    sender_name.short_description = "Sender"

    def recipient_name(self, obj):
        """Display recipient name properly."""
        return obj.recipient.get_full_name() or obj.recipient.username
    recipient_name.short_description = "Recipient"

    def message_preview(self, obj):
        """Display a short preview of the message in Admin."""
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = "Message Preview"

    def reply_button(self, obj):
        """Generate a wider, styled reply button for admin messages."""
        return format_html(
            '<a href="{}" class="chat-reply-button" '
            'style="display:inline-block; width:120px; padding:10px 15px; '
            'font-size:14px; text-align:center; background-color:#007bff; '
            'color:white; border:none; border-radius:6px; cursor:pointer; '
            'transition:0.3s ease-in-out; text-decoration:none;">Reply</a>',
            reverse("admin:chat_reply", args=[obj.id])
        )
    reply_button.short_description = "Reply"

    def get_urls(self):
        """Add custom admin URL for replying to messages."""
        urls = super().get_urls()
        custom_urls = [
            path('chatmessage/<int:message_id>/reply/', self.admin_site.admin_view(self.reply_view), name="chat_reply"),
        ]
        return custom_urls + urls

    @method_decorator(csrf_exempt)
    def reply_view(self, request, message_id):
        """Handle message replies from admin."""
        message = get_object_or_404(ChatMessage, id=message_id)

        if request.method == "POST":
            reply_text = request.POST.get("reply_message", "").strip()

            if reply_text:
                # ✅ Send reply as "Settlex (Admin)"
                ChatMessage.objects.create(
                    sender=request.user,  # Admin user
                    recipient=message.sender,  # Replying back to sender
                    message=reply_text
                )

                messages.success(request, "Reply sent successfully!")
                return HttpResponseRedirect(reverse("admin:settlements_app_chatmessage_changelist"))

        # ✅ Fix: Add "subtitle" to context
        context = {
            "message": message,
            "subtitle": "Replying to Chat Message",  # ✅ Fixes the missing variable error
        }
        return render(request, "admin/chat_reply.html", context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Automatically mark message as read when admin views it."""
        message = self.get_object(request, object_id)
        if message and not message.is_read and request.user.is_staff:
            message.is_read = True
            message.save()
        return super().change_view(request, object_id, form_url, extra_context)

    class Media:
        js = ('admin/js/jquery.init.js',)


# ✅ Define a custom action to send activation email
def send_activation_email(modeladmin, request, queryset):
    for user in queryset:
        if not user.is_active:
            messages.warning(request, f"User {user.email} is not active. Activate the user before sending email.")
            continue  # Skip inactive users

        # ✅ Send activation email
        subject = "Your SettleX Account Has Been Activated"
        message = f"""
        Dear {user.first_name} {user.last_name},

        Your account has been successfully activated. You can now log in to SettleX.

        Login here: https://settlex.onestoplegal.com.au

        Regards,
        SettleX Team
        """

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.success(request, f"Activation email sent to {user.email}")

        except Exception as e:
            messages.error(request, f"Failed to send activation email to {user.email}: {e}")

send_activation_email.short_description = "✅ Send Activation Email"

# ✅ Register the User model with the custom admin action
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_active")
    list_filter = ("is_active",)
    actions = [send_activation_email]  # ✅ Add the action to the dropdown

# ✅ Unregister default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)