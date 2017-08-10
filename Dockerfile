FROM totem/python-base:2.7-trusty

RUN apt-get update -y --fix-missing
RUN apt-get install -y ca-certificates python-dev libssl-dev libldap2-dev libsasl2-dev

ADD requirements.txt /opt/
RUN pip install -r /opt/requirements.txt

RUN apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

WORKDIR /opt/bouncer

EXPOSE 4010

ENTRYPOINT ["python", "-m", "bouncer", "-H", "0.0.0.0"]
CMD [""]

ADD . /opt/bouncer
