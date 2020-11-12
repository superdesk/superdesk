FROM python:3.6

# install server
WORKDIR /opt/superdesk/
COPY requirements.txt ./
RUN python3 -m pip install -U -r requirements.txt

# copy server
COPY . .

ENV PYTHONUNBUFFERED=1
ENV C_FORCE_ROOT=False
ENV CELERYBEAT_SCHEDULE_FILENAME=/tmp/celerybeatschedule.db
ENV TZ=Europe/London

ENTRYPOINT ["honcho"]
CMD ["start"]
