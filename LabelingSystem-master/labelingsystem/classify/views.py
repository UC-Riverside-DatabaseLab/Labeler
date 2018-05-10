from django.shortcuts import render
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView, FormView, DetailView
from .models import Classify
from task.models import Task
#from post.models import Post
#from response.models import PostResponse
from collections import deque
from collections import Counter
from .forms import CreateClassificationModelForm
#from .forms import EditTaskForm
from flask import Flask, request
#from .forms import UpdateLabelerForm

from nltk.metrics.agreement import AnnotationTask

from itertools import combinations

import csv
import datetime
import os
from django.conf import settings
from django.views.decorators.http import require_POST

import random
from django.db.models import Q

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.


#class TaskListView(LoginRequiredMixin, ListView):
#	model = Task
#	template_name = 'task/task_list.html'

#	def dispatch(self, request, *args, **kwargs):
#		user = self.request.user
		#post_list = []
#		self.array = []
#		self.task_complete = False
#		try:
#			task_ids = Participation.objects.filter(labeler=user.email).values('task').distinct()			
#			get_list_or_404(task_ids)			
#			self.task_list = Task.objects.filter(id__in=task_ids)
#			get_list_or_404(self.task_list)
			
#		except:			
#			  return redirect('/task/task_empty', permanent=True)
		 
#		for taskid in self.task_list:
#			try :
				#print(taskid)
#				task_object = get_object_or_404(Task, pk=taskid.pk)
				#print(task_object)
#				post_response_ids = PostResponse.objects.filter(task=taskid.pk, responder=self.request.user.pk).values_list('post__id', flat=True).distinct()
#				post_list = get_list_or_404(taskid.post_list.filter(~Q(id__in=post_response_ids)))		
				#print("here")	
#				if len(post_response_ids) >= int(Task.objects.filter(id=taskid.pk).values_list('num_labelers', flat=True).first()):
#					print ("herrrrr", len(post_response_ids),int(Task.objects.filter(id=taskid.pk).values_list('num_labelers', flat=True).first()) )
#					self.array.append(True)
#				else :
#					self.array.append(False)			
	#			self.array.append(False)
#			except:
				#print(post_list)
#				self.array.append(True)
	
#		return super(TaskListView, self).dispatch(request, *args, **kwargs)

#	def get_queryset(self):
#		return self.task_list

#	def get_context_data(self, **kwargs):
#		context = super(TaskListView, self).get_context_data(**kwargs)
#		context['task_list'] = self.get_queryset()
#		context['task_complete_list'] = self.array
#		return context

#class TakeTaskView(LoginRequiredMixin, TemplateView):
#	model = Task
#	template_name = 'task/take_task.html'
#	ctr = 1
#	def dispatch(self, request, *args, **kwargs):
#		self.task = get_object_or_404(Task, pk=self.kwargs['pk'])
#		#print(self.task)
#		post_list = []
#		temppost = ''
#		post_response_ids = PostResponse.objects.filter(task=self.task.pk, responder=self.request.user.pk).values_list('post__id', flat=True).distinct()
#		self.num_labeled = len(PostResponse.objects.filter(task=self.task.pk).values_list('responder__email', flat=True))
#		self.num_labeled = len(PostResponse.objects.filter(task=self.task.pk, responder=self.request.user.pk).values_list('responder__email', flat=True))
#		self.num_posts = list(Task.objects.filter(id=self.task.pk).values_list('num_posts').first())[0]
#		if int(self.num_labeled) /int(self.num_posts) * 100 > 100 :
#			self.scaled = 100;
#		else :
#			self.scaled = int(self.num_labeled) /int(self.num_posts) * 100;
		#print(post_response_ids)
#		least_responded_post = Task.objects.filter(id=self.task.pk).values_list('num_labelers', flat=True).first()
#		print (least_responded_post)
		#Task.objects.filter(id__in=task_ids)
#		lst_reponded_list = []
#		res_reponded_list = []
#		try:
#			temp = get_list_or_404(self.task.post_list.filter(~Q(id__in=post_response_ids)))			
			#temppost = post_list;
#			print(post_list[0])
#			l1 = list(self.task.post_list.all().filter(task=self.task.pk).values_list('id', flat=True))
#			l2 = list(post_response_ids)
#			diff_list = [item for item in l1 if not item in l2]
#			print(diff_list)
#			for responded_post in diff_list:
#				responder_ids = list(PostResponse.objects.filter(task=self.task.pk, post=responded_post).values_list('responder__id', flat=True).distinct())
				#print (len(responder_ids))
				#print('hereeee')
				#print (responded_post)
				#print (least_responded_post)
#				lnt = len(responder_ids)
#				lsts = int(least_responded_post)
#				print("number of reponders for this post", lnt)
#				if lnt<lsts:
					#least_responded_post = len(responder_ids)
					#print("hereee")
#					post_list = Post.objects.filter(id=responded_post)
					#print('hereee')
#					print("list of posts not responded by this user", post_list)					
#					lst_reponded_list.append(len(responder_ids)+1)
					#lst_reponded_list = sorted(lst_reponded_list)
#					least_responded_post = min(lst_reponded_list)#[0]
					#print(least_responded_post )
