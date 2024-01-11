from os import name
from django.contrib import admin
from django.urls import path,include, re_path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.urls import reverse_lazy
from django.conf.urls.static import static

app_name = 'Base'

urlpatterns = [
    # path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name='passwordResetConfirm.html'),name="password_reset_confirm"),
    path('',views.home,name="home"),
    path("register/", views.registerPage, name="register"),
    path("login/",views.loginPage,name="login"),
    path("otp/",views.otp,name="otp"),
    path("logout/",views.logoutUser,name="logout"),
    path("userprofile/",views.userProfile,name="userprofile"),
    path("changepassword/",views.changePassword,name="changePassword"),
    path("stockpicker/",views.stockpicker,name="stockpicker"),
    path("stocktracker/",views.stocktracker,name="stocktracker"),
    path("prediction/",views.stockpredictionpicker,name="stockpredictionpicker"),
    path("stockprediction/",views.stockprediction,name="stockprediction"),
    path("tips/",views.tips,name="tipsntricks"),
    path("pennystockpicker/",views.pennystockpicker,name="pennystockpicker"),
    path("pennystockprediction/",views.pennystockprediction,name="pennystockpicker"),
    
    
    # re_path(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.PasswordResetConfirmView.as_view(),
    #         name='password_reset_confirm'),
    path("stock-news/",views.stock_news,name="stock-news"),
    path("payment/",views.proUser,name="payment"),
    path("payment/success/",views.proUser,name="success"),  
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)