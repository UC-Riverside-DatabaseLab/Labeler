from django import forms
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.urlresolvers import resolve

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Fieldset, ButtonHolder, HTML, Button
from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from django.forms.fields import ChoiceField

import random
import string
import hashlib

from .models import Classify
from quiz.models import Quiz
from response.models import PostResponse
from task.models import Task
#from label.models import Label
#from post.models import Post

from collections import deque
import os
import csv
from io import TextIOWrapper

CHOICES = (('T', 'True',), ('F', 'False',))
QCHOICES = (('create', 'Create New Quiz',), ('choose', 'Choose From Available Quizes',))
DISPLAY_CHOICES = (
    ("locationbox", "Display Location"),
    ("displaybox", "Display Direction")
)
options = [
    ('Textbox1', 'Textbox1'),
    ('Textbox2', 'Textbox2'),
    
    ]
#class PostModelForm(forms.ModelForm):
#    class Meta:
 #       model = Post

  #  def __init__(self, *args, **kwargs):
   #     forms.ModelForm.__init__(self, *args, **kwargs)
	#if 'initial' in kwargs:
        #	self.fields['post_list'].queryset = Post.objects.filter(Post.id=initial.id)#Post.avail.all()



#############################Create Task#######################################
class CreateClassificationModelForm(forms.Form):
	dynamic_data = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=options)

	def __init__(self, *args, **kwargs):
		super(CreateClassificationModelForm, self).__init__(*args, **kwargs)
		self.fields['Classifier Name'] = forms.CharField(max_length=50)
		self.fields['Classifier Description'] = forms.CharField(widget=forms.Textarea, required=False)
		#self.fields['Min Number of Posts'] = forms.IntegerField(required=False)
		#self.fields['Min Number of Labelers'] = forms.IntegerField(required=False)
		self.fields['Upload Task Posts and Labels'] = forms.FileField()
		#self.fields['Display Type'] = forms.ChoiceField(widget=forms.RadioSelect, choices=DISPLAY_CHOICES)
		task_name_list = Task.objects.all()
		temp = []
		for task_name in task_name_list :
                        post_ll= Task.objects.filter(id=task_name.pk).values_list('post_list', flat=True)
                        count = 0
                        for postid in post_ll :
                                if len(PostResponse.objects.filter(task=task_name, post=postid).values_list('responder__email', flat=True).distinct()) >= int(Task.objects.filter(id=task_name.pk).values_list('num_labelers', flat=True).first()):
                                        count = count + 1
#               print ()
                        if count == len(post_ll):
                                temp.append(task_name.pk)
                #print ('this is temp', temp)
                #tmp = temp
		self.fields['Choose Labeling Task'] =forms.ModelChoiceField(queryset=Task.objects.filter(id__in=temp), required=False)

#		self.fields['Choose Quiz'] =forms.ModelChoiceField(queryset=Quiz.objects.all(), required=False)##forms.CharField(max_length=5, widget=forms.Select(choices=QCHOICES))
		#Quiz.objects.filter(creator=self.request.user.pk)
		#Quiz.objects.filter(creator=self.request.user.pk)
		#Quiz.objects.all()
#		self.fields['Quiz Title'] = forms.CharField(max_length=50, required=False)
#		self.fields['Quiz Description'] = forms.CharField(widget=forms.Textarea, required=False)
#		self.fields['Number of Questions'] = forms.IntegerField(required=False)
#		self.fields['Pass Mark'] = forms.IntegerField(max_value=100, required=False)
		