#					break				
#				else:
#					lst_reponded_list.append(len(responder_ids))	
#					res_reponded_list.append(Post.objects.filter(id=responded_post))
#					print(responded_post)		
#			if post_list == [] :
#				#= min(lst_reponded_list)
#				post_list = res_reponded_list[lst_reponded_list.index(min(lst_reponded_list))]
#				#print('all were labeled more than min')
#				#print(res_reponded_list)
#			if responded_post == None :
#				post_list = temp
#				#print ('here here')			
#			#print ("before return")
#			
			#least_responded_post = sorted(least_responded_post)
			#print(least_responded_post[0])	

			#if self.task.random_label=='T':
			#	random.shuffle(post_list)
			
			#ctr = ctr + 1			
			
			#self.task.filter(post_list).update(task=self.task.pk)
#			self.post = post_list[0]
#			print (self.post)
#		except:
			#self.complete = True
			#print(get_list_or_404(self.task.post_list.filter(~Q(id__in=post_response_ids))))
			#if post_list==[]:
			#self.complete = True	
#			return redirect('/task/task_complete', permanent=True)

#		return super(TakeTaskView, self).dispatch(request, *args, **kwargs)

#	def get_context_data(self, **kwargs):
#		context = super(TakeTaskView, self).get_context_data(**kwargs)
#		context['task'] = self.task
#		context['post'] = self.post
		#print(self.post)
		#context['complete'] = self.complete
#		context['label_list'] = self.task.label_list.all()
#		context['post_list'] = self.task.post_list.all()
#		context['num_labeled'] = self.num_labeled;
#		print (int(self.num_labeled) /int(self.num_posts) * 100)		
#		context['scaled'] = self.scaled;

#		return context

#class TaskCompleteView(LoginRequiredMixin, TemplateView):
 #   template_name = 'task/task_complete.html'
#
#class TaskEmptyView(LoginRequiredMixin, TemplateView):
 #   template_name = 'task/task_empty.html'

class CreateClassificationModelView(LoginRequiredMixin, FormView):
	model = Classify
	form_class = CreateClassificationModelForm
	
	template_name = 'classify/create_classification_model.html'
	success_url = '/classify/create_classification_model_success'
	#self.temp = Task.objects.filter(creator='1')
	
#	def upload_file(request):
#		if request.method == 'POST':
#			form = CreateTaskForm(request.POST, request.FILES)
#			print ('here')
#	        if form.is_valid():
        	  #  handle_uploaded_file(request.FILES['file'])
	           # return HttpResponseRedirect('/success/url/')
#		print (request.FILES['task_upload_file'])
#	    else:
#	        form = UploadFileForm()
#	    return render(request, 'upload.html', {'form': form})
#	from django.views.decorators.http import require_POST

#	@require_POST
#	def file_upload(self,request):
 #           save_path = os.path.join(settings.MEDIA_ROOT, 'postlist',request.files['task_upload_file'])
 #           path = default_storage.save(save_path, request.files['task_upload_file'])
 #           return default_storage.path(path)
	
	
	def form_valid(self, form):
		
#			if form.is_valid():
				classifier_name = form.cleaned_data['Classifier Name']
				classifier_description = form.cleaned_data['Classifier Description']
				task_upload_file = form.cleaned_data['Upload Task Posts and Labels']
				display_type = form.cleaned_data['Display Type']#request.POST["display_ty
				self.temp = Task.objects.filter(creator='1')

				#task_upload_file  = CreateTaskForm(
				#self.fields['Upload Task Posts and Labels']
				#doc=Document(document=self.get_form_kwargs().get('files')['Upload Task Posts and Labels'])
				#doc.save()
				#print (self.get_form_kwargs().get('files')['Upload Task Posts and Labels'])
				#task_id = doc.id
				#print(doc)
				#task_upload_file = self.get_form_kwargs().get('files')['Upload Task Posts and Labels']
				#)	
				#task_upload_file.save()
				#rint (task_upload_file)
				#task_num_labelers = form.cleaned_data['Min Number of Labelers']
		#print(task_upload_file.document)
				#task_num_posts = form.cleaned_data['Min Number of Posts']
				#task_random_label = form.cleaned_data['Label Posts in Random Order']
				#quiz_title = form.cleaned_data['Quiz Title']
				#quiz_description = form.cleaned_data['Quiz Description']
				#max_posts = form.cleaned_data['Number of Questions']
				#pass_mark = form.cleaned_data['Pass Mark']
				#quiz_upload_file = form.cleaned_data['Upload Quiz Posts and Labels']
				#participating_coders = form.cleaned_data['Participating Coders']
				#print (request.FILES['task_upload_file'])
				#self.file_upload(request)
#		temp = request.FILES['task_upload_file']
#		print (temp)
		
				#prerequisite = form.cleaned_data['Choose Quiz']#form.create_quiz(quiz_title, quiz_description, max_posts, pass_mark, quiz_upload_file, self.request.user)
				classify = form.create_classification_model(classifier_name, classifier_description, self.request.user, task_upload_file)
		#print (task)
				#form.send_email(classify)
				#task.full_clean()
		#post_list = get_list_or_404(self.task.post_list.filter(~Q(id__in=post_response_ids)))			
		#if self.task.random_label=='T':
		#	random.shuffle(post_list)
				return super(CreateClassificationModelView, self).form_valid(form)
