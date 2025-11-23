FROM python:3.13-alpine

WORKDIR /app
COPY bridge.py /app/
COPY requirements.txt /app/

RUN pip install --upgrade --root-user-action=ignore pip && \
    pip install --root-user-action=ignore -r requirements.txt && \
    mkdir config


CMD "python" "bridge.py"
