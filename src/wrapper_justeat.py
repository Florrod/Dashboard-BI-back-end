from models import Order, LineItem, Clients, Brand, Platform
from wrapper import Wrapper

class WrapperJustEat(Wrapper):

    def wrap(json) -> Order:
        ordersJson = json['orders']
        for orderJson in ordersJson:

            lineitems, total_price = wrapLineItemsAndCalcTotalPrice(orderJson['lines'])

            client = wrapClient(orderJson['client'])

            order = Order(
                total_price = total_price,
                lineitems = lineitems,
                client = wrapClient(orderJson['client']),
                platform_id = integration.platform.id,
                brand_id = integration.brand.id
            )

            return order
    
    def wrapLineItemsAndCalcTotalPrice(lineitemsJson):
        total_price = 0
        lineitems = []
        for lineitemJson in lineitemsJson:
            total_price += (lineitemJson['price'] * lineItemJson['quantity'])
            lineitems.append(wrapLineItem(lineitemJson))
        return lineitems, total_price

    def wrapLineItem(lineitemJson) -> LineItem:
        return LineItem(
            product_name = lineitemJson['name'],
            quantity = lineitemJson['quantity'],
            price = lineitemJson['price']
        )

    def wrapClient(clientJson) -> Clients:
        client = Clients.getWithEmail(email=clientJson['email'])
        if client == None:
            client = Clients(
                email = clientJson['email'],
                orders_count = 1
            )

        else:
            client.orders_count += 1

        return client




