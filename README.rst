SearchIt
=======

SearchIt(previously Joineka) is modern search engine powered by Bing API that built with pure Python and Django framework. Feel free to copy and use (even research and commercial) but don't forget to contribute like add more i18n, security layer, etc because this was just MVP then collab together for the future of this project.


Basic Commands
--------------

Setup Project in Local Development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Make virtual environment
* Clone repository inside the env
* Move to repo directory then make sure you have list of package that you need in the project is compatible or not. If you find that some package not up-to-date, you must find update from newest package forker in project's github page. Simply add package name and it's github URL inside requirements/base.txt
* Then save edited package list and run this command::
	
    $ pip install -r requirements/local.txt

* Edit shorturls package inside lib/python3.x/site-packages/shorturls/templatetags/shorturl,py in line 5, 40, 44::

    $ export DATABASE_URL="sqlite:///db.sqlite"
    $ python3 manage.py migrate
    $ python3 manage.py createsuperuser
    $ python3 manage.py runserver 0.0.0.0:8000


Type checks
^^^^^^^^^^^

Running type checks with mypy:

::

  $ mypy core

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ pytest



VPS Deployment
------------------------

* Make sure doing bunch of command below::

    $ sudo apt update
    $ sudo apt install python3-pip python3-dev virtualenv  libpq-dev postgresql postgresql-contrib nginx curl

* Make postgres db inside, i know it's risky but for effective budget this still ok::

    $ sudo -u postgres psql


You can follow postgres setup section in `this page`_.
  
.. _`this page`: https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04

* Copy local bash_profile and paste into server terminal
* Just do the same thing like Local Development but only step 1 - step 3
* After save edited package list, you can run this command::

    $ pip install -r requirements/production.txt

* Create AWS IAM Access Key ID and Secret Key, then grab both to paste in some place
* Create S3 Bucket then grab then bucket name to paste in some place
* Add domain to Mailgun, grab the domain and Secret Key to paste in some place
* Edit shorturls package inside lib/python3.x/site-packages/shorturls/templatetags/shorturl,py in line 5, 40, 44 and continue::

    $ export DJANGO_SETTINGS_MODULE='config.settings.production'
    $ export DJANGO_SECRET_KEY='<secret key goes here>'
    $ export DJANGO_ALLOWED_HOSTS='<add current server ip, if gunicorn ready just change into domain>'
    $ export DJANGO_ADMIN_URL='9udf/'
    $ export MAILGUN_API_KEY='<mailgun key related to the domain>'
    $ export MAILGUN_DOMAIN='<mailgun sender domain (make new subdomain inside this sub)>'
    $ export DJANGO_AWS_ACCESS_KEY_ID='add secret access key generated from IAM'
    $ export DJANGO_AWS_SECRET_ACCESS_KEY='add access key generated from IAM'
    $ export DJANGO_AWS_STORAGE_BUCKET_NAME='make new from IAM then config in S3 as public'
    $ export DATABASE_URL='postgres://<postgres-username>:<postgres-password>@127.0.0.1:5432/<database-name>'
    $ export REDIS_URL='redis://127.0.0.1:6379/1'

* Comment config that force server to redirect to it's own installed SSL (we don't have enough money now, so use CF)::

    # SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
    # SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

* Doin normal Django setup::

    $ python manage.py makemigrations
    $ python manage.py migrate
    $ python manage.py collectstatic

* Add new port TCP/IP blank in port 8000 via Lightsail GUI then run::

    $ sudo ufw allow 8000


* Test the code, after that quit with ctrl + C::

    $ python3 manage.py runserver 0.0.0.0:8000

* Check Gunicorn exist or not(still in the same directory), then deactivate environment::

    $ file ../bin/gunicorn

* Create new gunicorn.service file::

    $ sudo nano /etc/systemd/system/gunicorn.service

* Fill that file with this code, after finish just save it::

    [Unit]
    Description=gunicorn daemon
    Requires=gunicorn.socket
    After=network.target

    [Service]
    User=ubuntu
    Group=www-data
    WorkingDirectory=/home/ubuntu/venv/core
    ExecStart=/home/ubuntu/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/venv/core/config.sock config.wsgi:application -e DJANGO_SETTINGS_MODULE='config.settings.production' -e DJANGO_SECRET_KEY='<creare excellent secret key>' -e DJANGO_ALLOWED_HOSTS='<if gunicorn = 52.76.195.29, if using domain = www.joineka.com' -e DJANGO_ADMIN_URL='< someURL/ >' -e DJANGO_BING_KEY='<add bing key>' -e DATABASE_URL="sqlite:///db.sqlite" -e REDIS_URL='redis://127.0.0.1:6379/1' -e DJANGO_AWS_STORAGE_BUCKET_NAME='<aws bucket name>' -e MAILGUN_API_KEY='<mailgun key>' -e MAILGUN_DOMAIN='registered domain in mailgun' -e DJANGO_AWS_ACCESS_KEY_ID='<access key id capslock couple with secret key>' -e DJANGO_AWS_SECRET_ACCESS_KEY='<secret access key couple with secret access key id>'

    [Install]
    WantedBy=multi-user.target

* Create new gunicorn.socket file::

    $ sudo nano /etc/systemd/system/gunicorn.socket

* Fill that file with this code, after finish just save it::

    [Unit]
    Description=gunicorn socket

    [Socket]
    ListenStream=/run/gunicorn.sock

    [Install]
    WantedBy=sockets.target

* Test Gunicorn files we added before::

    $ sudo systemctl start gunicorn.socket
    $ sudo systemctl enable gunicorn.socket

* After doing any modification to Codebase or Gunicorn files::

    $ sudo systemctl daemon-reload
    $ sudo systemctl restart gunicorn

* Check if Gunicorn ready to live::

    $ sudo systemctl status gunicorn.socket
    $ sudo systemctl status gunicorn

* Create nginx file for this project::

    $ sudo nano /etc/nginx/sites-available/<name Codebase(project) directory>

* Open cloudflare and add A DNS record point to current server IP for deploy project/ codebase

* Fill that file with this code then save

    server {
        listen 80;
        server_name <domain that already added to cloudflare>;

        if ($http_x_forwarded_proto = "http") {
            return 301 https://$server_name$request_uri;
        }

        location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
            root /home/ubuntu/env/kdco;
        }

        location / {
            include proxy_params;
            proxy_pass http://unix:/run/gunicorn.sock;
        }
    }

* Create soft link in Nginx's site-enabled directory::

    $ sudo ln -s /etc/nginx/sites-available/<name Codebase(project) directory> /etc/nginx/sites-enabled

* Check Nginx files that we added before, it should be 'ok'::

    $ sudo nginx -t

* Reload + restart nginx files (doin first time or make change in web server / Nginx)::

    $ sudo systemctl daemon-reload
    $ sudo service nginx restart


Further change like docker/ vagrant, ansible, sentry as soon as possible.

