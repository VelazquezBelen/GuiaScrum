import json

from tour.event_handling import EventSubscriber

consumer = EventSubscriber("log_eventos")

def callback1(ch, method, properties, body):
    d = json.loads(body)
    print(d)

consumer.subscribe("movement", callback1)
consumer.start_listening()
