


class Order():
    """Holds each order's information, can get the information itself."""
    def __init__(self):
        # Order information
        self.ID = 0
        self.date = None
        self.now = True
        self.total_delay = 0
        self.total_cost = 0.0
        # Delivery information
        self.name = ""
        self.delivery_address = None
        self.delivery_cost = 0
        self.delivery_discount = 0.0
        self.phone = None
        self.message = ""
        self.delivery_date = None
        self.delay = 0
        self.sharing_span = 0 # 0 = no sharing
        self.pickup = False
        self.isDelivered = False
        # Items information
        self.items = []
        self.preparation_time = 0
        self.max_keep_time = 0
        self.items_cost = 0.0

    def set_items(self, number_items, items_selection, source_list):
        for i in range(number_items):
            to_add = source_list[int(items_selection[i])-1]
            # if the pizza has already been ordered,
            # increment the amount ordered
            for ordered in self.items:
                if to_add["name"] == ordered["name"]:
                    ordered["amount"] += 1
                    break
            # else add the pizza to the order list
            else:
                to_add["amount"] = 1
                self.items.append(to_add)

    def compute_preparation_delay(self, cooking_delay):
        """Compute the preparation (make + cook) delay"""
        delay = 0
        for item in self.items:
            if delay < item["time"]:
                delay = item["time"]
        delay += cooking_delay
        self.preparation_time = delay

    def compute_order_full_delay(self, cooking_delay):
        """Compute the preparation (along with delivery, if any) delay"""
        delay = 0
        self.compute_preparation_delay(cooking_delay)
        delay += self.preparation_time
        if not self.pickup:
            delay += self.delay
        self.total_delay = delay

    def compute_items_cost(self):
        cost = sum(
            item["price"]*item["amount"]
            for item in self.items)
        self.items_cost = cost

    def compute_delivery_cost(self, delivery_charge, discount_level):
        self.delivery_cost = delivery_charge
        if self.sharing_span != 0:
            self.delivery_discount = delivery_charge*float(self.sharing_span)*discount_level/100

    def compute_order_full_cost(self, delivery_charge, discount_level):
        self.compute_items_cost()
        if not self.pickup:
            self.compute_delivery_cost(delivery_charge, discount_level)
        self.total_cost = self.items_cost + self.delivery_cost - self.delivery_discount