#		self.fields['Label Posts in Random Order'] =  forms.CharField(max_length=5, widget=forms.Select(choices=CHOICES))
#widget=forms.RadioSelect(attrs={'class': 'Radio'}), choices=('True','False')
#		self.fields['Upload Quiz Posts and Labels'] = forms.FileField(required=False)

		#self.fields['Participating Coders'] = forms.CharField(widget=forms.Textarea, required=False)

		self.helper = FormHelper()
		self.helper.form_id = 'create_classification_model_form'
		self.helper.form_method = 'POST'
		self.helper.form_action = '/classify/create_classification_model/'
		temp =[]# Task.objects.filter(creator='1')
		tmp = []
		task_name_list = Task.objects.all()
		#print ('All tasks', task_name_list)
		#post_response_ids = PostResponse.objects.filter(task=taskid.pk, responder=self.request.user.pk).values_list('post__id', flat=True).distinct()
		#posts_no = len(T
		for task_name in task_name_list : 
			post_ll= Task.objects.filter(id=task_name.pk).values_list('post_list', flat=True)
			count = 0
			for postid in post_ll :
				if len(PostResponse.objects.filter(task=task_name, post=postid).values_list('responder__email', flat=True).distinct()) >= int(Task.objects.filter(id=task_name.pk).values_list('num_labelers', flat=True).first()):
					count = count + 1
#		print ()
			if count == len(post_ll):
				temp.append(task_name)
		#print ('this is temp', temp)
		tmp = temp
		#tmp1 = temp.pop()
		#print(temp)
		#tmp1 = temp.pop()
		#print(temp)