#		print (request.FILES['task_upload_file'])
#		else:
#			form = CreateTaskForm()
#	def file_upload(request):
 #           save_path = os.path.join(settings.MEDIA_ROOT, 'postlist', request.FILES['task_upload_file'])
 #           path = default_storage.save(save_path, request.FILES['task_upload_file'])
 #           return default_storage.path(path)
	def get_conext(self, **kwargs):
#               context = super(TaskEvaluationListView, self).get_context_data(**kwargs)
#               context['task_list'] = self.get_queryset()
#               context['array'] = self.array
#               context['counter'] = self.counter
		context['temp'] = self.temp
#               context['task_size'] = self.task_size
		return context


class CreateClassificationModelSuccessView(LoginRequiredMixin, TemplateView):
	template_name = 'classify/create_classification_model_success.html'


##############Edit Task##################################

#class EditTaskView(LoginRequiredMixin, FormView):
#	model = Task
#	form_class = EditTaskForm
#	template_name = 'task/edit_task.html'
#	success_url = '/task/edit_task_success'

#	def form_valid(self, form):
#		task_title = form.cleaned_data['Task Title']
#		task_description = form.cleaned_data['Task Description']
#		task_upload_file = form.cleaned_data['Upload Task Posts and Labels']
#		task_num_labelers = form.cleaned_data['Min Number of Labelers']
#		task_num_posts = form.cleaned_data['Min Number of Posts']
#		task_random_label = form.cleaned_data['Label Posts in Random Order']
#		quiz_title = form.cleaned_data['Quiz Title']
#		quiz_description = form.cleaned_data['Quiz Description']
#		max_posts = form.cleaned_data['Number of Questions']
#		pass_mark = form.cleaned_data['Pass Mark']
#		quiz_upload_file = form.cleaned_data['Upload Quiz Posts and Labels']
#		participating_coders = form.cleaned_data['Participating Coders']
		
#		prerequisite = form.cleaned_data['Choose Quiz']#form.create_quiz(quiz_title, quiz_description, max_posts, pass_mark, quiz_upload_file, self.request.user)
#		task = form.edit_task(task_title, task_description, self.request.user, prerequisite, task_num_labelers, task_num_posts, task_random_label, task_upload_file)
#		form.send_email(task)

#		return super(EditTaskView, self).form_valid(form)

#class EditTaskSuccessView(LoginRequiredMixin, TemplateView):
#	template_name = 'task/edit_task_success.html'


################Udpate Labeler##########################
#class UpdateLabelerView(LoginRequiredMixin, FormView):
#	model = Task
#	form_class = UpdateLabelerForm
#	template_name = 'task/update_labeler.html'
#	success_url = '/task/update_labeler_success'
#	def dispatch(self, request, *args, **kwargs):
#		task = get_object_or_404(Task, pk=self.kwargs['pk'])
#	def dispatch(self, request):
	    # if this is a POST request we need to process the form data
#		if request.method == 'GET':
#			self.argA = request.GET.get('pk')
			# create a form instance and populate it with data from the request:
#			prime = UpdateLabelerForm(initial={'Select Task': request.GET.get('pk'), 'Participating Coders':request.GET.get('clist')}) 			#UpdateLabelerForm(request.GET)
#			return render(request,'task/update_labeler.html',{'form':prime})	 
#		(initial={'email':'johndoe@coffeehouse.com','name':'John Doe'})
		#return prime
		# check whether it's valid:
#		if form.is_valid():
		    # process the data in form.cleaned_data as required
		    # ...
		    # redirect to a new URL:
#		    return HttpResponseRedirect('/thanks/')

	    # if a GET (or any other method) we'll create a blank form
#	    else:
#		form = NameForm()
#		else:
#			form = UpdateLabelerForm(request.POST)	
		#def form_valid(self, form): 
#			if form.is_valid():
          		
           	#return HttpResponseRedirect('/about/contact/thankyou')
#				ttask = form.cleaned_data['Select Task']
			#print(ttask)
#				tcoders = form.cleaned_data['Participating Coders']		
			#print(tcoders)
		#participating_coders = form.cleaned_data['Participating Coders']
#				pform = form.update_labeler(ttask, tcoders)
	#form.send_email(quiz)
#				return super(UpdateLabelerView, self).form_valid(pform)

	    #return render(request, 'name.html', {'form': form})
	    	#return super(UpdateLabelerView, self).dispatch(request)

		

		#return super(UpdateLabelerView, self).form_valid(form)

#class UpdateLabelerSuccessView(LoginRequiredMixin, TemplateView):
#	template_name = 'task/update_labeler_success.html'


#class TaskEvaluationListView(LoginRequiredMixin, ListView):
#	model = Task
#	template_name = 'task/task_evaluation_list.html'

#	def dispatch(self, request, *args, **kwargs):
#		self.task_list = Task.objects.filter(creator=self.request.user.pk)
#		self.array = []
		#self.coder_emails = PostResponse.objects.filter(task=self.task.pk).values_list('responder__email', flat=True).distinct().order_by('responder__email')
		#post_list = self.task.post_list.all()
		#i=0;
