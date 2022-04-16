# Dockerfile, Image, Container
FROM python:3.10
FROM ubuntu:20.04

RUN apt update
RUN apt upgrade -y
RUN apt install -y ffmpeg
RUN apt install -y python3-pip

ADD main.py .
ADD requirements.txt .

RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]