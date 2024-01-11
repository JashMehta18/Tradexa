from re import template
from django.contrib import admin
from django.urls import path,include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('Base.urls', namespace='Base')),
    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='passwordResetConfirm.html'
        ),
         name='password_reset_confirm'),
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name='passwordReset.html'),name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name='passwordResetDone.html'),name="password_reset_done"),
    # path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name='passwordResetConfirm.html'),name="password_reset_confirm"),

    path('password-reset-complete', auth_views.PasswordResetCompleteView.as_view(template_name='passwordResetComplete.html'), name='password_reset_complete'),
]

urlpatterns += staticfiles_urlpatterns()
