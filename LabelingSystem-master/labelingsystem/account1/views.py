from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView

from .forms import SignUpForm, AccountPasswordChangeForm, PasswordResetRequestForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
#from settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.views.generic import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from task.models import Participation
from response.models import PostResponse

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
class SignUpView(CreateView):
	form_class = SignUpForm
	template_name = 'account/signup.html'
#     template_name = "account/forgot_password.html"    #code for template is given below the view's code
   # success_url = reverse_lazy('account:forgot_password_success')
    #form_class = PasswordResetRequestForm
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
 #           if self.validate_email_address(data) is True:                 #uses the method written above
         #       '''
          #      If the input is an valid email address, then the following code will lookup for users associated with that email address. If found then an email will be sent to the address, else an error message will be printed on the screen.
           #     '''
              #  associated_users= User.objects.filter(Q(email=data))
#if self.validate_email_address(data) is True:                 #uses the method written above
         #       '''
          #      If the input is an valid email address, then the following code will lookup for users associated with that email address. If found then an email will be sent to the address, else an error message will be printed on the screen.
           #     '''
              #  associated_users= User.objects.filter(Q(email=data))
               # if associated_users.exists():
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
                            subject_template_name="Request to reset your password"#'registration/password_reset_subject.txt' 
                            # copied from django/contrib/admin/templates/registration/password_reset_subject.txt to templates directory
                            email_template_name='account/password_reset_email.html'
                            # copied from django/contrib/admin/templates/registration/password_reset_email.html to templates directory
                            #subject = loader.render_to_string(subject_template_name, c)
                            # Email subject *must not* contain newlines
                            #subject = ''.join(subject.splitlines())
                            email = loader.render_to_string(email_template_name, c)
                            send_mail(subject_template_name, email, 'ucipt.labeling@gmail.com' , [user.email], fail_silently=False)
#                    result = self.form_valid(form)
 #                   messages.success(request, 'An email has been sent to ' + data +". Please check your inbox to continue reseting password.")
                #print (messages)
                   # return result
                result = self.form_invalid(form)
                messages.error(request, 'No user is associated with this email address')
                #return result
            messages.error(request, 'Invalid Input')
           # return self.form_invalid(form)


#   send_mail(subject_template_name, email, 'ucipt.labeling@gmail.com' , [user.email], fail_silently=False)
	success_url = reverse_lazy('account:login')

class AccountDetailView(LoginRequiredMixin, DetailView):
	model = User
	template_name = 'account/account_detail.html'
	fields = ('email', )

	def dispatch(self, request, *args, **kwargs):
		user = self.request.user
		self.task_list = Participation.objects.filter(coder=user).values_list('task', flat=True)
		self.task_size = len(self.task_list)
#		print (self.task_size)
		self.post_response_list = PostResponse.objects.filter(responder=user)
		return super(AccountDetailView, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(AccountDetailView, self).get_context_data(**kwargs)
		context['task_list'] = self.task_list
		context['task_size'] = self.task_size
#		print (self.task_size)
		context['post_response_list'] = self.post_response_list
		return context

class AccountPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
	form_class = AccountPasswordChangeForm
	template_name = 'account/password_change.html'
	success_url = reverse_lazy('account:password_change_success')


class ResetPasswordRequestView(FormView):
        template_name = "account/forgot_password.html"    #code for template is given below the view's code
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
            if self.validate_email_address(data) is True:                 #uses the method written above
         #       '''
          #      If the input is an valid email address, then the following code will lookup for users associated with that email address. If found then an email will be sent to the address, else an error message will be printed on the screen.
           #     '''
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
                            subject_template_name="Request to reset your password"#'registration/password_reset_subject.txt' 
                            # copied from django/contrib/admin/templates/registration/password_reset_subject.txt to templates directory
                            email_template_name='account/password_reset_email.html'    
                            # copied from django/contrib/admin/templates/registration/password_reset_email.html to templates directory
                            #subject = loader.render_to_string(subject_template_name, c)
                            # Email subject *must not* contain newlines
                            #subject = ''.join(subject.splitlines())
                            email = loader.render_to_string(email_template_name, c)
                            send_mail(subject_template_name, email, 'ucipt.labeling@gmail.com' , [user.email], fail_silently=False)
                    result = self.form_valid(form)		    
                    messages.success(request, 'An email has been sent to ' + data +". Please check your inbox to continue reseting password.")
		#print (messages)
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
	success_url = reverse_lazy('account:password_reset_success') #'/account/login'
	form_class = SetPasswordForm
	
	def post(self, request, uidb64=None, token=None, *arg, **kwargs):
     	# """
     	#  View that checks the hash in a password reset link and presents a
     	#  form for entering a new password.
     	#  """
		UserModel = get_user_model()

		form = self.form_class(request.POST)
		assert uidb64 is not None and token is not None#checked by URLconf
		try:
			uid = urlsafe_base64_decode(uidb64)
			user = UserModel._default_manager.get(pk=uid)
		except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
			user = None
	#	print(self.request.user)

		if user is not None and default_token_generator.check_token(user, token):
			if form.is_valid():
		        	new_password= form.cleaned_data['new_password2']
			        user.set_password(new_password)
			        user.save()
				#print (new_password)
		        	messages.success(request, 'Password has been reset.')
			        return self.form_valid(form)
			else:
			        messages.error(request, 'Password reset has not been successful.')
		        	return self.form_invalid(form)
		else:
			messages.error(request,'The reset password link is no longer valid.')
		return self.form_invalid(form)
