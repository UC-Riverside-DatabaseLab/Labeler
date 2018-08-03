from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, PasswordResetForm
from cuser.forms import AuthenticationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from django.core.mail import send_mail
from django import forms
from django.conf import settings

User = get_user_model()

class SignUpForm_Alt(forms.Form):

    def __init__(self, *args, **kwargs):
        super(SignUpForm_Alt, self).__init__(*args, **kwargs)
        self.fields['Name'] = forms.CharField(max_length=255)
        self.fields['Email Address'] = forms.CharField(max_length=255)
        self.fields['Company/Institution'] = forms.CharField(max_length=255)
        self.fields['For what do you intend to use the crowdtagger?'] = forms.CharField(widget=forms.Textarea, required=False)
        self.helper = FormHelper()
        self.helper.form_id = 'signup_form'
        self.helper.form_method = 'POST'
        self.helper.form_action = '/account/signup_alt/'
        self.helper.layout = Layout(
      Field('Name', placeholder="Enter your name..."),
      Field('Email Address', placeholder="Enter your email address..."),
      Field('Company/Institution', placeholder="Enter your Company/Institution..."),
      Field('For what do you intend to use the crowdtagger?', placeholder="Explain your intention..."),)
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn btn-info btn-sm pull-right'))

    def send_email(self, name, email, belong, intention):
        subject = 'new application from ' + name
        message = 'name: ' + name + '\n' + 'email address: ' + email + '\n' + 'institution/company: ' + belong + '\n' + 'intention: ' + intention + '\n'
        send_mail(subject, message, settings.EMAIL_FROM, [settings.EMAIL_TO], fail_silently=False)

class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'login-form'

        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Field('email', placeholder="e-mail"),
            Field('password', placeholder="Password")
        )
        self.helper.add_input(Submit('submit', 'Sign in', css_class='btn btn-info btn-sm pull-right'))

class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn btn-info btn-sm pull-right'))

class AccountPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(AccountPasswordChangeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'password-change-form'

        self.helper.add_input(Submit('submit', 'Submit', css_class='btn btn-info btn-sm pull-right'))

class PasswordResetRequestForm(forms.Form):
    email_or_username = forms.CharField(label=("Email Or Username"), max_length=254)

class SetPasswordForm(forms.Form):
    #"""
    #A form that lets a user change set their password without entering the old
    #password
    #"""
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
        }
    new_password1 = forms.CharField(label=("New password"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=("New password confirmation"),
                                    widget=forms.PasswordInput)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                    )
        return password2
