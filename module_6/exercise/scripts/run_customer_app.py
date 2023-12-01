#!/usr/bin/env python
import sys
import os

sys.path.append("../")

import argparse
from db_and_event_definitions import CUSTOMERS_DATABASE
from customer_app import CustomerEventConsumer


def main():
    parser = argparse.ArgumentParser(description="Run customer app")
    parser.add_argument(
        "--customer_id", "-c", type=str, choices=CUSTOMERS_DATABASE, help="Customer ID"
    )
    args = parser.parse_args()

    customer_app = CustomerEventConsumer(customer_id=args.customer_id)
    customer_app.initialize_rabbitmq()
    print(
        " [*] Customer App with ID = {} waiting for CustomerEvents. \
		To exit press CTRL+C".format(
            customer_app.customer_id
        )
    )
    customer_app.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
