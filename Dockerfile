ARG BUILD_FROM=python:3.13-alpine
FROM ${BUILD_FROM}

WORKDIR /app
COPY bridge.py /app/
COPY requirements.txt /app/

RUN pip install --upgrade --root-user-action=ignore pip && \
    pip install --root-user-action=ignore -r requirements.txt && \
    mkdir config

COPY run.sh /
RUN chmod a+x /run.sh

CMD ["/run.sh"]
