# django_rest_template

This template provides a setup to easily develop RESTFUL servers.
It implements following features:

## Features

### Security

- User Management Backend (http://localhost:8000/admin)
  - Create Users / Groups
  - Define permissions
  - Block authorization (Tokens)
  - https://docs.djangoproject.com/en/5.0/ref/contrib/admin/
- JWT Authorization
  - Is used to authorize REST clients with user credentials
  - https://django-rest-framework-simplejwt.readthedocs.io/en/latest/
- Role-based access restrictions
  - restricting access based on roles
  - Model level permission
  - https://www.django-rest-framework.org/api-guide/permissions/
- Access-log
  - Needed for sensitive data
  - Every request will be logged with username and IP

### Database

- Object–relational mapping (ORM)
  - Helpful tool to use database table in objects
  - Mapping Classes to Data Table
  - https://docs.djangoproject.com/en/5.0/topics/db/models/
- Database migration
  - Easy set-up of databases
  - https://docs.djangoproject.com/en/5.0/topics/migrations/

### Webservice

- Apps
  - Django method to split functionalities
  - https://docs.djangoproject.com/en/5.0/ref/applications/
- Django REST framework
  - Clean structure of functionalities
  - Serialization of model objects
    - https://www.django-rest-framework.org/api-guide/serializers/
  - Hyperlink based Model object relations
    - https://www.django-rest-framework.org/api-guide/serializers/#hyperlinkedmodelserializer
  - Class based view handlers
    - https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset
  - https://www.django-rest-framework.org/
- Browsable Swagger API
  - http://localhost:8000/swagger
  - http://localhost:8000/redoc
  - https://drf-yasg.readthedocs.io/en/stable/

### Examples

- Simple example of storing Patient Appointment data
  - can be found in ./server/django_web_template/appointment
- Simple example for a client
  - found in client/login_test.py
  - needs 'requests' library

### Docker

- Deployment ready Docker set up
  - Django -> Gunicorn -> nignx set-up
  - Django -> Postgres set-up
  - Django container cron job
- Tool to create and personalize docker composition settings and generate password / secret_key
  - ./install_scripts/create_docker_env.py
- Docker secrets for passwords secret_key
  - https://docs.docker.com/compose/use-secrets/
- Docker compose file to run standalone
  - https://docs.docker.com/compose/

## Development

Before we start please be sure you either forked downloaded this template.
Create and venv installed the requirements.

```shell
$ python -m venv venv
$ source ./venv/Scripts/activate
$ pip install -r ./server/requirements.txt
```

Zsh

```zsh
$ python -m venv venv
$ source ./venv/bin/activate
$ pip install -r server/requirements.txt
```

To start your own Rest-app we use the django framework to kick things off.

```shell
$ cd ./server
$ python manage.py startapp appointment
```

this will create a new package with all the necessary files.
See more in this tutorial https://docs.djangoproject.com/en/5.0/intro/tutorial01/

### Model

Let us define a small model of Patients and Appointments in 'server/appointment/models.py'

```python
from django.db import models


# Create your models here.
class Patient(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    birth_date = models.DateField()

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.birth_date})'


class Appointment(models.Model):
    date = models.DateField()
    patient = models.ForeignKey(Patient, related_name="appointments", on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.date}: {self.patient.last_name}'
```

Each class represents a table. The defined variables define columns on the tables.
Primary-key will be automatically created, so no need to define one if nothing special is needed.

`patient = models.ForeignKey(Patient, related_name="appointments", on_delete=models.CASCADE)` defines a relation ship
between the two tables.
If you have an Appointment object you can access the responding Patient object though the
attribute `appointment1.patient`.
Since we also defined `related_name=appointments` we can further access all responding Appointment object`with`patient1.appointments`

More infos https://docs.djangoproject.com/en/5.0/topics/db/models/

### Serializer

With the models we can read and write data to the Database. Next we create functionalities to easily receive and respond
objects to clients.
Create a file server/appointment/serializers

```python
from rest_framework import serializers
from appointment.models import Patient, Appointment


class PatientSerializer(serializers.HyperlinkedModelSerializer):
    appointments = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='appointment-detail'
    )

    class Meta:
        model = Patient
        fields = ['url', 'first_name', 'last_name', 'birth_date', 'appointments']


class AppointmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Appointment
        fields = ['url', 'date', 'patient']
```

Using the `HyperlinkedModelSerializer` conveniently creates callable urls for the clients to request / update /
delete / use an object.
Also, we define a `Meta` subclass containing the model Class to serialize and the fields which should be contained in
the respsonse.
More on https://www.django-rest-framework.org/api-guide/serializers/#hyperlinkedmodelserializer

With `serializers.HyperlinkedRelatedField` we can also serialize related Appointments of the defined Person object.
The parameter `view-name` defines underlying model class of the relation. The appendix `'-detail'` is
django-rest-framework standard.
See more https://www.django-rest-framework.org/api-guide/relations/#hyperlinkedrelatedfield

#### Add to admin site (optional)

You can add your models to the Django-Admin backend to view and manipulate the data from the administrator site.
Edit ./server/appointment/admin.py

```python
from django.contrib import admin

from appointment.models import Appointment, Patient

admin.site.register(Appointment)
admin.site.register(Patient)
```

### View

Next step in our app is to create the view in ./server/appointment/views.py

```python
from rest_framework import viewsets

from appointment.models import Patient, Appointment
from appointment.sezializers import PatientSerializer, AppointmentSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows patients to be viewed or edited.
    """
    model = Patient
    queryset = Patient.objects.all().order_by('last_name', 'first_name')
    serializer_class = PatientSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows patients to be viewed or edited.
    """
    model = Appointment
    queryset = Appointment.objects.all().order_by('date')
    serializer_class = AppointmentSerializer
```

Views will handle the requests. Inheriting `viewsets.ModelViewSet` automatically handles all requests of a model
object.
You will be able to view all objects in the database of this class, view just a requested one or add, delete, update
objects.

- `model` defines the database model which will be handled
- `queryset` defines a database query to retrieve all objects of the class. When you use pagination it is wise to sort
  them.
- `serializer_class` defines the serializer to format the object to json
  See more on https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset

If your request is not model specific you will have plenty other possibilities.
https://www.django-rest-framework.org/api-guide/views/

### Install app in Django

First we have to tell django, that we have a new app. Edit the file ./server/django_web_template and add your module to
the list of installed apps.

```python
...
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'django_web_template.jwt_extension',
    'appointment',
]
...
```

Please be sure you do not change anything else if you do not understand the app properly.

We now have to add our Views to the router in ./server/django_web_template/urls.py

```python
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from appointment import views as rest_views

router = routers.DefaultRouter()
router.register(r'patients', rest_views.PatientViewSet)
router.register(r'appointment', rest_views.AppointmentViewSet)

...

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

```

`router.register(r'patients', rest_views.PatientViewSet)` the first parameter defines the path to access the view
https://www.django-rest-framework.org/tutorial/6-viewsets-and-routers/#using-routers
https://docs.djangoproject.com/en/5.0/topics/http/urls/

### Migrate

Since we added new model which will have to be created as table in the database. We have to create a migration for our
app
We can use django tools for this:

```shell
$ cd ./server
$ python manage.py makemigrations appointment
Migrations for 'appointment':
  appointment\migrations\0001_initial.py
    - Create model Patient
    - Create model Appointment
```

This tool will automatically create a submodule in appointments called `migrations` and our first migration.
With every `makemigrations` we will receive a new file with the changes of our models.
Therefore, these files help us to upgrade or downgrade our database in production without loosing data.Be sure you
upload these files into github.
https://docs.djangoproject.com/en/5.0/topics/migrations/

We than can install it in our database.

```shell
$ python manage.py migrate
Operations to perform:
  Apply all migrations: admin, appointment, auth, contenttypes, sessions, token_blacklist