#		from collections import deque
		#items = deque(temp)
		p = 0
		self.helper.layout = Layout(
			HTML("""<div class="panel panel-info">
					<div class="panel-heading">
						Step 1: Create Classification Model
					</div>
					<div class="panel-body">
					"""),
			Field('Classifier Name', placeholder="Enter the classification task name..."),
			Field('Classifier Description', placeholder="Write some description about the classifier..."),
#			Field('Min Number of Posts', placeholder="Minimum number of posts to be labeled by labelers for this task"),
#			Field('Min Number of Labelers', placeholder="Minimum number of labelers per post"),			
			HTML(""""""),
#			Field('Label Posts in Random Order', placeholder=""),
#			Field('Upload Task Posts and Labels', placeholder = ""),
#			Field('Source of Training Data', placeholder=""),
			Field('Choose Quiz', placeholder=""),	
			HTML(""" 
			<!--script>$(function() {
			    $('input[name=post-format]').on('click init-post-format', function() {
		        	$('#gallery-box').toggle($('#post-format-gallery').prop('checked'));
			    }).trigger('init-post-format');
				 $('input[name=post-format]').on('click init-post-format', function() {
				$('#gallery-box1').toggle($('#post-format-gallery1').prop('checked'));
			    }).trigger('init-post-format');

			});
			</script-->

			<!--label><input type="radio" name="post-format" id="post-format-gallery">CSV File</label><br/>
			<label><input type="radio" name="post-format" id="post-format-gallery1">Labeling Task</label-->

			<!--div id="gallery-box"> <!--style="border: 1px solid red;"--><!--select class="some_class">
		            <option value="1">Sum</option>
        	    		<option value="2">Difference</option>
	        	    <option value="3">Whatever</option>
		        </select-->"""),
			
#			Field('Upload Task Posts and Labels', placeholder = ""),
			HTML("""
                        </div>"""),
			HTML("""
			<!--div id="gallery-box1"> <!--style="border: 1px solid red;"--><!--select class="some_class" id="test"-->
			<!--script-->"""),
#			Field('Choose Labeling Task', placeholder=""),
			HTML("""			                     
			</div>"""),


			HTML("""<style> p.solid {border : 1px; display: inline-block ; border-style: solid;} </style>
			<!--table style="border: 1px solid black;"--> 

			<tr>
			<td>
			<!--p class="solid">
				<b>Note</b> : Upload a csv file with <a href="/media/sample_survey1.csv" download="sample_survey1.csv">this sample format</a> <br/>[All labels separated with pipelines on the first line. <br/>Each post on a separate line after that.]
				</td>
			</tr>
			</p-->
				<!--/table-->
			"""),
			#HTML("""</div>
			#		</div>"""),
#			Field('Choose Quiz', placeholder=""),
			#Field('Quiz Title', placeholder="Enter the quiz title..."),
			#Field('Quiz Description', placeholder="Write some description about the quiz..."),
			#Field('Number of Questions'),
			#Field('Pass Mark'),
			#Field('Upload Quiz Posts and Labels'),
			#HTML("""</div>
			#		</div>"""),
			
			#Field('Participating Coders', placeholder=" coder1@example.com \n coder2@example.com \n ..."),
			HTML("""</div-->
					</div-->"""),
			 
			  HTML("""<div class="panel panel-info">
                                        <div class="panel-heading">
                                                Step 2: Source of Training Data
                                        </div>
                                        <div class="panel-body"> """),
			HTML("""
					 
                        <script>$(function() {
                            $('input[name=post-format]').on('click init-post-format', function() {
                                $('#gallery-box').toggle($('#post-format-gallery').prop('checked'));
                            }).trigger('init-post-format');
                                 $('input[name=post-format]').on('click init-post-format', function() {
                                $('#gallery-box1').toggle($('#post-format-gallery1').prop('checked'));
                            }).trigger('init-post-format');

                        });
                        </script>

                        <label><input type="radio" name="post-format" id="post-format-gallery">CSV File</label><div></div>
                        <!--label><input type="radio" name="post-format" id="post-format-gallery1">Labeling Task</label-->

                        <div id="gallery-box"> <!--style="border: 1px solid red;"--><!--select class="some_class">
                            <option value="1">Sum</option>
                                <option value="2">Difference</option>
                            <option value="3">Whatever</option>
                        </select-->                        <!--label><input type="radio" name="post-format" id="post-format-gallery1">Labeling Task</label-->
"""),

                       Field('Upload Task Posts and Labels', placeholder = ""),
                        HTML("""
                        </div><div>"""),
                        HTML("""<label><input type="radio" name="post-format" id="post-format-gallery1">Labeling Task</label>
                        </div><div id="gallery-box1"> <!--style="border: 1px solid red;"--><!--select class="some_class" id="test"-->
                        <!--script-->"""),
                        Field('Choose Labeling Task', placeholder=""),
                        HTML(""" <!--label><input type="radio" name="post-format" id="post-format-gallery1">CSV File</label--><div></div>                                            
                        </div>"""),
			HTML("""
					</div></div>
                                        """),


		)
		  

		self.helper.add_input(Submit('create_classification_model_submit', 'Submit', css_class='btn btn-info btn-sm pull-right'))


	def create_classification_model(self, classifier_name, classifier_description, user, task_upload_file):
			
		try:
		#	task_obj = Task.objects.create(
		#		#id = default,
                #                title = task_title,
                #                description = task_description,
                #                num_posts = task_num_posts,
                #                num_labelers = task_num_labelers,
                #                random_label = task_random_label,
                #                creator = user,
                #                prerequisite = prerequisite,
		#		upload_file = task_upload_file
                #               )
		#	task_obj.save()
		#	self.id = task_obj.id
			#print (task_upload_file)
			#mypath = os.path.dirname(os.path.abspath(__file__))
			#print (mypath)
#			csvfile = open(str(task_upload_file), 'r')
#			csvfile = open(str(task_upload_file), 'rb')
			#print("this issss", csvfile)
	#		print (os.path.abspath(csvfile))
			#csvfile = open(str(task_upload_file), 'rb')# as csvfile:
			#print (csvfile)
			#print(task_upload_file)
			
#			readerR = csv.reader(TextIOWrapper(task_upload_file), delimiter='|', skipinitialspace=True)
#			print(TextIOWrapper(task_upload_file))
#			print (readerR)
			#svfile = open(task_upload_file, 'rb')# as csvfile:
			#rint (csvfile)
		#	print (task_upload_file)
			readerR = csv.reader(TextIOWrapper(task_upload_file), delimiter='|', skipinitialspace=True)
