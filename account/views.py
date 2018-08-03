from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView

from .forms import SignUpForm, AccountPasswordChangeForm, PasswordResetRequestForm, SetPasswordForm, LoginForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.views.generic import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from task.models import Participation
from response.models import PostResponse
from django.shortcuts import redirect

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


from django.contrib.auth import get_user_model, login
User = get_user_model()
from django.contrib.auth.decorators import login_required, permission_required

from .forms import SignUpForm_Alt
class SignUpAltView(FormView):
  form_class = SignUpForm_Alt
  template_name = 'account/signup_alt.html'
  success_url = reverse_lazy('account:signup_success')
  def form_valid(self, form):
    name = form.cleaned_data['Name']
    email = form.cleaned_data['Email Address']
    belong = form.cleaned_data['Company/Institution']
    intention = form.cleaned_data['For what do you intend to use the crowdtagger?']
    form.send_email(name, email, belong, intention)
    return super(SignUpAltView, self).form_valid(form)

class SignUpSuccessView(TemplateView):
  template_name = 'account/signup_success.html'

class LoginRequiredMixin(object):
  
  @classmethod
  def as_view(cls, **initkwargs):
    view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
    return login_required(view, login_url='/account/login')

class SignUpView(CreateView):
  form_class = SignUpForm
  template_name = 'account/signup.html'
  success_url = reverse_lazy('account:account_activate_success.html')

  @staticmethod
  def validate_email_address(email):
        #'''
        #This method here validates the if the input is an email address or not. Its return type is boolean, True if the input is a email address or False if its not.
        #'''
    try:
      validate_email(email)
      return True
    except ValidationError:
      return False

  def post(self, request, *args, **kwargs):
        #'''
        #A normal post request which takes input from field "email_or_username" (in ResetPasswordRequestForm). 
        #'''
    form = self.form_class(request.POST)
    if form.is_valid():
      user = form.save(commit=False)
      user.is_active = False
      user.save()
      current_site = get_current_site(request)
      subject = 'Activate Your MySite Account'
      c = {
          'email': user.email,
          'domain': request.META['HTTP_HOST'],
          'site_name': 'your site',
          'uid': urlsafe_base64_encode(force_bytes(user.pk)),
          'user': user,
          'token': default_token_generator.make_token(user),
          'protocol': 'http',
          }
      subject_template_name="Request to Activate Your Account"
      email_template_name='account/acc_active_email.html'    
      email = loader.render_to_string(email_template_name, c)
      send_mail(subject_template_name, email, 'ucipt.labeling@gmail.com' , [user.email], fail_silently=False) 
      messages.success(request, "An email has been sent to you. Please check your inbox.")
      return redirect('/account/login')
    return render(request, 'account/signup.html', {'form': form})

class ActivateAccountSuccessView(TemplateView):
  template_name = 'account/account_activate_success.html'
  success_url = reverse_lazy('account:login') #'/account/login'
  form_class = LoginForm

  def post(self, request, uidb64=None, token=None, *arg, **kwargs):
        # """
        #  View that checks the hash in a password reset link and presents a
        #  form for entering a new password.
        #  """
    UserModel = get_user_model()
    form = self.form_class(request.POST)
    assert uidb64 is not None and token is not None  # checked by URLconf
    try:
      uid = urlsafe_base64_decode(uidb64)
      user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
      user = None
    if user is not None and default_token_generator.check_token(user, token):
      user.is_active = True
      user.save()
      return redirect('/account/login')
    else:
      return render(request, 'account_activation_invalid.html')



class AccountDetailView(LoginRequiredMixin, DetailView):
  model = User
  template_name = 'account/account_detail.html'
  fields = ('email', )

  def dispatch(self, request, *args, **kwargs):
    user = self.request.user
    self.task_list = Participation.objects.filter(labeler=user).values_list('task', flat=True)
    self.task_size = len(self.task_list)
    self.post_response_list = PostResponse.objects.filter(responder=user)
    return super(AccountDetailView, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(AccountDetailView, self).get_context_data(**kwargs)
    context['task_list'] = self.task_list
    context['task_size'] = self.task_size
    context['post_response_list'] = self.post_response_list
    return context

class AccountPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
  form_class = AccountPasswordChangeForm
  template_name = 'account/password_change.html'
  success_url = reverse_lazy('account:password_change_success')


class ResetPasswordRequestView(FormView):
  template_name = "account/forgot_password.html"
  success_url = reverse_lazy('account:forgot_password_success')
  form_class = PasswordResetRequestForm

  @staticmethod
  def validate_email_address(email):
  #'''
  #This method here validates the if the input is an email address or not. Its return type is boolean, True if the input is a email address or False if its not.
  #'''
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

  def post(self, request, *args, **kwargs):
  #'''
  #A normal post request which takes input from field "email_or_username" (in ResetPasswordRequestForm). 
  #'''
    form = self.form_class(request.POST)
    if form.is_valid():
        data= form.cleaned_data["email_or_username"]
    if self.validate_email_address(data) is True:                 
  #      '''
  #      If the input is an valid email address, then the following code will lookup for users associated with that email address. If found then an email will be sent to the address, else an error message will be printed on the screen.
  #      '''
        associated_users= User.objects.filter(Q(email=data))
        if associated_users.exists():
          for user in associated_users:
            c = {
                'email': user.email,
                'domain': request.META['HTTP_HOST'],
                'site_name': 'your site',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
                }
            subject_template_name = "Request to reset your password"
            email_template_name = 'account/password_reset_email.html'
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject_template_name, email, 'ucipt.labeling@gmail.com', [user.email], fail_silently=False)
            result = self.form_valid(form)
            return result
        result = self.form_invalid(form)
        messages.error(request, 'No user is associated with this email address')
        return result
    messages.error(request, 'Invalid Input')
    return self.form_invalid(form)

class ResetPasswordRequestSuccessView(TemplateView):
  template_name = 'account/forgot_password_success.html'

class AccountPasswordChangeSuccessView(LoginRequiredMixin, TemplateView):
  template_name = 'account/password_change_success.html'

class AccountPasswordResetSuccessView(TemplateView):
  template_name = 'account/password_reset_success.html'

class PasswordResetConfirmView(FormView):
  template_name = 'account/password_reset.html'
  success_url = reverse_lazy('account:login')
  form_class = SetPasswordForm

  def post(self, request, uidb64=None, token=None, *arg, **kwargs):
      # """
      #  View that checks the hash in a password reset link and presents a
      #  form for entering a new password.
      #  """
    UserModel = get_user_model()
    form = self.form_class(request.POST)
    assert uidb64 is not None and token is not None  # checked by URLconf
    try:
      uid = urlsafe_base64_decode(uidb64)
      user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
      user = None
    if user is not None and default_token_generator.check_token(user, token):
      if form.is_valid():
        new_password = form.cleaned_data['new_password2']
        user.set_password(new_password)
        user.save()
        messages.success(request, 'Password has been reset.')
        return self.form_valid(form)
      else:
        messages.error(request, 'Password reset has not been successful.')
        return self.form_invalid(form)
    else:
      messages.error(request, 'The reset password link is no longer valid.')
    return self.form_invalid(form)
