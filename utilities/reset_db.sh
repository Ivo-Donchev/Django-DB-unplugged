#!/bin/bash

USERNAME="ivo"
DATABASE="django_db_unplugged"

sudo -u postgres dropdb --if-exists "$DATABASE"

sudo -u postgres createdb -O $USERNAME "$DATABASE"

python manage.py migrate

python manage.py shell -c 'from utilities import setup_db'
