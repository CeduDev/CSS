from concurrent import futures
import grpc
import sys
from proto import restaurant_pb2
from proto import restaurant_pb2_grpc

RESTAURANT_ITEMS_FOOD = ["chips", "fish", "burger", "pizza", "pasta", "salad"]
RESTAURANT_ITEMS_DRINK = ["water", "fizzy drink", "juice", "smoothie", "coffee", "beer"]
RESTAURANT_ITEMS_DESSERT = [
    "ice cream",
    "chocolate cake",
    "cheese cake",
    "brownie",
    "pancakes",
    "waffles",
]


class Restaurant(restaurant_pb2_grpc.RestaurantServicer):
    def FoodOrder(self, request, context):
        return self.process_order(request, RESTAURANT_ITEMS_FOOD)

    def DrinkOrder(self, request, context):
        return self.process_order(request, RESTAURANT_ITEMS_DRINK)

    def DessertOrder(self, request, context):
        return self.process_order(request, RESTAURANT_ITEMS_DESSERT)

    def MealOrder(self, request, context):
        meal_items = [
            RESTAURANT_ITEMS_FOOD,
            RESTAURANT_ITEMS_DRINK,
            RESTAURANT_ITEMS_DESSERT,
        ]

        if len(request.items) != 3:
            return self.create_response(
                request.orderID,
                restaurant_pb2.RestaurantResponse.REJECTED,
                request.items,
            )

        for i in range(3):
            if request.items[i] not in meal_items[i]:
                return self.create_response(
                    request.orderID,
                    restaurant_pb2.RestaurantResponse.REJECTED,
                    request.items,
                )

        return self.create_response(
            request.orderID, restaurant_pb2.RestaurantResponse.ACCEPTED, request.items
        )

    def process_order(self, request, menu):
        invalid_items = [item for item in request.items if item not in menu]

        if invalid_items:
            return self.create_response(
                request.orderID,
                restaurant_pb2.RestaurantResponse.REJECTED,
                request.items,
            )
        else:
            return self.create_response(
                request.orderID,
                restaurant_pb2.RestaurantResponse.ACCEPTED,
                request.items,
            )

    def create_response(self, orderID, status, items):
        response = restaurant_pb2.RestaurantResponse()
        response.orderID = orderID
        response.status = status
        response.itemMessage.extend(
            [restaurant_pb2.items(itemName=item) for item in items]
        )
        return response


def serve():
    if len(sys.argv) < 2:
        print("Specify port! Usage: python restaurant_server.py <port>")
        sys.exit(1)

    port = sys.argv[1]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    restaurant_pb2_grpc.add_RestaurantServicer_to_server(Restaurant(), server)
    server.add_insecure_port(f"localhost:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