#                       readerF = csv.reader(TextIOWrapper(task_upload_file), delimiter='|', skipinitialspace=True)
			#reader = csv.reader(open(task_upload_file, newline=''), delimiter='|')
			print ("here")
			#print(readerR)
		#	posts = readerR
		#	print (posts)
		#	for post in posts:
		#		print (post)
			labelsF = next(readerR)
			print (labelsF)
			#random.shuffle(labelsF)
			#print(labelsF)
#			for rowF in labelsF:
		        #print (labelsF)
			#print (task_random_label)			
			print ('here again')	
#			task_obj = Task.objects.create(
#				title = task_title,
#				description = task_description,
#				num_posts = task_num_posts,
#				num_labelers = task_num_labelers,
#				random_label = task_random_label,
#				creator = user,
#				prerequisite = prerequisite
#				)
			print(classifier_name, classifier_description, user)
			classify_obj = Classify.objects.create(
                                #id = default,
                                name = classifier_name,
                                description = classifier_description,
#                                num_posts = task_num_posts,
 ##                               num_labelers = task_num_labelers,
                                #random_label = task_random_label,
                                creator = user,
 #                               prerequisite = prerequisite,
                              	#upload_task= task_upload_file
                                )
			#task_obj.full_clean()
			print (user)
			classify_obj.save()
			self.id = classify_obj.id
	
						
#			posts = readerR
			#print ('here again')
		#	print(posts)
#			print (posts)
#			list2_shuf_temp = []
#			ctr = 0
#			for post in posts:		    
#				print(post)
#				if post != [] :
#					list2_shuf_temp.append(post[0])
#					ctr = ctr + 1
#			#	print(post)
#			print(task_random_label)
#			if task_random_label == 'T':								   	
#				print ('here in T')
#				list1_shuf = []
#				list2_shuf = []
#				index_shuf = range(ctr) #len(posts))
#				index_shuf1 = [i for i in range(ctr)]#len(posts))]
#				print(index_shuf)
#				random.shuffle(index_shuf1)
#				print('random')
#				for i in index_shuf1:	
#				    #print(labelsF)
				    #temp = labelsF[i]		
				    #list1_shuf.append(temp)	
				   # print (list2_shuf_temp)
#				    temp = list2_shuf_temp[i]
#				    list2_shuf.append(temp)
#				    print(list2_shuf)
#				list1_shuf = labelsF
#			else : 
#					list2_shuf = list2_shuf_temp
#					list1_shuf = labelsF

#			for label in  list1_shuf:
				#print (label)
#				label_object = Label.objects.create(content=label)				
#				task_obj.label_list.add(label_object)
#				print (label)
			#random.shuffle(posts)
			#print (posts)
#			for post in list2_shuf:
#				post_object = Post.objects.create(
#				content = post,
#				author = user)
				
#				print (post)
#				task_obj.post_list.add(post_object)
			
		except:
			return None

		return classify_obj

#	def create_quiz(self, quiz_title, quiz_description, max_posts, pass_mark, quiz_upload_file, user):
#		try:
			

			#reader = csv.reader(TextIOWrapper(quiz_upload_file), delimiter='|', skipinitialspace=True)
#			csvfile = open(str(quiz_upload_file), 'rb')# as csvfile:
#			print (csvfile)
#			readerR = csv.reader(csvfile, delimiter='|', skipinitialspace=True)
#			quiz_object = Quiz.objects.create(
#				title = quiz_title,
#				description = quiz_description,
#				max_posts = max_posts,
#				pass_mark = pass_mark,
#				creator = user)

#			answer_key_object = AnswerKey.objects.create(quiz=quiz_object)

#			label_list = []
#			labelsF = next(readerR)
			
			#print(quiz_title)
#			for label in labelsF:
				#print (label)
#				label_object = Label.objects.create(content=label)
#				label_list.append(label_object)
#				quiz_object.label_list.add(label_object)

