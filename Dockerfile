FROM python:3.7

RUN pip install requests datetime

COPY . /opt/EnergyStar

WORKDIR /opt/EnergyStar

CMD tail -f /dev/null