Running migrations:
  Applying appointment.0001_initial... OK
```

If you did not run this command yet the output will be longer

Now you can run the app as descriped above in Deployment

## Deployments

### Local Deployment

Before we start please be sure you either forked downloaded this template.

Create venv

```shell
$ python -m venv venv
$ source ./venv/Scripts/activate
```

Lets jump into the './server' path, where the actual django code is stored.

```shell
$ cd ./server
```

Install postgresql (for mac)

```shell
$ brew install postgresql
```

Install requirements

```shell
$ pip install -r ./requirements.txt
```

Django_web_template depends on environment variables. The easiest way to provide them is to copy the file '
./server/.env.example'

```shell
$ cp .env.example .env
```

Now we can set-up the database. Since the '.env' file routes the database to a local sqlite file. Which will be created
after installing our tables.

```shell
$ python manage.py migrate
```

And create a admin user

```shell
$ python manage.py createsuperuser
Username (leave blank to use 'amazing.user'): admin
Email address: test@test.ch
Password:
Password (again):
This password is too short. It must contain at least 8 characters.
This password is too common.
This password is entirely numeric.
Bypass password validation and create user anyway? [y/N]: y
Superuser created successfully.
```

Finally, we can start django:

```shell
$ python manage.py runserver
```

We can check if everything is running. http://localhost:8000/admin
Congrats!!

Migrate the database to get the default authentication tables plus your UserProfile table:

```shell
python manage.py makemigrations
python manage.py migrate
```

### Docker deployment

Install docker https://docs.docker.com/engine/install/.
Please be aware that you need additional tools to run Docker on Windows. https://docs.docker.com/desktop/wsl/
Before we start please be sure you either forked downloaded this template.

create necessary docker environment files

```shell
$ python ./install_scripts/create_docker_env.py
```

Follow the instructions:

```
Welcome to docker environment creation
Creating .env file for docker
Define Hostname from which django will server (leave blank to use 'localhost'): localhost
Define Host port from which django will server (leave blank to use '8000'): 123456
Be sure you change the 'nginx.conf' to listen to the same port and 'docker-compose.yml' to map nginx to the same port
Define Protocol which django will server (leave blank to use 'http'): http
Postgres Database name (leave blank to use 'django'): django
Postgres Username (leave blank to use 'django'): django
Postgres Password (leave blank to generate):
.env to ..
DB pw written to ..\secrets
DB url written to ..\secrets
Secret key written to ..\secrets
```

Please be aware that you need to manually change the listen port in '/nginx/nginx.conf' and the mapping in /compose.yaml

```
server {

    listen 12345;
    location /static/ {
        alias /var/staticfiles/;
    }

    location /media/ {
        alias /var/mediafiles;
    }

    location / {
        limit_req zone=mylimit burst=20 nodelay;
        real_ip_header X-Forwarded-For;
        real_ip_recursive on;
        proxy_pass http://web_app;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Host $http_host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_set_header Host $host:$server_port;
        proxy_redirect off;
    }

}
```

```yaml
nginx:
  image: django_server
  build: ./nginx
  restart: always
  ports:
    - ${PORT}:12345
  volumes:
    - static_volume:/var/staticfiles
    - media_volume:/var/mediafiles
  depends_on:
    - web
