FROM rasa/rasa:2.0.0rc2

ENTRYPOINT []
RUN apt-get update && apt-get install -y python3 python3-pip && python3 -m pip install --no-cache --upgrade pip && pip3 install --no-cache rasa==2.4.3
ADD . /app/
RUN chmod +x /app/start_services.sh
CMD /app/start_services.sh