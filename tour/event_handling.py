import json
from typing import Dict, Callable

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties


class EventSubscriber:
    """Clase para subscribirse a eventos en un servidor y exchange determinado.

    La documentacion de RabbitMQ recomienda separar la conexion de publicaciones
    de la de subscripciones. Tambien recomienda un canal por thread.

    Autor: Bruno.
    """

    def __init__(self, exchange_name: str, host: str = "amqps://qacbbkir:SaSlHJKAr16CFWuaeIoKg4ZGeYCE5E2h@clam.rmq.cloudamqp.com/qacbbkir"):
    # def __init__(self, exchange_name: str, host: str = "localhost"):
        """Constructor.
        Crea una conexion al servidor de eventos solo para subscripciones.

        Autor: Bruno.

        :param exchange_name: nombre del exchange donde se publican los eventos.
        :param host: host donde esta corriendo el servidor de eventos.
        """
        self._exchange_name = exchange_name
        self._exchange_type = "topic"

        # Crea conexion y canal para subscripciones.
        self._subscribe_connection = pika.BlockingConnection(
            pika.URLParameters(host))
            # pika.ConnectionParameters(host))
        self._subscribe_channel = self._subscribe_connection.channel()
        # Crea el exchange (si no existe).
        self._subscribe_channel.exchange_declare(
            # TODO Si salta una excepcion de pika poner en True.
            durable=True,
            exchange=self._exchange_name, exchange_type=self._exchange_type)

    def subscribe(
            self,
            event: str,
            callback: Callable[
                [BlockingChannel, Basic.Deliver, BasicProperties, bytes], None]
    ) -> None:
        """Realiza una subscripcion al evento dado.

        Autor: Bruno.

        :param event: Evento al que se realiza la subscripcion.
        :param callback: Funcion a ejecutar cuando se captura el evento.
        :return: None
        """
        # Crea la cola. Cuando la conexion del consumidor se cierra, la cola
        # se elimina.
        result = self._subscribe_channel.queue_declare(queue='', exclusive=True)

        # Vincula la cola al exchange, con el evento dado.
        self._subscribe_channel.queue_bind(exchange=self._exchange_name,
                                           queue=result.method.queue,
                                           routing_key=event)
        # Hace la subscripcion al evento.
        self._subscribe_channel.basic_consume(queue=result.method.queue,
                                              on_message_callback=callback,
                                              auto_ack=True)

    def start_listening(self) -> None:
        """Comienza a escuchar los eventos a los que esta subscripto.

        Autor: Bruno.

        :return: None.
        """
        self._subscribe_channel.start_consuming()

    def close_connections(self) -> None:
        """Cierra el canal y la conexion realizada en el servidor de eventos.

        Autor: Bruno.

        :return: None.
        """
        self._subscribe_channel.close()
        self._subscribe_connection.close()


class EventPublisher:
    """Clase para publicar eventos en un servidor y exchange determinado.

    La documentacion de RabbitMQ recomienda separar la conexion de publicaciones
    de la de subscripciones. Tambien recomienda un canal por thread.

    Autor: Bruno.
    """
    def __init__(self, exchange_name: str, host: str = "amqps://qacbbkir:SaSlHJKAr16CFWuaeIoKg4ZGeYCE5E2h@clam.rmq.cloudamqp.com/qacbbkir"):
    # def __init__(self, exchange_name: str, host: str = "localhost"):
        """Constructor.
        Crea una conexion al servidor de eventos solo para publicaciones.

        Autor: Bruno.

        :param exchange_name: nombre del exchange donde se publican los eventos.
        :param host: host donde esta corriendo el servidor de eventos.
        """
        self._exchange_name = exchange_name
        self._exchange_type = "topic"

        # Crea conexion y canal para publicaciones.
        self._publish_connection = pika.BlockingConnection(
            pika.URLParameters(host))
            # pika.ConnectionParameters(host))
        self._publish_channel = self._publish_connection.channel()
        # Crea el exchange (si no existe).
        self._publish_channel.exchange_declare(
            # TODO Si salta una excepcion de pika poner en True.
            durable=True,
            exchange=self._exchange_name, exchange_type=self._exchange_type)

    def publish(self, event: str, payload: Dict) -> None:
        """Publica el evento dado en el exchange, junto con un diccionario
        que almacena su informacion.

        Autor: Bruno.

        :param event: evento a publicar.
        :param payload: diccionario con datos del evento.
        :return: None.
        """
        self._publish_channel.basic_publish(
            self._exchange_name, routing_key=event, body=json.dumps(payload))

    def close_connections(self) -> None:
        """Cierra el canal y la conexion realizada en el servidor de eventos.

        Autor: Bruno.

        :return: None.
        """
        self._publish_channel.close()
        self._publish_connection.close()