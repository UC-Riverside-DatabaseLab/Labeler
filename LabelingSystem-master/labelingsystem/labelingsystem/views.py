from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

class HomeView(LoginRequiredMixin, TemplateView):
	template_name = 'index.html'
	def get_template_names(self, *args, **kwargs):
		#roles_urls = {'admin': 'admin_index.html'}
		if self.request.user.is_superuser:	
			return 'super_admin_index.html'
	#		return [roles_urls.get(self.request.user.role, default)]
		elif self.request.user.is_staff:
			return 'admin_index.html' 
		else :
			return 'index.html'

	def dispatch(self, *args, **kwargs):
		return super(HomeView, self).dispatch(*args, **kwargs)

class AdminIndexView(LoginRequiredMixin, TemplateView):
	template_name = 'admin_index.html'

class SuperAdminIndexView(LoginRequiredMixin, TemplateView):
        template_name = 'super_admin_index.html'

class AboutView(LoginRequiredMixin, TemplateView) :
	template_name = 'about.html'
