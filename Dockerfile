FROM ubuntu
RUN apt-get update -y && apt-get install -y python-pip
COPY app /opt/folder-scavenger
WORKDIR /opt/folder-scavenger
RUN pip install -r requirements.txt
