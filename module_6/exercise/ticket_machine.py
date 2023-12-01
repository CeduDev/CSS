import json

import pika

from xprint import xprint


class TicketEventProducer:
    def __init__(self):
        # Do not edit the init method.
        # Set the variables appropriately in the methods below.
        self.connection = None
        self.channel = None
        self.exchange = "ticket_events_exchange"
        self.routing_key = "ticket_event"

    def initialize_rabbitmq(self):
        xprint("TicketEventProducer initialize_rabbitmq() called")

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost")
        )
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange, exchange_type="direct")

    def publish_ticket_event(self, ticket_event):
        xprint(
            "TicketEventProducer: Publishing ticket event {}".format(vars(ticket_event))
        )
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.routing_key,
            body=json.dumps(vars(ticket_event)),
        )

    def close(self):
        # Do not edit this method
        self.channel.close()
        self.connection.close()
