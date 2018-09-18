# Crowdtagger


## Overview
This repository contains source code for the [crowdtagger](http://dblab-rack30.cs.ucr.edu) site which is created with Python and Django.

This project helps with the collaborative labeling and its goal is to provide a platform for labelers from around the world to share the labeling tasks. It can be deployed via different approaches with web server like Apache and database service like PostgreSQL.

The goal of this project is for user to easily built and deploy his own collaborative labeling service as well as maintain the site.

## Project Structure
```
[labelingsystem]/                  <- project root
├── [labelingsystem]/              <- Django root
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── account/
├── classify/
│   ├── Model.py					 <- classify model
├── label/
│   ├── Model.py					 <- label model
├── post/
│   ├── Model.py					 <- post model
├── quiz/
│   ├── Model.py					 <- quiz model
├── response/
│   ├── Model.py					 <- response model
├── task/
│   ├── Model.py					 <- task model, database model
├── manage.py
├── media/
├── static/
└── templates/
    ├── base.html
    └── about.html
```
## Using docker
The easiest way to run this project is to use docker as it has the binaries and all dependencies pre-installed.
1. Install docker
2. Inside this directory, run:`docker build . -t [IMAGE_TAG]`.
3. (TODO)

## Running from github
### 💾 Installation and requirements on Ubuntu 16.04
Crowdtagger requires Python 3.4+, Apache 2.2+, PostgreSQL or MySQL and OS-specific dependency tools.
1. Clone this repository: `git clone https://github.com/UC-Riverside-DatabaseLab/Labeler.git`.
2. `cd` into `labelingsystem`: `cd /.../labelingsystem`.
3. Install [virtualenv](https://github.com/pypa/virtualenv) using pip: `pip install virtualenv`.
4. Create a new python3 virtualenv called `venv`: `virtualenv --python=/usr/bin/python3 venv`.
5. Set the local virtualenv to `venv`: `source venv/bin/activate`. If all went well then your command line prompt should now start with `(venv)`. 
6. Install the requirements: `python3 -m pip install -r requirements.txt`.


### 💾 Configuring Database service on Ubuntu 16.04
Django applications can be built with different database service. In this guide, we'll demonstrate how to install and configure PostgreSQL and MySQL to use with this project.
#### PostgreSQL
1. Install PostgreSQL: `sudo apt-get install python-pip python-dev libpq-dev postgresql postgresql-contrib`.
2. Login into the database as postgres user: `sudo -u postgres psql`.
3. Create a new database for this project: `CREATE DATABASE myproject;`.
4. Create a new user: `CREATE USER myprojectuser WITH PASSWORD 'password';`.
5. Grant all privileges of the new database to the new user : `GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;`. You will be using this user and database to access the PostgreSQL service in Django application.
6. End user session and exit: `\q` and `exit`.
7. Install PostgreSQL client package if we want to connect it to Django: `python3 -m pip install django psycopg2`.

#### MySQL or MariaDB
1. Install MySQL: `sudo apt-get install python-pip python-dev mysql-server libmysqlclient-dev` or MariaDB `sudo apt-get install python-pip python-dev mariadb-server libmariadbclient-dev libssl-dev`. You will be asked to select and confirm a password for the administrative account.
2. Login into the database as the administrative user: `mysql -u root -p`. Use the password you just set during the installation.
3. Create a new database for this project: `CREATE DATABASE myproject;`.
4. Create a new user: `CREATE USER myprojectuser@localhost IDENTIFIED BY 'password';`.
5. Grant all privileges of the new database to the new user : `GRANT ALL PRIVILEGES ON myproject.* TO myprojectuser@localhost;`. You will be using this user and database to access the MySQL or MariaDB service in Django application.
6. End user session and exit: `exit`.
7. Install MySQL client package if we want to connect it to Django: `python3 -m pip install django mysqlclient`.

#### Edit Django settings for database setup
Once the installation is completed, you can connect the django application with the database service by editing the `labelingsystem/labelingsystem/settings.py`
1. `cd` into `labelingsystem`: `cd /.../labelingsystem/labelingsystem`.
2. Edit the `settings.py` and find the attribute `DATABASE`
3. Change it to following if you are using PostgreSQL
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'myproject', // the database name you created in the last step.
        'USER': 'myprojectuser', // the user name you created.
        'PASSWORD': 'password', // the password you use to create the user.
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
4. Change it to following if you are using MySQL or MariaDB
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'myproject', // the database name you created in the last step.
        'USER': 'myprojectuser', // the user name you created.
        'PASSWORD': 'password', // the password you use to create the user.
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
#### Database migration
1. `cd` into `labelingsystem`: `cd /.../labelingsystem`.
2. Run `./deletemigrations.sh` to remove all the existing migrations.(Caution: do not run this if you have already migrated the database and want to make changes to the models later)
3. Run `python3 manage.py makemigrations label post quiz task response` to make the migrations.
4. Run `python3 manage.py migrate` to migrate the database.

### Configuring Email service
Django applications can be built with different email service. In this guide, we'll demonstrate how to configure this project using gmail backend.
1. Login into your Google account.
2. Go to your Google Account settings, find Security -> Account permissions -> Access for less secure apps, enable this option. You can access this option [here](https://myaccount.google.com/lesssecureapps?pli=1).
#### Edit Django settings for email setup
1. `cd` into `labelingsystem`: `cd /.../labelingsystem/labelingsystem`.
2. Edit the `settings.py` and find the attributes related to emails.
3. Change it to following
```
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'email_account' # your server gmail account name.
EMAIL_HOST_PASSWORD = 'password' # your server gmail password.
EMAIL_FROM = 'from@gmail.com' # the email address you want to sent from
EMAIL_TO = 'to@gmail.com'# the email address you want to receive applications.
```

### ▶️ Deployment
Django applications can be deployed via different approaches. In this guide, we'll demonstrate how to deploy this project directly and using Apache server.
#### Finish Django settings
Here is a detailed introduction about some of the vital attributes you need to configure before you deploy the project.
 
* `MEDIA_DIR`: the path of the media files, you should move your media files to this place if you want to deploy the project using Apache, or change it to `os.path.join(BASE_DIR, 'media')` if you want to deploy the project directly.
* `STATIC_DIR`: the path of the media files, you should move your static files to this place if you want to deploy the project using Apache, or change it to `os.path.join(BASE_DIR, 'static')` if you want to deploy the project directly.
* `SECRET_KEY`: create your own secret key and use it here, you can use this [tool](https://www.miniwebtool.com/django-secret-key-generator/)

for all the other attributes, please read the comments or visit [here](https://docs.djangoproject.com/en/2.0/ref/settings/) to understand its purpose


#### Direct server
1. Make sure you complete the installation of requirements and configuration of database as well as email services.
2. `cd` into `labelingsystem`: `cd /.../labelingsystem`.
3. Run `python3 manage.py runserver 127.0.0.1:8000` to start Django application in local
4. Run `sudo ufw allow 8000` if you have firewall enabled or you can use a different port number if port 8000 is occupied.
5. If the terminal shows that `Starting development server at http://127.0.0.1:8000/`, this means you have successfully deployed this project directly.
6. Open any browser in your OS and reach `http://127.0.0.1:8000/`, you shall see the login page of the crowdtagger.

#### Apache server
In this guide, we'll demonstrate how to deploy this project using Apache server on both CentOS 7 and Ubuntu 16.04.
##### > Ubuntu 16.04
1. Install Apache 2: `sudo apt-get install apache2`. Verify the version of your Apache, make sure it's higher than 2.2.
2. Start Apache service: `sudo systemctl start apache2`.
3. Verify the installation is successful by view port 80 of localhost in your browser, you shall see a welcome page of Apache.
4. Install mod-wsgi: `sudo apt-get install libapache2-mod-wsgi-py3`.
5. Create a new site configuration file: `sudo vim /etc/apache2/sites-available/crowdtagger.conf`
##### > CENTOS 7.0
1. Install python 3.5 if there is no python environment. You can refer to [this tutorial](https://linuxize.com/post/how-to-install-python-3-on-centos-7/). We will assume you have python3, pip installed and virtualenv enabled.
1. Install Apache 2: `sudo yum install httpd`. Verify the version of your Apache, make sure it's higher than 2.2.
2. Start Apache service: `sudo apachectl start`.
3. Install httpd-devel: `sudo yum install -y httpd-devel`.
4. Install mod-wsgi: `sudo yum install mod_wsgi`.
5. Edit `/etc/httpd/conf/httpd.conf` and add one line
```
LoadModule  wsgi_module modules/mod_wsgi.so
```
6. Restart Apache to make it effective: `sudo apachectl restart`.
7. Create a new site configuration file: `sudo vim /etc/apache2/sites-available/crowdtagger.conf`
##### > Edit Site configurations
Edit the configuration file to following if you are using Apache 2.4+.
```
<VirtualHost *:80>
    ServerName www.yourdomain.com # your IP address
    ServerAlias otherdomain.com
    ServerAdmin domain@gmail.com
  
    Alias /media/ /path/to/media/ # MEDIA_DIR you set in the settings.py
    Alias /static/ /path/to/static/ # STATIC_DIR you set in the settings.py
  
    <Directory /path/to/media/>
        Require all granted
    </Directory>
  
    <Directory /path/to/media/>
        Require all granted
    </Directory>
    
    <Directory /.../labelingsystem/>
        Require all granted
    </Directory>
  
    WSGIScriptAlias / /.../labelingsystem/labelingsystem/wsgi.py # path to the root folder of the project
    WSGIProcessGroup labelingsystem
    WSGIApplicationGroup %{GLOBAL}   
    WSGIDaemonProcess project python-path=/.../labelingsystem/:/.../labelingsystem/venv/lib/python3.*/site-packages/ # python3.* depends on your python version.

    <Directory /.../labelingsystem/labelingsystem/>
    <Files wsgi.py>
        Require all granted
    </Files>
    </Directory>
</VirtualHost>
```
If you are using Apache 2.2, replace all the `Require all granted` to
```
Options -Indexes
AllowOverride All
Order allow,deny
Allow from all
```
**Remember to restart Apache service to make the configuration file effective.**
##### > Collect Static files
1. `cd` into `labelingsystem`: `cd /.../labelingsystem`.
2. Run `python3 manage.py collectstatic`. By default the collected static files will be stored in `/var/www/static`, but you can always move it to the `STATIC_DIR` you set in the `settings.py`.

##### > Edit files Permission 
1. `cd` into the folder that contains the project root folder `labelingsystem`.
2. Edit permission of the root folder: `sudo chmod -R 644 labelingsystem`.
3. Edit permission of the files in root folder: `sudo find labelingsystem -type d | xargs chmod 755`.
4. `cd` into the folder that contains the `static` folder.
5. Edit permission of the root folder: `sudo chgrp -R www-data static && sudo chmod -R g+w static`.
6. `cd` into the folder that contains the `media` folder.
7. Edit permission of the root folder: `sudo chgrp -R www-data media && sudo chmod -R g+w media`.

##### > RUN
Open any browser in your OS and reach `www.yourdomain.com`, you shall see the login page of the crowdtagger.

## Run the crowdtagger
### Initialization
if you have successfully deployed the project using either way(direct or Apache), you can assign yourself as a super user.
1. `cd` into `labelingsystem`: `cd /.../labelingsystem`.
2. Run `python3 manage.py createsuperuser`.
3. You will be prompt to type in your username and password, please use your email as the username.
4. Reach the crowdtagger login page and you can login use the username and password you just created.
### Create new user
As a superuser, you can have administrator views of all the current models in the Django application including the users. To create new user, you need to follow these steps.
1. Login into the website as the super user.
2. Navigate to Administration View -> Users -> ADD USER
3. Type in username(email address) and password for the new user, then click save.
4. The user is created now. By default, it's in active status.
### Change user status
As a superuser, you can change the status of an user anytime by following these steps.
1. Login into the website as the super user.
2. Navigate to Administration View -> Users
3. Click on the user email address you want to change its status.
4. There are three possible status:
* **Active**: user with lowest privilege, can only take task assigned by higher level users.
* **Staff**: user with privilege to create task/quiz and assign them to other users, can also take task themselves.
* **Superuser**: user with highest privilege, in addition to staff privilege superuser can also view and modify the user status and task/quiz details.
5. You can then change the status of an user by click the corresponding select boxes, e.g. if you want to change a user to stuff, you need to select both **active** and **staff**.
### Tutorial
For more information, please refer to this [tutorial page](http://dblab-rack30.cs.ucr.edu/about/) to learn the details about the terminology and how to run the crowdtagger as different characters.
## Caveats
#### Q: What happens if I want to edit the code when it's already deployed using Apache?

You must run `sudo apachectl restart` (in CENTOS 7.0) or `sudo systemctl restart apache2` (in Ubuntu 16.04) every time you make any changes to the code the reflect the changes
#### Q: What happens if I want to edit the model description in the backend database?

Aside from restart Apache service, you also need to Run `python3 manage.py makemigrations yourapp` to make migrations and `python3 manage.py migrate yourapp` to actually migrate the changes to the model in database.

#### Q: Why is my webpage scrambled and does not appear correctly?
Make sure you have run the `python3 manage.py collectstatic` and put the `static` folder in the correct place(specified in `STATIC_DIR`).

#### Q: Why my webpage shows "you have no permission to access ..."?
Make sure you set the correct permission to all files related to the project, please refer to Edit files Permission [Section](#edit-files-permission).
#### Q: What if I have other errors when I try to deploy it using Apache?
You should first run a direct server to make sure there is no error on Django side. Then you can view the error log of Apache `/var/log/httpd/access_log` (in CENTOS 7.0) or `/var/log/apache2/access.log` (in Ubuntu 16.04) to debug the Apache side.

## Your feedback

Do you encounter any problems when deploying this project? You can contact us at <vagelish@gmail.com>.
