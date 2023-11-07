FROM public.ecr.aws/docker/library/python:3.12-alpine

RUN apk add haproxy

COPY requirements.txt /
RUN python3 -m venv pysecrets \
    && source pysecrets/bin/activate \
    && pip3 install --no-cache-dir -r requirements.txt

COPY . /

CMD ["/run.sh"]
