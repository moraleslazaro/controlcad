# DESCRIPTION: Create a Python/Django environment to run ControlCAD
# AUTHOR: Lazaro Morales <moraleslazaro@gmail.com>
# COMMENTS:
#	This file describes how to build a basic docker image with the
#	tools needed to run the ControlCAD app. Run this commands from 
#	the ControlCAD folder.
# Usage:
#
#	# Build the image
#	docker build -t moraleslazaro/django .
#
#       # Running docker client and server on the same host using mount will
#       # update the development folder automatically.
#	docker run --rm --mount type=bind,source=${pwd},target=/controlcad -p 8080:8000 moraleslazaro/django
#
#   	# Running docker server on a different hosts without the controlcad folder
#	docker run -d --rm -p 8080:8000 moraleslazaro/django  

# Base docker image
FROM debian

LABEL MAINTAINER Lazaro Morales <moraleslazaro@gmail.com>

# Install and setup the environment
WORKDIR /controlcad
COPY . /controlcad
RUN apt-get update && apt-get install python-pip -y && pip install -r requirements.txt

# Autorun ControlCAD
ENTRYPOINT [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