#			postsF = readerR
#			for post in postsF:
				#print (post)
#				post_object = Post.objects.create(
#					content = post[0],
#					author = user)
#				quiz_object.post_list.add(post_object)
#				answer_object = Answer.objects.create(
#					answer_key = answer_key_object,
#					post = post_object,
#					label = [item for item in label_list if item.content == post[1]][0])
#		except:
#			return None

#		return quiz_object

	

#	def add_participant(self, task, coder):
#		Participation.objects.create(
#			task=task,
#			labeler=coder)

#	def send_email(self, task):
#		participating_coders = self.cleaned_data['Participating Coders']
#		coder_list = participating_coders.split()
#		print (coder_list)
#		coder_l = []
		#for coder in coder_list:
		#	print (coder)
		#	subject = str.format("Task created for {0}", coder)
		#	message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here: http://0.0.0.0/account/signup/\n\nBest,\nUCIPT Team", coder)
		#	print (task, coder)
		#	self.add_participant(task, coder)
		#	coder_l.append(coder)
		#	send_mail(subject, message, 'sara.alaee@gmail.com', coder_l, fail_silently=False)
		#	coder_l = []
#		for coderP in coder_list:
#			print (coderP)
			#subject = str.format("Task created for {0}", coderP)
			#message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here: [WEBSITE_URL]\n\nBest,\nUCIPT Team", coderP)
#			print (coderP)
#			self.add_participant(task, coderP)
#			coder_l.append(coderP)
#			#send_mail(subject, message, 'sara.alaee@gmail.com', coder_l, fail_silently=False)
#			coder_l = []

			#UserModel = get_user_model()
#			passwrd = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
#			passw = hashlib.sha224(passwrd.encode('utf-8')).hexdigest()
#			print(passwrd)
#			print(passw)
#			User = get_user_model()
#			if not User.objects.filter(email=coderP) :
#				print ('there')	
#				User.objects.create(email=coderP)
#				user = User._default_manager.get(email=coderP)
                                #print (user)
#				user.set_password(passwrd)
#				user.save()
#				subject = str.format("Task created for {0}", coderP)
#				message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here: http://dblab-rack30.cs.ucr.edu/account/login\n Your password :{1} \nBest,\nUCIPT Team", coderP, passwrd)
#				print (coderP)
#				print (subject)
                        #self.add_participant(task, coder)
#				coder_l.append(coderP)
	                        #print (coder_l)
        	                #print ('right here')
#				send_mail(subject, message, 'sara.alaee@gmail.com', coder_l, fail_silently=False)
#			else : 
#				print ('there else')	
#				user = User._default_manager.get(email=coderP)
#				print (user)
#				subject = str.format("Task created for {0}", coderP)
#				message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here: http://dblab-rack30.cs.ucr.edu/account/login\n\nBest,\nUCIPT Team", coderP)
        	             	#print (coderP)
                	        #print (subject)
                        #self.add_participant(task, coder)
#				coder_l.append(coderP)
#				print (coder_l)
#				print ('right here')
#				send_mail(subject, message, 'sara.alaee@gmail.com', coder_l, fail_silently=False)
				#user.set_password(passwrd)
				#user.save()
				#form = self.form_class(request.POST)
				#assert uidb64 is not None and token is not None  # checked by URLconf
			        #try:
			         #   uid = urlsafe_base64_decode(uidb64)	    
			          #  user = UserModel._default_manager.get(pk=uid)
    
			        #except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
    				#	user = None

				#user.set_password(passwrd)
		        #user.save()
#			subject = str.format("Task created for {0}", coderP)
#			message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here: http://dblab-rack30.cs.ucr.edu/account/login\n Your password :{1} \nBest,\nUCIPT Team", coderP, passwrd)
#			print (coderP)
#			print (subject)
			#self.add_participant(task, coder)
