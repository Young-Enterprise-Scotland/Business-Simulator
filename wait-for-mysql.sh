#!/bin/sh

# while ! nc -z db 52000 ; do
#     echo "Waiting for the MySQL Server"
#     sleep 3
# done

sleep 15
python3 manage.py makemigrations
python3 manage.py migrate
python3 db_populate
python3 manage.py runserver 0.0.0.0:8000