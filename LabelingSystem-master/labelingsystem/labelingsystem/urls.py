"""labelingsystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from .views import *

admin.site.site_header = 'Social Post Analyzer'
admin.site.site_title = 'Social Post Analyzer Labeling System'

urlpatterns = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('account:login'))),
    url(r'^admin/', admin.site.urls),
    url(r'^index/$', HomeView.as_view(), name='home'),
    url(r'^about/$', AboutView.as_view(), name='about'),
    url(r'admin_index/$', AdminIndexView.as_view(), name='admin_index'),
    url(r'super_admin_index/$', SuperAdminIndexView.as_view(), name='super_admin_index'),
    url(r'^account/', include('account.urls', namespace='account')),
    url(r'^task/', include('task.urls', namespace='task')),
    url(r'^quiz/', include('quiz.urls', namespace='quiz')),
    url(r'^response/', include('response.urls', namespace='response')),
    url(r'^classify/', include('classify.urls', namespace='classify')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