#		t = []
#		pt = []
#		for task_name in self.task_list:
			#print(self.task_list.values('num_labelers')[2])
#		for post in post_list:
#			row = []
#			row.append(task_name)
		
			#for coder_email in self.coder_emails:
			#	label = 'N/A'
			#	try:
			#		post_response = Task.objects.get(task=self.task.pk, post=post.pk, responder__email=coder_email)
			#		label = post_response.label
			#	except:
			#		pass
			#print (task_name.pk)
			#print(task_name)
#			val = len(PostResponse.objects.filter(task=task_name.pk).values_list('responder__email', flat=True))
#			l = list(Task.objects.filter(title=task_name).values_list('num_posts').first())
			#print(l[0])
#			if l[0] != None:
#				row.append(int(val)/int(l[0]))
#				row.append(list(set([part.encode("utf8") for part in PostResponse.objects.filter(task=task_name.pk).values_list('responder__email', flat=True)])))
#				for l in list(set([part.encode("utf8") for part in PostResponse.objects.filter(task=task_name.pk).values_list('responder__email', flat=True)])):
#					t.append(l)
					
					#print (t)				
				
#			else:
#				row.append(val)
			#print(len(PostResponse.objects.filter(task=task_name.pk).values_list('responder__email', flat=True)))
			#print(len(Task.objects.filter(task_name.pk).values_list('num_posts')))
#			self.array.append(row)
#		self.counter = Counter(t)
#		pt.append(self.counter.keys())
#		pt.append(self.counter.values())
#		self.counter = pt
		#print(len(PostResponse.objects.filter(task=task_name.pk).values_list('responder__email', flat=True).values('task')))
		#self.labeled_so_far = len(PostResponse.objects.filter(task=task_name.pk).values_list('responder__email', flat=True).distinct('task'))
		#i = i+1
#		try:
			
			#print (self.task_list)
			#for taskI in self.task_list:
			#	print(taskI)

#			self.task_size = len(self.task_list)
#			#self.coder = PostResponse.objects.filter(task=self.task.pk).values_list('responder__email', flat=True).distinc
#			get_list_or_404(self.task_list)
			
#		except:
#			return redirect('/task/task_evaluation_empty', permanent=True)

#		return super(TaskEvaluationListView, self).dispatch(request, *args, **kwargs)

#	def get_queryset(self):
#		return self.task_list
#
#	def get_conext(self, **kwargs):
#               context = super(TaskEvaluationListView, self).get_context_data(**kwargs)
#               context['task_list'] = self.get_queryset()
#               context['array'] = self.array
#               context['counter'] = self.counter
#                context['temp'] = temp
#               context['task_size'] = self.task_size
#              return context
#_data(self, **kwargs):
#		context = super(TaskEvaluationListView, self).get_context_data(**kwargs)
#		context['task_list'] = self.get_queryset()
#		context['array'] = self.array
#		context['counter'] = self.counter
		#context['arrat'] = labeled_so_far;
#		context['task_size'] = self.task_size
#		return context

#class TaskEvaluationEmptyView(LoginRequiredMixin, TemplateView):
 #   template_name = 'task/task_evaluation_empty.html'

#class TaskEvaluationDetailView(LoginRequiredMixin, DetailView):
#	model = Task
#	template_name = 'task/task_evaluation_detail.html'

#	def dispatch(self, request, *args, **kwargs):
#		self.task = get_object_or_404(Task, pk=self.kwargs['pk'])
#		self.array = []
#		self.kappa = []
#		self.kappa1 = []
#		self.kappa_name="/media/csvfileFinal"
#		self.eval_name="/media/csvfileP"
#		self.kappa_nameLong = "/media/csvfileFinal"
#		self.lblr = []
#		self.head = []
#		self.coder_emails = PostResponse.objects.filter(task=self.task.pk).values_list('responder__email', flat=True).distinct().order_by('responder__email')
#		post_list = self.task.post_list.all()

#		name =  "media/csvfileP"# + str(self.task.pk)
#		self.eval_name = "/"+name 

#                    print (name)
                                #dateVal =datetime.datetime.now()
#		filepp = open(str(name),"w+")
#		filepp.write(';')
#		for coder_email in self.coder_emails:
#			filepp.write(coder_email)
#			filepp.write(';')
#		filepp.write('Majority Vote')
#		filepp.write('\n')
#		voteList = {}
#		listTemp = []
#		cpr = 0
#		for post in post_list:
#			row = []
#			cpr = cpr + 1
			#if cpr > 6:
			#	row.append('...')
			#	break
#			row.append(post.content)
#			filepp.write(post.content)
#			filepp.write(';')
#			i = 0
#			if len(self.coder_emails) > 5:
#				self.coder_emails_temp = self.coder_emails[0:5]
#				temp_emails = self.coder_emails
#				self.coder_emails_temp.append("(List continues...)")
				#for coder_email in temp_emails:
				#	filepp.write(coder_email)
				#	filepp.write(';')
				#filepp.write('\n')	
#				voteList = {}
#				listTemp = []
#				for coder_email in temp_emails:
#                                	if len(self.coder_emails) > 5  and coder_email == "(List continues...)":
#                                        	label = '...'
#	                                else :
#					print ('/....N?A////')
#					label = 'N/A'
#					try:
#						post_response = PostResponse.objects.filter(task=self.task.pk, post=post.pk, responder__email=coder_email).last()
#						label = post_response.label
						#print('label...',label)
						#filepp.write(coder_email)
			#		filepp.write(';')
