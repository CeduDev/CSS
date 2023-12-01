from types import SimpleNamespace
import pika
import json
from db_and_event_definitions import CustomerEvent
import time
import logging

from xprint import xprint


class CustomerEventConsumer:
    def __init__(self, customer_id):
        # Do not edit the init method.
        # Set the variables appropriately in the methods below.
        self.customer_id = customer_id
        self.connection = None
        self.channel = None
        self.temporary_queue_name = None
        self.customer_events = []
        self.customer_events_exchange = "customer_events_exchange"

    def initialize_rabbitmq(self):
        xprint(
            "CustomerEventConsumer {}: initialize_rabbitmq() called".format(
                self.customer_id
            )
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost")
        )
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=self.customer_events_exchange, exchange_type="topic"
        )

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.temporary_queue_name = result.method.queue
        self.channel.queue_bind(
            exchange=self.customer_events_exchange,
            queue=self.temporary_queue_name,
            routing_key=self.customer_id,
        )

    def handle_event(self, ch, method, properties, body):
        xprint(
            "CustomerEventConsumer {}: handle_event() called".format(self.customer_id)
        )
        customer_event = json.loads(body)

        ce = CustomerEvent(
            customer_id=customer_event["customer_id"],
            ride_number=customer_event["ride_number"],
            cost=customer_event["cost"],
            purchase_time=customer_event["purchase_time"],
        )

        self.customer_events.append(ce)

    def start_consuming(self):
        xprint(
            "CustomerEventConsumer {}: start_consuming() called".format(
                self.customer_id
            )
        )

        self.channel.basic_consume(
            queue=self.temporary_queue_name,
            on_message_callback=self.handle_event,
            auto_ack=True,
        )
        self.channel.start_consuming()

    def close(self):
        # Do not edit this method
        try:
            if self.channel is not None:
                xprint("CustomerEventConsumer {}: Closing".format(self.customer_id))
                self.channel.stop_consuming()
                time.sleep(1)
                self.channel.close()
            if self.connection is not None:
                self.connection.close()
        except Exception as e:
            xprint(
                "CustomerEventConsumer {}: Exception {} on close()".format(
                    self.customer_id, e
                )
            )
            pass
