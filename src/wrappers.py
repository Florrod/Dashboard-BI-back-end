from utils import APIException
from models import Order, LineItem, Clients, Brand, Platform

class Wrapper():

    def __init__(self, integration):
        self.integration = integration,
    def wrap(self, json) -> Order:
        if self.integration.platform.id == 1:
            wrapper = WrapperJustEat(self.integration)
        elif self.integration.platform.id == 2:
            wrapper = WrapperGlovo(self.integration)
        else:
            raise APIException("Platform not supported")
        return wrapper.wrap(json)

class WrapperJustEat(Wrapper):

    def wrap(self, json) -> Order:
        ordersJson = json['orders']
        for orderJson in ordersJson:
            lineitems, total_price = wrapLineItemsAndCalcTotalPrice(orderJson['lines'])
            client = wrapClient(orderJson['client'])
            order = Order(
                total_price = total_price,
                lineitems = lineitems,
                client = wrapClient(orderJson['client']),
                platform_id = self.integration.platform.id,
                brand_id = self.integration.brand.id
            )
            return order
    
    def wrapLineItemsAndCalcTotalPrice(self, lineitemsJson):
        total_price = 0
        lineitems = []
        for lineitemJson in lineitemsJson:
            quantity = lineitemJson['quantity']
            total_price += (lineitemJson['price'] * quantity)
            lineitems.append(wrapLineItem(lineitemJson))
        return lineitems, total_price

    def wrapLineItem(self, lineitemJson) -> LineItem:
        return LineItem(
            product_name = lineitemJson['name'],
            quantity = lineitemJson['quantity'],
            price = lineitemJson['price']
        )

    def wrapClient(self,clientJson) -> Clients:
        client = Clients.getWithEmail(email=clientJson['email'])
        if client == None:
            client = Clients(
                email = clientJson['email'],
                orders_count = 1
            )
        else:
            client.orders_count += 1
        return client

class WrapperGlovo(Wrapper):

    def wrap(self,json) -> Order:
        for orderJson in json:

            lineitems = wrapLineItems(orderJson['lines'])
            total_price = orderJson['orderPrice']['amount']
            client = wrapClient(orderJson['addresses'])

            order = Order(
                total_price = total_price,
                lineitems = lineitems,
                client = client,
                platform_id = self.integration.platform.id,
                brand_id = self.integration.brand.id
            )

            return order
    
    def wrapLineItems(self,orderJson): #Para el producto más pedido
        lineitems = []
        lineitems.append(wrapLineItem(orderJson))
        return lineitems

    def wrapLineItem(self,orderJson) -> LineItem:
        return LineItem(
            product_name = orderJson['description'],
            quantity = orderJson['quantity'],
            price = orderJson['orderPrice']['amount'] / orderJson['quantity']
        )


    def wrapClient(self,addressesJson) -> Clients: #Para el cliente recurrente y nuevo

        for address in addressesJson:
            if address['type'] == "DELIVERY":
                phone= address['contactPhone']
        
                client = Clients.getWithPhone(phone=phone)
                if client == None:
                    client = Clients(
                        phone = phone,
                        orders_count = 1
                    )

                else:
                    client.orders_count += 1
        
                return client
        return None