#						filepp.write(str(label))
#						myMap = {}
#						listTemp.append(str(label))
#						maximum = ( '', 0 ) # (occurring element, occurrences)
#						for n in :
#							if n in voteList:voteList[n] += 1
#							else: voteList[n] = 1
#						        # Keep track of maximum on the go
#						        if voteList[n] > maximum[1]: maximum = (n,voteList[n])
#						filepp.write(';')
#					except:
#						filepp.write('N/A')	
#						listTemp.append('N/A')
#						filepp.write(';')
#						pass
					#if len(self.coder_emails) > 5:
		                         #        label = '...'

			#		row.append(label)
			#	filepp
#				maximum = ( '', 0 ) # (occurring element, occurrences)
#				for n in listTemp:
#					if n in voteList:
#						voteList[n] += 1
#					else: 
#						voteList[n] = 1
                                                        # Keep track of maximum on the go
#					if voteList[n] > maximum[1]:
#						 maximum = (n,voteList[n])
			#	filepp.write(';')
				#print('maximum', maximum)
			#	filepp.write(maximum[0])
			#	filepp.write('\n')
				

#			else :
#                          self.coder_emails_temp = self.coder_emails
#                           voteList = {}
#                           listTemp =[]
#			i = 0
#			for coder_email in self.coder_emails_temp:
                                #i = i+1

                               #if i>6: #self.coder_emails) > 5 and coder_email == "(List continues...)":
                               #   break
#                                if len(self.coder_emails) > 5 and coder_email == "(List continues...)":
                                  # print ('coder email-----------')
#                                   label ='...'
                                   #continue
                                   #try:
                                    # post_response = PostResponse.objects.filter(task=self.task.pk, post=post.pk, responder__email=coder_email).last()
                                     #print (post_response)
                                     #label = post_response.label
                                     #filepp.write(str(label))
                                     #filepp.write(';')
                                 #  listTemp.append(str(label))
                                   #except:
                                    # filepp.write('N/A')#listTemp.append('N/A')
                                     #filepp.write(';')
                                  # listTemp.append(str(label))
                                     #pass

#                               else :
#                                   label = 'N/A'
#                               	   try : 
#                                     post_response = PostResponse.objects.filter(task=self.task.pk, post=post.pk, responder__email=coder_email).last()
#                                     print (post_response)
#                                     label = post_response.label
#                                     if len(self.coder_emails) <= 5:
#                                        filepp.write(str(label))
#                                        filepp.write(';')
#                                     listTemp.append(str(label))
#                                   except:
#                                     if len(self.coder_emails) <= 5:
#                                        filepp.write('N/A')#listTemp.append('N/A')
#                                        filepp.write(';')
#                                     listTemp.append(str(label))
#                                     pass
#                                row.append(label)
#			maximum = ( '', 0 )
#			for n in listTemp:
#                                    if n in voteList:
#                                              voteList[n] += 1
#                                    else:
#                                              voteList[n] = 1
                                                      # Keep track of maximum on the go
#                                    if voteList[n] > maximum[1]:
#                                              maximum = (n,voteList[n])
			#filepp.write(';')
#			filepp.write(maximum[0])
#			filepp.write('\n')
#                              i = i+1
#			maximum = ( '', 0 ) # (occurring element, occurrences)
#			for n in listTemp:
#				if n in voteList:
#					voteList[n] += 1
#				else:
#					voteList[n] = 1
                                                        # Keep track of maximum on the go
#				if voteList[n] > maximum[1]:
#					maximum = (n,voteList[n])
                                #filepp.write(';')
#			print('maximum', maximum)
#                               filepp.write(maximum[0])
#                               filepp.write('\n')
#				row.append(maximum[0])
                                #row.append(label)
#			self.coder_emails_temp.append("(List continues...)")			
#			row.append(maximum[0])
#			self.array.append(row)
			#maximum = ( '', 0 ) # (occurring element, occurrences)
			#for n in listTemp:
                         #       if n in voteList:
                          #              voteList[n] += 1
                           #     else:
                        #                voteList[n] = 1
                         #                               # Keep track of maximum on the go
                          #      if voteList[n] > maximum[1]:
                           #             maximum = (n,voteList[n])
                            #    #filepp.write(';')
                        #print('maximum', maximum)
			#row.append(label)
#			maximum = ( '', 0 ) # (occurring element, occurrences)
#			for n in listTemp:
#                                if n in voteList:
#                                        voteList[n] += 1
 #                               else:
#                                        voteList[n] = 1
                                                        # Keep track of maximum on the go
#                                if voteList[n] > maximum[1]:
#                                        maximum = (n,voteList[n])
                                #filepp.write(';')
#			print('maximum', maximum)
			#filepp.write(maximum[0])
			#filepp.write('\n')

#			row.append(maximum[0])
#			self.array.append(row)

#		try:
#			annotation_triplet_list = []
#			post_response_list = PostResponse.objects.filter(task=self.task.pk)
			#rint (post_response_list)
