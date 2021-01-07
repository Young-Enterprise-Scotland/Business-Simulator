# Pull the base image
FROM python:3.8.2

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
#Upgrade pip
RUN pip install pip -U
ADD requirements.txt /code/

RUN apt-get update
RUN apt-get install -y netcat
RUN pip install -r requirements.txt
RUN cat /wait-for-mysql.sh | tr -d '\r' > /wait-for-mysql.sh
RUN chmod +x /wait-for-mysql.sh
# Converts line ending of script and uninstalls dos2unix
ADD . /code/
