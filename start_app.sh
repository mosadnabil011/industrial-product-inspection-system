#!/bin/bash

cd /home/force/Videos/graduation-project-master

mkdir -p logs

python3 app.py >> logs/app.log 2>&1