#			post_response_t = [part.encode("utf8") for part in PostResponse.objects.filter(task=self.task.pk).values_list('responder__email', flat=True).distinct()]
#			lst_rp = []
#			triple_list = []
#			ctr = 0
#			for post_response in post_response_t:
#				post_response = str(post_response).replace('b\'', '')
#				post_response = post_response.replace('\'', '')
#				lst_rp.append(post_response)
#				print (post_response)
				#triple_list.append([])
				#triple_list[ctr].append(post_response)
				#triple_list[ctr].append(post_response)
				#triple_list[ctr].append('0')
					#ctr = ctr + 1
			#print (triple_list)
				# Get all combinations of [1, 2, 3]
				# and length 2
			#	print (post_response)
				#post_response = post_response.replace('b', '\'')
			#	print(post_response)
			#print ('here')
			#print("post_reposne", post_response_t)
#			if len(post_response_t) > 5 :
#				post_response_t_temp = post_response_t[0:5] 
#				for post_response in post_response_t_temp:
#					post_response = str(post_response).replace('b\'', '')
#					post_response = post_response.replace('\'', '')
#					lst_rp.append(post_response)
#				lst_rp.append("(List continues...)")

#				comb_temp = combinations(post_response_t, 2)
#				for i in list(comb_temp):
                                	#print ("in the comb")
#					annotation_triplet_list = []
#					ip = []
#					sp = ""
                        #       ct = ctr + 1    
                	                #print (ctr)
#					temp =  str(i[0]).replace('b\'', '')
#					temp = temp.replace('\'', '')
#					if ([temp,temp,'0'] not in triple_list) :
#						triple_list.append([])
#						triple_list[ctr].append(temp)
#						triple_list[ctr].append(temp)
#						triple_list[ctr].append('0')
#						ctr = ctr + 1
#					triple_list.append([])
#					for s in i:
#						st = str(s).replace('b\'', '')
#						st = st.replace('\'', '')
#						ip.append(st)
#						triple_list[ctr].append(st)
                                #triple_list[ctr].append(i[0])
                                #triple_list[ctr].append(i[0])
                                #triple_list[ctr].append(0)
#					print(triple_list[ctr])
#					for post_response in post_response_list:
                        #               print(post_response)    
                        #               print(ip, post_response.responder.email)        
#	                                        if (post_response.responder.email in ip):
	
#       	                                        annotation_triplet = (post_response.responder.email, post_response.post.content, post_response.label.content)
                                        #       print (post_response.responder.email)
                                        #       print(annotation_triplet)
#                	                                annotation_triplet_list.append(annotation_triplet)

#                        	                        t = AnnotationTask(annotation_triplet_list)
                                #print("kappa " +str(t.kappa()))
#					triple_list[ctr].append(str(t.kappa()))
                                #str(t.kappa()))
#					self.lblr.append(triple_list)
#					ctr = ctr + 1
#				self.alpha1 = t.alpha()
#	                        print (triple_list)
#				self.kappa1.append(triple_list)
				#print ('before EXPORT')
#				exportCSV(triple_list, self.alpha1, self.coder_emails)
#				 print ('in export CSV')
				#with open('result.csv','w') as file:
				#print(self.task)
				
#				name = "media/csvfile" #+ str(self.task.pk)
#				self.kappa_nameLong = "/"+name
#				print (name)
				
				#dateVal =datetime.datetime.now()
#				filep = open(str(name),"w+")	
					#print ('here in csv')
				#print (filep)
#				i = 0
#				ct = 1
#				filep.write(';')
#				prev_email = 's'
				#if 's' is not 's@gmail.com':
				#	print (True)
#				for email in triple_list:
#					print (email)					
#					if email[0] != prev_email :
						#print ('in email 0', email[0])
#						prev_email = email[0]
#						filep.write(email[0])	
#						filep.write(';')
#				filep.write(email[1])
#				filep.write('\n')
#				for row in triple_list:						
				#	print (row[0], row[1], row[2])
				#filep.write(row[0])
				#filep.write(row[0])
#				for i in range(0, len(self.coder_emails)):
#					filep.write(row[0])
#					filep.write(';')
				#	print (i)
#					if i == 0 or i==ct-1:
#						filep.write(row[0])
#						filep.write(';')
				#		print('row 0', row[0])
#						for k in range(0,i) :
 #                                                     filep.write('--;')
#						filep.write(row[0])
#						filep.write(';')
						
#					if i == len(self.coder_emails)-1 :						
#						i = ct
#						filep.write(row[2])
					#	filep.write(row[0])
#						print (ct)
#						print (range(0,ct))
#						for k in range(0,ct) :
#							filep.write('--;')
#						filep.write('\n')
#						ct = ct+1
#					else :
#						i = i+1						
#						filep.write('--')
#						filep.write(row[2])
#						filep.write(';')
#					#filep.write('\n')
#				filep.close()
						#or col in row:
						#file.write(col)
						#print (triple_list)
					#	for rowp in triple_list:
#							print (rowp)
						#	if forloop.counter != forloop.parentloop.counter:
						#		if col in rowp:
						#	file.write(rowp)
#					file.close()
                        #self.kappa.append(triple_list)                               

                                


