from django.conf.urls import url

from django.contrib.auth.views import LoginView, LogoutView
from .views import *
from .forms import *

app_name = 'account'

urlpatterns = [
    url(r'^login$', LoginView.as_view(template_name='account/login.html', redirect_field_name='home', form_class=LoginForm, redirect_authenticated_user=True), name='login'),
    url(r'^signup/$', SignUpView.as_view(), name='signup'),
    url(r'^signup/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', SignUpView.as_view(), name='signup'),
    url(r'^logout/$', LogoutView.as_view(redirect_field_name='account:login'), name='logout'),
    url(r'^account_detail/(?P<pk>[-\w]+)/$', AccountDetailView.as_view(), name='account_detail'),
    url(r'^password_change/$', AccountPasswordChangeView.as_view(), name='password_change'),
    url(r'^password_change_success/$', AccountPasswordChangeSuccessView.as_view(), name='password_change_success'),
    url(r'^forgot_password/$', ResetPasswordRequestView.as_view(), name='forgot_password'),
    url(r'^forgot_password_success/$', ResetPasswordRequestSuccessView.as_view(), name='forgot_password_success'),
    url(r'^password_reset/$', PasswordResetConfirmView.as_view(), name='password_reset'),
    url(r'^password_reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', PasswordResetConfirmView.as_view(),name='password_reset'),
    url(r'^password_reset_success/$', AccountPasswordResetSuccessView.as_view(), name='password_reset_success'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',ActivateAccountSuccessView.as_view(), name='activate'),
    url(r'^account_activate_success/$', ActivateAccountSuccessView.as_view(), name='account_activate_success'),
]

