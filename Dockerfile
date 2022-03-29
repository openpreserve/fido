FROM python:3.6-alpine as builder

LABEL maintainer="carl.wilson@openpreservation.org" \
      org.openpreservation.vendor="Open Preservation Foundation" \
      version="0.1"

RUN  apk update && apk --no-cache --update-cache add gcc build-base libxml2-dev libxslt-dev git

WORKDIR /src

COPY setup.py setup.py
COPY requirements.txt requirements.txt
COPY README.md README.md
COPY fido/* fido/

RUN mkdir /install && pip install -U pip && pip install -r requirements.txt --prefix=/install && pip install --prefix=/install .

FROM python:3.6-alpine

RUN apk update && apk add --no-cache --update-cache libc6-compat libstdc++ bash libxslt
RUN install -d -o root -g root -m 755 /opt && adduser --uid 1000 -h /opt/fido_sigs -S eark && pip install -U pip python-dateutil

WORKDIR /opt/fido_sigs

COPY --from=builder /install /usr/local
COPY . /opt/fido_sigs/
RUN chown -R eark:users /opt/fido_sigs

USER eark

EXPOSE 5000
ENV FLASK_APP='fido.signatures'
ENTRYPOINT flask run --host "0.0.0.0" --port "5000"
