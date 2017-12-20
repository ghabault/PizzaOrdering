import time
import re
import requests
from flask import Flask, render_template, request, redirect, url_for, abort, session, Markup

app = Flask(__name__)
app.config['SECRET_KEY'] = 'F34TF$($e34D';

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

def get_delay(delivery_addr):
    """Send the customer information to the Delivery Management System, and receive delay"""
    delivery_delay = 0
    webpath = "https://automatic-vehicle.herokuapp.com/order_management.php?origin=Hiyoshi"
    #webpath += shopaddr
    webpath += "&destination="
    webpath += delivery_addr
    #print webpath
    websource = requests.get(webpath, auth=('yamanaka', 'yamanaka'))
    #print websource.text
    data = str(websource.text)
    #delivery_delay = filter(str.isdigit, data)
    delivery_delay = re.findall('\d+', data)
    return int(delivery_delay[0])

def compute_delay(order):
    """Compute the preparation (along with delivery, if any) delay"""
    delay = 0
    for pizza in order.pizzas:
        if delay < pizza["time"]:
            delay = pizza["time"]
    delay += COOKING_DELAY
    if not order.pickup:
        delay += order.delay
    order.total_delay = delay

def compute_cost(order):
    cost = sum(
        pizza["price"]*pizza["amount"]
        for pizza in order.pizzas)
    if not order.pickup:
        cost += DELIVERY_CHARGE
    order.cost = cost

def format_table_row(l_num, l_sym, l_text, c_num, c_sym, c_text, r_num, r_sym, r_text):
    row = """
        <tr>
            <td> {}{}{} </td>
            <td> {}{}{} </td>
            <td> {}{}{} </td>
        </tr>
    """.format(l_num, l_sym, l_text, c_num, c_sym, c_text, r_num, r_sym, r_text)

    return row


class Order():
    """Holds each order's information, can get the information itself."""
    def __init__(self):
        self.ID = 0
        self.name = ""
        self.pickup = False
        self.address = None
        self.phone = None
        self.pizzas = []
        self.cost = 0
        self.date = None
        self.delay = 0
        self.total_delay = 0
        self.isDelivered = False

    def set_pizzas(self, number_pizzas, pizza_list):
        for i in range(number_pizzas):
            to_add = PIZZAS_AVAILABLE[int(pizza_list[i])-1]
            # if the pizza has already been ordered,
            # increment the amount ordered
            for ordered in self.pizzas:
                if to_add["name"] == ordered["name"]:
                    ordered["amount"] += 1
                    break
            # else add the pizza to the order list
            else:
                to_add["amount"] = 1
                self.pizzas.append(to_add)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    session['customer_name'] = request.form['customer_name']
    session['customer_phone'] = request.form['customer_phone']
    session['delivery_addr'] = request.form['delivery_addr']
    session['nb_pizza'] = request.form['nb_pizza']
    session['message'] = request.form['message']
    if session['delivery_addr']:
        session['delivery_delay'] = get_delay(session['delivery_addr'])
        #print session['delivery_delay']
    return redirect(url_for('order_page'))

@app.route('/order')
def order_page():
    menu = """
    """
    menu += format_table_row("", "", "<strong>Number</strong>", "", "", "<strong>Name</strong>", "", "", "<strong>Price</strong>")
    for i, pizza in enumerate(PIZZAS_AVAILABLE):
        # each pizza's number is its index (i) + 1,
        # so the first pizza is 1
        menu += format_table_row("", "#", str(i+1).zfill(2), "", "", pizza["name"], "", "$ ", str(pizza["price"]))
    menu = Markup(menu)
    return render_template('order.html', menu=menu)


@app.route('/message', methods=['POST'])
def message():
    session['customer_selection'] = request.form['customer_selection']
    if not 'customer_name' in session:
        return abort(403)
    order = Order()
    order.name = session['customer_name']
    if session['delivery_addr']:
        order.pickup = False
        order.delay = session['delivery_delay']
    else:
        order.pickup = True
    order.address = session['delivery_addr']
    order.phone = session['customer_phone']
    pizza_list = session['customer_selection'].strip().split(",")
    # print pizza_list
    order.set_pizzas(int(session['nb_pizza']), pizza_list)
    compute_cost(order)
    compute_delay(order)
    order.date = time.strftime("%c")
    # orders.append(order)

    bill = """
    """
    bill += format_table_row("", "", "<strong>Order summary:</strong>", "", "", "<strong>Price each:</strong>", "", "", "<strong>Subtotal:</strong>")
    for pizza in order.pizzas:
        bill += format_table_row(pizza["amount"], "x", pizza["name"], "", "$ ", pizza["price"], "", "$ ", pizza["price"]*pizza["amount"])

    if not order.pickup:
        bill += format_table_row("", "", "Delivery charge", "", "", "", "", "$ ", DELIVERY_CHARGE)

    # print the line before total
    bill += format_table_row("", "", "", "", "", "", "", "", "----------")

    # print the total of the order
    bill += format_table_row("", "", "", "", "", "<strong>Total:</strong>", "", "<strong>$ </strong>", order.cost)

    bill = Markup(bill)

    if order.pickup:
        delay_msg = "Ready in: {:3} min (approx.)".format(order.total_delay)
        return render_template('message.html', name=order.name,
                                               date=order.date,
                                               type="Pickup",
                                               delay_msg=delay_msg,
                                               bill=bill,
                                               phone=session['customer_phone'],
                                               message=session['message'])
    else:
        delay_msg = "Delivered in: {:3} min (approx.)".format(order.total_delay)
        addr_msg = "Delivery address: " + session['delivery_addr']
        return render_template('message.html', name=order.name,
                                               date=order.date,
                                               type="Delivery",
                                               delay_msg=delay_msg,
                                               addr=addr_msg,
                                               bill=bill,
                                               phone=session['customer_phone'],
                                               message=session['message'])


if __name__ == '__main__':
    PIZZAS_AVAILABLE = sorted(
        PIZZAS_AVAILABLE,
        key=lambda k: (k["price"], k["name"]))

    orders = []
    completed_orders = []

    app.run()