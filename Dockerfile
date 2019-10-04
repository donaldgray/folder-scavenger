FROM alpine:3.9

RUN apk add --update --no-cache --virtual=run-deps \
  python3 \
  ca-certificates \
  && rm -rf /var/cache/apk/*

WORKDIR /opt/app
CMD ["python3", "-u", "folder-scavenger.py"]

COPY requirements.txt /opt/app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app /opt/app/
