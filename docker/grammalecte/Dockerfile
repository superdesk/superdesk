FROM ubuntu:bionic

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -y

# we need grammalecte >= 1.2 and at time of creating this file last stable version is 1.1.1
# so we keep a 1.2 pre-release on our servers

RUN apt-get install -y --no-install-recommends locales python3 wget ca-certificates unzip &&\
    sed -i "s/# en_US.UTF-8/en_US.UTF-8/" /etc/locale.gen && locale-gen
ENV LC_ALL en_US.UTF-8

RUN mkdir /grammalecte
WORKDIR /grammalecte
RUN wget https://superdesk-test.s3-eu-west-1.amazonaws.com/sd-sdsite/Grammalecte-fr-v1.2.zip
RUN unzip Grammalecte-fr-v1.2.zip && rm -f Grammalecte-fr-v1.2.zip

EXPOSE 9999
CMD python3 grammalecte-server.py --host 0.0.0.0 --port 9999