#			else :
#				post_response_t_temp = post_response_t;
#				for post_response in post_response_t_temp:
#                                	post_response = str(post_response).replace('b\'', '')
#	                                post_response = post_response.replace('\'', '')
#        	                        lst_rp.append(post_response)
#                	                print (post_response)

#			self.head.append(lst_rp)
#			comb = combinations(post_response_t_temp, 2)
		#	print (comb)
			#ctr = 0
			#triple_list = []
#			ip = [] 
#			lst_rp = []
#			triple_list = []
#			ctr = 0

			#triple_list.append([])
			#triple_list.append(post_response_t)
			# Print the obtained combinations
#			for iv in list(comb):				
#				annotation_triplet_list = []				
#				triple_list.append([])
				#print (i[0])
#				temp =  str(iv[0]).replace('b\'', '')
#				temp = temp.replace('\'', '')
#				if ([temp,temp,'0'] not in triple_list) :
#					triple_list.append([])
#					triple_list[ctr].append(temp)
#					triple_list[ctr].append(temp)
#					triple_list[ctr].append('0')
#					ctr = ctr + 1
			#	print (triple_list)
#			print (triple_list)
#			comb = combinations(post_response_t, 2)
#			for i in list(comb):
#				print ("in the comb")
#				annotation_triplet_list = []
#				ip = []
#				sp = ""
			#	ct = ctr + 1	
#				print (ctr)
#				temp =  str(i[0]).replace('b\'', '')
#				temp = temp.replace('\'', '')
#				if ([temp,temp,'0'] not in triple_list) :
#                                        triple_list.append([])
#                                        triple_list[ctr].append(temp)
#                                        triple_list[ctr].append(temp)
#                                        triple_list[ctr].append('0')
#                                        ctr = ctr + 1
#				triple_list.append([])
#				for s in i:
				#	print (s)
					#print (sp)
					#p.join(s)
					#p.join(" , ")
#					print ("sds"+s)
					#print (s)
#					sp = sp+s+" , "
#					st = str(s).replace('b\'', '')
#					st = st.replace('\'', '')
#					print (st)
#					ip.append(st)
#					triple_list[ctr].append(st)
				#triple_list[ctr].append(i[0])
				#triple_list[ctr].append(i[0])
				#triple_list[ctr].append(0)

#				print(triple_list[ctr])	
				#triple_list.append(sp)
			#	print(triple_list)
				#print(post_response_list)
#				for post_response in post_response_list:
#			#		print(post_response)	
			#		print(ip, post_response.responder.email)	
#					if (post_response.responder.email in ip):
						
#						annotation_triplet = (post_response.responder.email, post_response.post.content, post_response.label.content)			
					#	print (post_response.responder.email)
					#	print(annotation_triplet)
#						annotation_triplet_list.append(annotation_triplet)
						
#						t = AnnotationTask(annotation_triplet_list)
				#print("kappa " +str(t.kappa()))
#				triple_list[ctr].append(str(t.kappa()))
				#str(t.kappa()))
#				self.lblr.append(triple_list)
				
#				ctr = ctr + 1
#			if len(post_response_t) > 5 :
#				self.alpha = self.alpha1
#			else : 
#				self.alpha = t.alpha()
#			print (triple_list)
#			self.kappa.append(triple_list)
#			name = "media/csvfileFinal" #+ str(self.task.pk)
#			self.kappa_name = "/" + name
			#print (name)
                        #dateVal =datetime.datetime.now()
#			filep = open(str(name),"w+")
                                        #print ('here in csv')
                                #print (filep)
#			i = 0
#			ct = 1
#			filep.write(';')
#			prev_email = 's'
                                #if 's' is not 's@gmail.com':
                                #       print (True)
#			for email in triple_list:
#                       print (email)                                   
#				if email[0] != prev_email:
#					prev_email = email[0]
#					filep.write(email[0])
#					filep.write(';')
#			filep.write(email[1])
#			filep.write('\n')
#			for row in triple_list:
                                #       print (row[0], row[1], row[2])
                                #filep.write(row[0])
                                #filep.write(row[0])
#                               for i in range(0, len(self.coder_emails)):
#                                       filep.write(row[0])
#                                       filep.write(';')
                                #       print (i)
 #                                       if i == 0 or i==ct-1:
#                                                filep.write(row[0])
#                                                filep.write(';')
                                #               print('row 0', row[0])
#                                                for k in range(0,i) :
#                                                      filep.write('--;')
#                                               filep.write(row[0])
#                                               filep.write(';')

#                                        if i == len(self.coder_emails)-1 :
#                                                i = ct
#                                                filep.write(row[2])
                                        #       filep.write(row[0])
#                                               print (ct)
#                                               print (range(0,ct))
#                                               for k in range(0,ct) :
#                                                       filep.write('--;')
 #                                               filep.write('\n')
#                                                ct = ct+1
 #                                       else :
#                                                i = i+1
#                                               filep.write('--')
#                                                filep.write(row[2])
#                                                filep.write(';')
                                        #filep.write('\n')
#			filep.close()	
			#self.kappa.append(triple_list)
	#	print (self.kappa)
#		except:
#			self.alpha = 'N/A'

#		return super(TaskEvaluationDetailView, self).dispatch(request, *args, **kwargs)

