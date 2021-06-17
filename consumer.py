import json
from pprint import pprint 

from tour.event_handling import EventSubscriber

consumer = EventSubscriber("logistica_test")

def callback1(ch, method, properties, body):
    evento = json.loads(body)
    # switcher = {
    #     'tour_scrum_assistant_p1' : 'el hall',
    #     'tour_scrum_assistant_p2' : 'la sala planning',
    #     'tour_scrum_assistant_p3' : 'la oficina',
    #     'tour_scrum_assistant_p4' : 'el tablero',
    #     'tour_scrum_assistant_p5' : 'la sala de desarrollo',
    #     'tour_scrum_assistant_p6' : 'la sala de reuniones'
    # }
    # place = switcher.get(evento["location"])
    #print('Evento:' + str(evento) + ' (El bot se mueve hacia ' + place + ')')
    # pprint(ch)
    # pprint(method)
    # pprint(properties)
    # pprint(body)
    pprint(evento)
    

consumer.subscribe("movement_now", callback1)
consumer.start_listening()
