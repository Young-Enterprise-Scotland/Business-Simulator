# Pull the base image
FROM python:3.8.3-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
#Upgrade pip
RUN pip install pip -U
ADD requirements.txt /code/

#Alpine stuff
RUN apk update
RUN pip install --upgrade pip
RUN apk add python3-dev
#RUN apk add default-libmysqlclient-dev
RUN apk add gpgme-dev
RUN apk add libc-dev
RUN apk add gcc jpeg-dev zlib-dev libffi-dev freetype-dev musl-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev cairo-dev pango-dev gdk-pixbuf-dev
RUN apk add mariadb-dev
RUN apk add dos2unix
#Install dependencies
RUN pip install -r requirements.txt
RUN cat /wait-for-mysql.sh | tr -d '\r' > /wait-for-mysql.sh
# Converts line ending of script and uninstalls dos2unix
RUN dos2unix /wait-for-mysql.sh && apk del dos2unix && rm -rf /var/lib/apt/lists/*
ADD . /code/

#RUN apk add gcc jpeg-dev zlib-dev libffi-dev freetype-dev musl-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev cairo-dev pango-dev gdk-pixbuf-dev
