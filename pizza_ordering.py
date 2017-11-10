""" Pizza Ordering System """
# IMPORT

import re
import sys
import time

# CONFIG
# cooking delay
COOKING_DELAY = 5

# maximum number of pizzas to order
MAX_PIZZAS = 5

# delivery charge in $
DELIVERY_CHARGE = 3.00
# delivery delay in minutes
DELIVERY_DELAY = 10

PIZZAS_AVAILABLE = (
    {"name": "Hawaiian",             "price": 8.5,  "time": 2},
    {"name": "Meat Lovers",          "price": 8.5,  "time": 2},
    {"name": "Pepperoni",            "price": 8.5,  "time": 2},
    {"name": "Ham & Cheese",         "price": 9.5,  "time": 3},
    {"name": "Classic Cheese",       "price": 9.5,  "time": 2},
    {"name": "Veg Hot 'n' Spicy",    "price": 9.5,  "time": 3},
    {"name": "Beef & Onion",         "price": 9.5,  "time": 3},
    {"name": "Seafood Deluxe",       "price": 13.5, "time": 4},
    {"name": "Summer Shrimp",        "price": 13.5, "time": 4},
    {"name": "BBQ Bacon & Mushroom", "price": 13.5, "time": 4},
    {"name": "BBQ Hawaiian",         "price": 13.5, "time": 4},
    {"name": "Italiano",             "price": 13.5, "time": 4},
)

def get_delay(order):
    """Compute the preparation (along with delivery, if any) delay"""
    delay = 0
    for pizza in order.pizzas:
        if delay < pizza["time"]:
            delay = pizza["time"]
    delay += COOKING_DELAY
    if not order.pickup:
        delay += DELIVERY_DELAY
    order.delay = delay

def print_order(order):
    """Prints the order details to the screen"""
    print_line("Name: " + order.name)
    print_line("Order date: {:10}".format(order.date))
    if order.pickup:
        print_line("Order type: {:10}Ready in: {:3} min (approx.)".format("Pickup", order.delay))
    else:
        print_line("Order type: {:10}Delivered in: {:3} min (approx.)".format("Delivery", order.delay))
        print_line("Delivery address: " + order.address)
        print_line("Customer phone number: " + order.phone)
    print_line("")
    print_line("Order summary:{:15}Price each:{:5}Subtotal:".format("", ""))
    for pizza in order.pizzas:
        print_line("{:5}x {:22}{:5}${:5.2f}{:8}${:>5.2f}".format(
            pizza["amount"], pizza["name"], "",
            pizza["price"], "", pizza["price"]*pizza["amount"]))
    if not order.pickup:
        print_line("{:4}Delivery charge{:29}${:>5.2f}".format(
            "", "", DELIVERY_CHARGE))

    print_line("{:48}------".format(""))
    print_line("{:40} Total: ${:.2f}".format("", order.cost))

def get_input(regex, input_message=None, error_message=None):
    """Gets valid input, validated using regular expressions."""
    # loops until input is valid ("break" is called)
    while True:
        # input to validate, input prompt is as specified
        if input_message:
            user_input = raw_input(str(input_message))
        else:
            user_input = raw_input()
        user_input = user_input.lower().strip()
        # check if the user wants to quit or cancel the order
        if user_input == "qq" or user_input == "quit":
            sys.exit()
        elif user_input == "cc" or user_input == "cancel":
            return "CANCEL"

        # check if the input matches the regex provided
        if re.match(regex, user_input, re.IGNORECASE):
            break

        # if it doesn't match, and an error message has been specified
        if error_message:
            print(str(error_message))

    return user_input

def print_line(line):
    """ Prints "| <message> |". Used for print_order()."""
    print("| {:54} |".format(line))

