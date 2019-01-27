FROM python:3.7-alpine

RUN pip install redis==3.0.1 gevent==1.4.0

COPY src .