#			coder_l.append(coderP)
#			print (coder_l)
#			print ('right here')
#			send_mail(subject, message, 'sara.alaee@gmail.com', coder_l, fail_silently=False)	


################Edit Task##############################Field('Task Title', placeholder=""),
			
			#Field('Quiz Title', placeholder="Enter the quiz title..."),
			#Field('Quiz Description', placeholder="Write some description about the quiz..."),
			#Field('Number of Questions'),
			#Field('Pass Ma
					


#	def edit_task(self, task_title, task_description, user, prerequisite, task_num_labelers, task_num_posts, task_random_label, task_upload_file):
			
#		try:
#			csvfile = open(str(task_upload_file), 'rb')# as csvfile:
			#print (csvfile)
#			readerR = csv.reader(csvfile, delimiter='|', skipinitialspace=True)
			#print (readerR)
#                       readerF = csv.reader(TextIOWrapper(task_upload_file), delimiter='|', skipinitialspace=True)
			#reader = csv.reader(open(task_upload_file, newline=''), delimiter='|')
			#print (readerF)
#			labelsF = next(readerR)
#			for rowF in labelsF:
		        #print (labelsF)
			#print (task_random_label)
#			task_obj = Task.objects.create(
#				title = task_title,
#				description = task_description,
#				num_labelers = task_num_labelers,
#				num_posts = task_num_posts,
#				random_label = task_random_label,
#				prerequisite = prerequisite,
#				creator = user)
			#print(task_random_label)
			
#			for label in labelsF:
#				#print (label)
#				label_object = Label.objects.create(content=label)				
#				task_obj.label_list.add(label_object)
				#print (label_object)
				
#			posts = readerR

#			for post in posts:
#				post_object = Post.objects.create(
#				content = post[0],
#				author = user)
#				#print (post)
#				task_obj.post_list.add(post_object)
#		except:
#			return None
#
#		return task_obj


############Update Labeler####################################
#class UpdateLabelerForm(forms.Form):

#	selectTask = forms.CharField(required=False)
	
#	def __init__(self, *args, **kwargs):
#		initial_arguments = kwargs.get('initial', None)
#		updated_initial = {}
#		lse = ''
#		if initial_arguments:
			# We have initial arguments, fetch 'user' placeholder variable if any
#			taskname = initial_arguments.get('Select Task', None)
#			labelers = initial_arguments.get('Participating Coders', None)
			#stp =labelers.decode('utf-8')
			#print (stp)
# Now update the form's initial values if user
#			updated_initial['Select Task'] = taskname
			#pp = labelers.encode("utf-8")
			#pp.decode("utf-8")
			#print (pp)			
#			tl = labelers.replace('\n', '')
#			tl = tl.replace('b\'', '\'')
#			tl = tl.replace("\'", '')
##			tl = tl.replace(" ", "")
#			tl = tl.replace(',','\n')			
#			tl = tl.replace("[", "")
#			tl = tl.replace("]","")
#			tl = tl.replace(" ", "")

#			tl = tl.replace(" ", "")
			#print(tl.str.decode('utf-8'))
#			print (tl)
			#test = bytes(tl, encoding='utf-8') 
			#test.decode('utf-8')
			#print (test)
			#tl.decode("utf-8", "replace")
#			str(tl, "utf-8", "strict")
#			updated_initial['Participating Coders'] = tl
            	# You can also initialize form fields with hardcoded values
            	# or perform complex DB logic here to then perform initialization
#            	updated_initial['comment'] = 'Please provide a comment'
            	# Finally update the kwargs initial reference
#		kwargs.update(initial=updated_initial)
#		super(UpdateLabelerForm, self).__init__(*args, **kwargs)
		#self.fields['Task Title'] = forms.CharField(max_length=50)
#		self.val = "";
		#pk = args[0]
#		listar = list(args)
		#field1= '0'		
#		field = 0
#		k = 1
		#current_url = resolve(request.path_info).url_name
		#print(current_url)

		#for c, item in enumerate(list(args), 1):
		 #  # print(c, item)
