#!/bin/bash

./deletemigrations.sh
./makemigrations.sh
python3 manage.py migrate
python3 manage.py runserver 127.0.0.1
