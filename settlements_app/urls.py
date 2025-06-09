from django.urls import path, include, reverse_lazy  # ✅ make sure 'path' is included
from django.contrib.auth import views as auth_views

from .views import (
    home, logout_view, register, new_instruction, upload_documents,
    my_settlements, solicitor_dashboard, edit_instruction, delete_instruction,
    view_settlement,
    long_poll_messages, check_new_messages, send_message, reply_view,
    mark_messages_read, check_typing_status, upload_chat_file, delete_message,
    CustomPasswordResetView
)
from two_factor.views import LoginView, SetupView  # ✅ Use built-in 2FA views

app_name = 'settlements_app'

urlpatterns = [
    path("", home, name="home"),
    path("login/", LoginView.as_view(), name="login"),
    # path("account/two_factor/setup/", SetupView.as_view(), name="two_factor_setup"),
    path("logout/", logout_view, name="logout"),
    path("register/", register, name="register"),
    path("password-reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("new-instruction/", new_instruction, name="new_instruction"),
    path("upload-documents/<int:instruction_id>/", upload_documents, name="upload_documents"),
    path("my-settlements/", my_settlements, name="my_settlements"),
    path("dashboard/", solicitor_dashboard, name="solicitor_dashboard"),
    path("edit-instruction/<int:instruction_id>/", edit_instruction, name="edit_instruction"),
    path("delete-instruction/<int:instruction_id>/", delete_instruction, name="delete_instruction"),
    path("settlement/<int:settlement_id>/", view_settlement, name="view_settlement"),


    # Chat
    path("long-poll-messages/", long_poll_messages, name="long_poll_messages"),
    path("check-new-messages/", check_new_messages, name="check_new_messages"),
    path("send-message/", send_message, name="send_message"),
    path("reply/<int:message_id>/", reply_view, name="reply_view"),
    path("mark-messages-read/", mark_messages_read, name="mark_messages_read"),
    path("check-typing-status/", check_typing_status, name="check_typing_status"),
    path("upload-file/", upload_chat_file, name="upload_chat_file"),
    path("delete-message/", delete_message, name="delete_message"),

    # Password reset
    path("password-reset/", CustomPasswordResetView.as_view(
        template_name="settlements_app/password_reset.html",
        success_url=reverse_lazy("settlements_app:password_reset_done"),
        email_template_name="settlements_app/password_reset_email.html",
        subject_template_name="settlements_app/password_reset_subject.txt"
    ), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="settlements_app/password_reset_done.html"
    ), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="settlements_app/password_reset_confirm.html",
        success_url=reverse_lazy("settlements_app:password_reset_complete")
    ), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="settlements_app/password_reset_complete.html"
    ), name="password_reset_complete"),
]