#		    item1 = item
		 #   if item != None:
		#	field = item
		#	k = c
		#	break
		    
		#item1 = i.next()
		
		#	i.next()
		
		#for i in list(args):
		  #print(i)
		#  field1= i		
		#print(k, field)
		#a = np.array(args)
		#b = [0,1]
		#print(list(a[b]))
		#num1 = None
		#field =list(args)
		#print(field.index("task new"))
		#task_name = ''
		#for num in args:
		 # if(num!=None):
		#task_name = num
      		  #print(num)

		#print (field.pop(0))
		  #print(Task.objects.get(title=field1))
		#print(Task.objects.filter(title=str(field)))
		 # if i!=None:
		#print(task_name)
		#field = self.getArgs(args)
		#print (self.getArgs(args))
		#print(self.get_first(args))
		
		
		#print(self.get_first(list(args)))		
#		l = list(self.get_first(args))
		#print(l , "h: ", l)
		#print([part.encode("utf8") for part in self.get_first(args)])

		#if ([part.encode("utf8") for part in self.get_first(args)] != []):
			#print("val: ")
	#	self.val = [part.encode("utf8") for part in self.get_first(args)]
		#print( kwargs.get('initial', None))
#		self.fields['Select Task'] = forms.CharField(required=False)
#		self.fields['Select Task'].widget.attrs['readonly'] = True
#ModelChoiceField(queryset=Task.objects.filter(title=[part.encode("utf8") for part in self.get_first(args)]))
#		else : 
			#print("val: ")
			#print(self.val)
#			self.fields['Select Task'] = None#str(self.val)#forms.ModelChoiceField(queryset=Task.objects.filter(title=self.val))		
		#print(flag)
		#if (task_name==''):
		#print(flag)			
		#self.fields['Select Task'] = forms.ModelChoiceField(queryset=Task.objects.filter(title=task_name))
#		self.fields['Participating Coders'] =forms.ModelChoiceField(queryset=Account.objects.all())##forms.CharField(max_length=5,
#		self.fields['Participating Coders'] = forms.CharField(widget=forms.Textarea, required=False)
		
		#print (self.fields['Participating Coders'])
#		self.helper = FormHelper()
#		self.helper.form_id = 'update_labeler_form'
#		self.helper.form_method = 'POST'
#		self.helper.form_action = '/task/update_labeler/'
#		self.helper.layout = Layout(
#			HTML("""<div class="panel panel-info">
#					<div class="panel-heading">
##						Add or Remove Labeler
#					</div>
					
#					"""),
			
			
			
#			HTML("""					
#				<div class="panel-body">
#				<p> <b>Note</b>: Select a task and add a labeler to it.</p>
#					"""),
#			Field('Select Task', placeholder=""),
#			Field('Participating Coders', placeholder="coder1@example.com \n coder2@example.com \n ..."),
#
			
#			)
		#print(self.fields['Select Task'])				
#		self.helper.add_input(Submit('update_labeler_submit', 'Submit', css_class='btn btn-info btn-sm pull-right'))


#	def update_labeler(self, task, participating_coders):
			
#		try:
#			#csvfile = open(str(task_upload_file), 'rb')# as csvfile:
			#print (csvfile)
		        #readerR = csv.reader(csvfile, delimiter='|', skipinitialspace=True)
			#print (readerR)
#                       readerF = csv.reader(TextIOWrapper(task_upload_file), delimiter='|', skipinitialspace=True)
			#reader = csv.reader(open(task_upload_file, newline=''), delimiter='|')
			#print (readerF)
			#labelsF = next(readerR)
#			for rowF in labelsF:
		        #print (labelsF)
			#print (task_random_label)
			#print(task)
			#print(coder)
			#participating_coders = self.cleaned_data['Participating Coders']
			#participating_coders= participating_coders.replace("\n", "")
