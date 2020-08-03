from utils import APIException
from models import Order, LineItem, Clients, Brand, Platform

class Wrapper():

    def __init__(self, integration):
        self.integration = integration,
    def wrap(self, json) -> Order:
        if self.integration.platform_id == 1:
            wrapper = WrapperJustEat(self.integration)
        elif self.integration.platform_id == 2:
            wrapper = WrapperGlovo(self.integration)
        else:
            raise APIException("Platform not supported")
        return wrapper.wrap(json)

class WrapperGlovo(Wrapper):

    def wrap(self,json) -> Order:
        for orderJson in json:

            lineitems = wrapLineItems(orderJson['lines'])
            total_price = orderJson['orderPrice']['amount']
            client = wrapClient(orderJson['addresses'])

            order = Order(
                total_price = total_price,
                lineItems = lineitems,
                client_id = client,
                platform_id = self.integration.platform_id,
                brand_id = self.integration.brand_id
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

class WrapperJustEat(Wrapper):

    def wrap(self, json) -> Order:
        for orderJson in json:

            lineitems = wrapLineItems(orderJson['lines'])
            total_price = orderJson['TotalPrice']
            client = wrapClient(orderJson['Customer']['Id'])

            order = Order(
                total_price = total_price,
                lineItems = lineitems,
                client_id = client,
                platform_id = self.integration.platform_id,
                brand_id = self.integration.brand_id
            )

            return order

            

    def wrapLineItems(self,orderJson): #Para el producto más pedido
        lineitems = []
        lineitems.append(wrapLineItem(orderJson))
        return lineitems

    def wrapLineItem(self,orderJson) -> LineItem:
        for lineItems in orderJson:
            return LineItem(
                product_name = orderJson['Items']['Name'],
                quantity = orderJson['Items']['Quantity'],
                price = orderJson['Items']['UnitPrice'] 
            )

    def wrapClient(self,customerJson) -> Clients: #Para el cliente recurrente y nuevo

        customer_id= ['Customer']['Id']

        client = Clients.getWithCustomerId(customer_id=customer_id)
        if client == None:
            client = Clients(
                customer_id_justeat = customer_id,
                orders_count = 1
            )

        else:
            client.orders_count += 1

        return client
        
    return None