#	def get_context_data(self, **kwargs):
#		context = super(TaskEvaluationDetailView, self).get_context_data(**kwargs)
#		context['task'] = self.task
#		context['array'] = self.array
#		context['coder_email_list'] = self.coder_emails_temp
#		context['alpha'] = self.alpha
#		print (self.kappa)
#		context['kappa'] = self.kappa		
#		context['lblr'] = self.lblr
#		context['head'] = self.head
#		context['tablefile1'] = self.eval_name
#		if self.kappa_nameLong != self.kappa_name:
#			self.kappa_name = self.kappa_nameLong
#		context['tablefile'] = self.kappa_name
		#context[tablefileLong] = self.kappa_nameLong
#		return context
#	def exportCSV(triple_list, alpha1, coder_emails):
#		print ('in export CSV')
#		with open('csvfile.csv','wb') as file:
			#print ('in the csvfile')
#			for email in coder_emails:
#				print (email)
#				file.write('email...')
#				file.write('\n')
		#{% for row in head %}
#		for row in coder_emails:
#			for col in row:
#				file.write(col)
#			for rowp in triple_list[0]:
#				if forloop.counter != forloop.parentloop.counter:
#					if col in rowp:
#						file.write(rowp[2])
#                        <tr>
 #                               {% for col in row %}
  #                              <tr>
   #                                      {% if col != "(List continues...)" %}
    #                                          <th>{{ col }}</th>
     #                                    {% else %}
      #                                          <th><a href="" >[See full list]</a></th>
       #                                  {% endif %}

        #                                {% for rowp in kappa.0 %}                                                                               
  #                                                              <!--td></td-->
         #                                       {% if forloop.counter != forloop.parentloop.counter %}
          #                                              {% if col in rowp %}
           #                                                     <td>{{ rowp.2 }}</td>
            #                                            {% endif %}
             #                                   {% else %}
              #                                                  <td>--</td>



#                                              {%endif%}

#                                        {% endfor %}
 #                               </tr>
  #                            {% endfor %}
   #                     </tr>
    #                    {% endfor %}

		

#class TaskParticipationListView(LoginRequiredMixin, ListView):
#	model = Participation
#	template_name = 'task/task_participation_list.html'

#	def dispatch(self, request, *args, **kwargs):
#		self.task_list = Task.objects.filter(creator=self.request.user.pk)
#		self.array = []
		#self.coder_emails = PostResponse.objects.filter(task=self.task.pk).values_list('responder__email', flat=True).distinct().order_by('responder__email')
		#post_list = self.task.post_list.all()
		#i=0;
#		for task_name in self.task_list:
			#print(self.task_list.values('num_labelers')[2])
#		for post in post_list:
#			row = []
#			x = Participation.objects.filter(task=task_name.pk).values('id').distinct('task');
#			responded_posts = len(PostResponse.objects.filter(task=task_name.pk))
#			posts_no = len(Task.objects.filter(id=task_name.pk).values_list('post_list', flat=True))
#			print(responded_posts)
#			print(posts_no)
#			row.append(task_name)
			
			#for coder_email in self.coder_emails:
			#	label = 'N/A'
			#	try:
			#		post_response = Task.objects.get(task=self.task.pk, post=post.pk, responder__email=coder_email)
			#		label = post_response.label
			#	except:
			#		pass
			#print (task_name.pk)
			#print(task_name)			self.labeler_list = [part.encode("utf8") for part in Participation.objects.filter(task=task_name.pk).values_list('labeler', flat=True)]
			#for l in list(self.labeler_list):
			#	row.append(list(self.labeler_list).get(l))
			
#			row.append(list(self.labeler_list))#list(Participation.objects.filter(task=task_name.pk).values_list('coder', flat=True)))#.distinct('coder')))
			#print(Participation.objects.filter(task=task_name.pk).values())
			#print(len(Task.objects.filter(task_name.pk).values_list('num_posts')))
#			self.array.append(row)
		#print(row)
		#print(len(PostResponse.objects.filter(task=task_name.pk).values_list('responder__email', flat=True).values('task')))
		#self.labeled_so_far = len(PostResponse.objects.filter(task=task_name.pk).values_list('responder__email', flat=True).distinct('task'))
		#i = i+1
#		try:
#			
			#print (self.task_list)
			#for taskI in self.task_list:
			#	print(taskI)

			#self.task_size = len(self.task_list)
			#self.coder = PostResponse.objects.filter(task=self.task.pk).values_list('responder__email', flat=True).distinc
#			get_list_or_404(self.task_list)
#			
#		except:
#			return redirect('/task/task_participation_empty', permanent=True)
#
#		return super(TaskParticipationListView, self).dispatch(request, *args, **kwargs)

#	def get_queryset(self):
#		return self.task_list

#	def get_context_data(self, **kwargs):
#		context = super(TaskParticipationListView, self).get_context_data(**kwargs)
		#context['task_list'] = self.get_queryset()
		
#		context['array'] = self.array
#		print (context['array'])
		#context['arrat'] = labeled_so_far;
#		context['task_size'] = self.task_size
#		return context

#class TaskParticipationEmptyView(LoginRequiredMixin, TemplateView):
 #   template_name = 'task/task_participation_empty.html'