```

This script will create the file .env in the root folder which general variables for the docker compose file and secrets
in /secrets which are needed to securely store passwords and are then used in the compose process.

Next we build and run the composition

```shell
$ docker compose build
$ docker compose up -d
```

`docker compose build` creates runnable images from our sources.'`docker compose up` runs the images in containers.
-d is to de-attach the docker composition for the current shell process.
You can use the command `docker compose up --build -d` to run in one line

We can check if everything is running. http://localhost:8000/admin
Admin user and password are by default: admin 123456
This can be changed in the ./compose.yaml file
Congrats!!

Let's stop it

```shell
$ docker compose down
```

### Explanation

Docker builds/downloads three images.

- 'django*proxy' which serves static files (i.e. *.css, \_.js) files and routes requests to 'django_server'.
- 'django_server' runs your django app with a gunicorn wsgi.
- 'postgres' runs the postgres dbms for 'django_server' to access

```shell
$ docker image
REPOSITORY      TAG       IMAGE ID       CREATED          SIZE
django_server   latest    b34ab5c22521   35 minutes ago   222MB
django_proxy    latest    ecacf9d5acf9   2 hours ago      41.1MB
postgres        latest    b0b90c1d9579   4 weeks ago      425MB
```

With `docker compose up` docker starts the images in containers.

```shell
$ docker container ls
CONTAINER ID   IMAGE           COMMAND                  CREATED         STATUS                   PORTS                            NAMES
e703812f3b5d   django_proxy    "/docker-entrypoint.…"   6 minutes ago   Up 6 minutes             80/tcp, 0.0.0.0:8000->8000/tcp   django_web_template-nginx-1
f70340c49b9e   django_server   "/bin/sh -c 'python …"   6 minutes ago   Up 6 minutes                                              django_web_template-web-1
cbb0eb1e4005   postgres        "docker-entrypoint.s…"   6 minutes ago   Up 6 minutes (healthy)   5432/tcp                         django_web_template-db-1
```

Also it creates a virtual network so the different containers can communicate with leaving the HOST computer.

```shell
$ docker network ls
NETWORK ID     NAME                          DRIVER    SCOPE
64e8fb510274   bridge                        bridge    local
df52f6304d32   django_web_template_default   bridge    local
85c377eaa6f2   docker_gwbridge               bridge    local
59f5a9bac522   host                          host      local
03a8e848ad40   none                          null      local
```

Lastly it creates three virtual volumes to persistently store data.

- django_web_template_db-data: storage for postgres data files (only postgres has access)
- django_web_template_media_volume: storage for media files to store uploads (shared between django_proxy and
  django_server)
- django_web_template_static_volume: storage for static files. Content will be created by django_server and served by
  django_proxy

```shell
docker volume ls
DRIVER    VOLUME NAME
local     django_web_template_db-data
local     django_web_template_media_volume
local     django_web_template_static_volume
```

## Troubleshooting

### psycopg2/psycopg2-binary Installation Issues

If you encounter issues installing psycopg2-binary, try one of these solutions:

1. Install system dependencies for psycopg2:

   - **Ubuntu/Debian**: `sudo apt-get install python3-dev libpq-dev`
   - **CentOS/RHEL**: `sudo yum install python3-devel postgresql-devel`
   - **macOS**: `brew install postgresql`

2. Use psycopg2 instead of psycopg2-binary:

   - Replace psycopg2-binary with psycopg2 in requirements.txt
   - This requires the PostgreSQL development libraries to be installed

3. Try an earlier version of psycopg2-binary (e.g., 2.9.5)

4. For macOS with M1/M2 chips, you might need to set environment variables:
   ```bash
   export LDFLAGS="-L/opt/homebrew/opt/openssl@1.1/lib -L/opt/homebrew/opt/libpq/lib"
   export CPPFLAGS="-I/opt/homebrew/opt/openssl@1.1/include -I/opt/homebrew/opt/libpq/include"
   ```

### Django Migration Issues

If you encounter migration issues:

1. Reset your migrations (for development only):

   ```bash
   find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
   find . -path "*/migrations/*.pyc" -delete
   python manage.py makemigrations
   python manage.py migrate
   ```

2. If using Docker, you might need to rebuild:
   ```bash
   docker compose down -v  # Remove volumes
   docker compose build --no-cache
   docker compose up -d
   ```