class Order():
    """Holds each order's information, can get the information itself."""
    def __init__(self):
        self.name = ""
        self.pickup = False
        self.address = None
        self.phone = None
        self.pizzas = []
        self.cost = 0
        self.date = None
        self.delay = 0
        self.isDelivered = False

    def get_pickup(self):
        user_input = get_input(
            r"$|(?:P|D)",
            "Pickup or delivery? [Pickup]:",
            "Please enter a 'p' (pickup) or a 'd' (delivery)")
        if user_input == "CANCEL":
            return "CANCEL"
        self.pickup = user_input.lower().startswith("p") or not user_input

    def get_name(self):
        user_input = get_input(
            r"[A-Z]+$",
            "Enter customer name:",
            "Name must only contain letters")
        if user_input == "CANCEL":
            return "CANCEL"
        self.name = user_input[:48]

    def get_address(self):
        user_input = get_input(
            r"[ -/\w]+$",
            "Delivery address:",
            "Address must only contain alphanumeric characters")
        if user_input == "CANCEL":
            return "CANCEL"
        self.address = user_input[:36]

    def get_phone(self):
        user_input = get_input(
            r"\d+$",
            "Phone number:",
            "Phone number must only contain numbers")
        if user_input == "CANCEL":
            return "CANCEL"
        self.phone = user_input[:11]

    def get_pizzas(self):
        # loop to get valid input, needs to be more specific than
        # just regex (needs to be greater than 0, less than 5)
        while True:
            user_input = get_input(
                r"\d$",
                "Number of pizzas to order:",
                "Must be a digit, 5 or less")
            if user_input == "CANCEL":
                return "CANCEL"

            if 0 < int(user_input) <= MAX_PIZZAS:
                number_pizzas = int(user_input)
                break
            else:
                print("Must be a digit, 5 or less (but more than 0)")

        print("\nWhat pizzas would you like to order?")
        for i, pizza in enumerate(PIZZAS_AVAILABLE):
            # each pizza's number is its index (i) + 1,
            # so the first pizza is 1
            print("{}: {} - {}".format(str(i+1).zfill(2), pizza["name"], str(pizza["price"])))

        print("\nEnter your selection number for each pizza you want to buy")
        for i in range(number_pizzas):
            # loop to get valid input
            while True:
                user_input = get_input(
                    r"\d\d?$",
                    "Pizza #{} of {}:".format(i+1, number_pizzas),
                    "Pizza selection number must "
                    "correspond to those listed above")
                if user_input == "CANCEL":
                    return "CANCEL"

                try:
                    # 0 is not a valid pizza number
                    if int(user_input) == 0:
                        raise IndexError
                    # selects the pizza based on user_input
                    # gives IndexError if not valid (e.g. 23 is not valid)
                    to_add = PIZZAS_AVAILABLE[int(user_input)-1]

                except IndexError:
                    print("Pizza selection number must "
                          "correspond to those listed above")

                # if there has been no error,
                else:
                    # input is valid, break from the while loop
                    break

            # if the pizza has already been ordered,
            # increment the amount ordered
            for ordered in self.pizzas:
                if to_add["name"] == ordered["name"]:
                    ordered["amount"] += 1
                    break
            # else add the pizza to the order list
            else:
                to_add["amount"] = 1
                order.pizzas.append(to_add)

    def get_cost(self):
        cost = sum(
            pizza["price"]*pizza["amount"]
            for pizza in self.pizzas)
        if not self.pickup:
            cost += DELIVERY_CHARGE
        self.cost = cost

    def get_details(self):
        if self.get_pickup() == "CANCEL":
            return "CANCEL"
        if self.get_name() == "CANCEL":
            return "CANCEL"
        if not self.pickup:
            if self.get_address() == "CANCEL":
                return "CANCEL"
            if self.get_phone() == "CANCEL":
                return "CANCEL"
        if self.get_pizzas() == "CANCEL":
            return "CANCEL"
        if self.get_cost() == "CANCEL":
            return "CANCEL"

if __name__ == "__main__":
    print(
        "  == Keio Pizzas ==\n"
        "==  Order Manager  ==\n"
        "Enter 'CC' to cancel order, or 'QQ' to exit program at any time.\n"
        "The first letter of a word is usually only required as input.\n"
        "A word [enclosed] in brackets is the default option.\n")

    # list to hold all completed orders
    orders = []

    # sorts pizza list by price, then alphabetically
    PIZZAS_AVAILABLE = sorted(
        PIZZAS_AVAILABLE,
        key=lambda k: (k["price"], k["name"]))

    # loop to get orders until told to quit (quits through sys.exit)
    while True:
        order = Order()
        if not order.get_details() == "CANCEL":
            order.date = time.strftime("%c")
            get_delay(order)
            print("\nOrder saved. Order was:")
            print_order(order)
            orders.append(order)
        else:
            print("\nOrder cancelled.")

        user_input = get_input(
            r"$|(?:Y|N|O).*",
            "Would you like to enter another order or view all "
            "previous orders? [Yes]/No/Orders:",
            "Only yes/no or \"orders\" responses allowed")
        if user_input.lower().startswith("n"):
            sys.exit()
        elif user_input.lower().startswith("o"):
            # print orders
            for i, order in enumerate(orders):
                # make nice box around orders, special title at top
                if i == 0:
                    print("-"*23 + " ALL ORDERS " + "-"*23)
                else:
                    print("|" + "-"*56 + "|")
                print_order(order)
                # if it is the last order, close the box
                if i == len(orders) - 1:
                    print("-" * 58)
