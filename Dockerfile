FROM continuumio/miniconda3

MAINTAINER chiau.hung.lee

ENV FLASK_APP run.py

RUN mkdir /app
RUN mkdir /app/musicsheet
RUN chmod 777 /app/musicsheet

ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5000
VOLUME /app/musicsheet

CMD ["flask","run","--host=0.0.0.0"]

# docker build -t music-sheet-pdf .
# docker run -d -p 5000:5000 music-sheet-pdf 