#			coder_list = participating_coders.split()
			#print(coder_list)
#			participation_obj = None
#			print(task)
#			for coderP in coder_list:
#				print('coder' , coderP[1:])
#				coderP = coderP[0:]
			#subject = str.format("Task created for {0}", coder)
			#message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here: [WEBSITE_URL]\n\nBest,\nUCIPT Team", coder)
				#self.add_participant(task, coder)
#				print(coderP)
#				print(Task.objects.filter(title=task).values_list('id', flat=True).first())
				#print(task.pk)
#				coder_l = []
#				if not Participation.objects.filter(coder=coderP , task_id=Task.objects.filter(title=task).values_list('id', flat=True).first()) :					
#					print("here")
#					print(coderP)
#					participation_obj = Participation.objects.create(
#					task_id=Task.objects.filter(title=task).values_list('id', flat=True).first(),
#					coder=coderP)
#					print(participation_obj)
#					passwrd = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
#					passw = hashlib.sha224(passwrd.encode('utf-8')).hexdigest()
#					print(passwrd.encode('utf-8'))
#					print(passw)
#					User = get_user_model()
#					if not User.objects.filter(email=coderP) :
#						print ('there')	
#						User.objects.create(email=coderP)
#						user = User._default_manager.get(email=coderP)
#						#print (user)
#						user.set_password(passwrd)
##						user.save()
#						subject = str.format("Task created for {0}", coderP)
#						message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here: http://dblab-rack30.cs.ucr.edu/account/login\n Your password :{1} \nBest,\nUCIPT Team", coderP, passwrd)
        	                               # print (coderP)
                	                       # print (subject)
                        #self.add_participant(task, coder)
#						coder_l.append(coderP)
                                	        #print (coder_l)
                                        	#print ('right here')
#						send_mail(subject, message, 'sara.alaee@gmail.com', coder_l, fail_silently=False)
#					else : 
						#print ('there else')	
#						user = User._default_manager.get(email=coderP)
#						#print (user)
#						subject = str.format("Task created for {0}", coderP)
#						message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here: http://dblab-rack30.cs.ucr.edu/account/login\n \nBest,\nUCIPT Team", coderP)
        	                                #print (coderP)
                	                        #print (subject)
                        #self.add_participant(task, coder)
#						coder_l.append(coderP)
#                                	        #print (coder_l)
                                        	#print ('right here')
#						send_mail(subject, message, 'sara.alaee@gmail.com', coder_l, fail_silently=False)
				#		user.set_password(passwrd)
				#		user.save()
        				#form = self.form_class(request.POST)
       					#assert uidb64 is not None and token is not None  # checked by URLconf
				        #try:
				         #   uid = urlsafe_base64_decode(uidb64)	    
				          #  user = UserModel._default_manager.get(pk=uid)
	    
				        #except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            				#	user = None

					#user.set_password(passwrd)
				        #user.save()
#					subject = str.format("Task created for {0}", coderP)
#					message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here: http://dblab-rack30.cs.ucr.edu/account/login\n Your password :{1} \nBest,\nUCIPT Team", coderP, passwrd)
#					print (coderP)
#					print (subject)
			#self.add_participant(task, coder)
#					coder_l.append(coderP)
#					print (coder_l)
#					print ('right here')
#					send_mail(subject, message, 'sara.alaee@gmail.com', coder_l, fail_silently=False)
#					subject = str.format("Task created for {0}", coderP)
#					message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here:[http://0.0.0.0/account/signup]\n\nBest,\nUCIPT Team", coderP)
#					coder_l.append(coderP)
#					print (coder_l)
#					send_mail(subject, message, 'sara.alaee@gmail.com', coder_l, fail_silently=False)
#		except:
#			return None

#		return participation_obj

#	def get_first(iterable, default=None):
#		if iterable:
#			for item in iterable:
#				print(item)
#				return item
#			print(iterable)
#		return default

