from utils import APIException
from models import Order, LineItem, Clients, Brand, Platform, DatabaseManager 
from typing import List
from datetime import timedelta, datetime, tzinfo, timezone
import dateutil.parser

class Wrapper():

    def __init__(self, integration):
        self.integration = integration

    def wrap(self, json) -> Order:
        print(self.integration)
        if self.integration.platform_id == 1:
            wrapper = WrapperJustEat(self.integration)
        elif self.integration.platform_id == 2:
            wrapper = WrapperGlovo(self.integration)
        else:
            raise APIException("Platform not supported")
        return wrapper.wrap(json)

class WrapperGlovo(Wrapper):

    def wrap(self,json) -> List[Order]:
        orders = []
        for orderJson in json:

            lineitems = self.wrapLineItems(orderJson)
            # date=(orderJson['scheduleTime']) // 1000
            date = self.wrapDateGL(orderJson['scheduleTime'])
            total_price = (orderJson['orderPrice']['amount'])/100
            client = self.wrapClient(orderJson['addresses'])
            client.addToDbSession()

            order = Order(
                total_price = total_price,
                date = date,
                lineItems = lineitems,
                client = client,
                platform_id = self.integration.platform_id,
                brand_id = self.integration.brand_id,
                integration_id = self.integration.id
            )

            orders.append(order)
            # print("AAAAAAHHH ->", order)
        return orders
    
    def wrapLineItems(self,orderJson): #Para el producto más pedido
        lineitems = []
        lineitems.append(self.wrapLineItem(orderJson))
        return lineitems

    def wrapLineItem(self,orderJson) -> LineItem:
        return LineItem(
            product_name = orderJson['description'],
            quantity = orderJson['quantity'],
            price = (orderJson['orderPrice']['amount'] / orderJson['quantity'])/100
        )

    def wrapDateGL(self,a):
        timestamp= a
        # date= datetime.utcfromtimestamp(int(timestamp))
        date = datetime.fromtimestamp((timestamp)/1000, tz=timezone.utc)
        return date


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

    def wrap(self, json) -> List[Order]:
        orders = []
        for orderJson in json:

            lineitems = self.wrapLineItems(orderJson['Items'])
            total_price = orderJson['TotalPrice']
            date=self.wrapDateJE(orderJson['scheduleTime'])
            client = self.wrapClient(orderJson['Customer'])
            client.addToDbSession()

            order = Order(
                total_price = total_price,
                date = date,
                lineItems = lineitems,
                client = client,
                platform_id = self.integration.platform_id,
                brand_id = self.integration.brand_id,
                integration_id = self.integration.id
            )
            orders.append(order)
        return orders
         

    def wrapLineItems(self,itemsJson): #Para el producto más pedido
        lineitems = []
        for itemJson in itemsJson:
            lineitems.append(self.wrapLineItem(itemJson))
        return lineitems

    def wrapLineItem(self,itemJson) -> LineItem:
        return LineItem(
            product_name = itemJson['Name'],
            quantity = itemJson['Quantity'],
            price = itemJson['UnitPrice'] 
        )

    def wrapDateJE(self,b):
        dates = b
        date= dateutil.parser.parse(dates)
        # date.strftime('%y-%M-%d %h:%m')
        return date


    def wrapClient(self,customerJson) -> Clients: #Para el cliente recurrente y nuevo

        customer_id= customerJson['Id']

        client = Clients.getWithCustomerPlatformId(customer_platform_id=customer_id)
        if client == None:
            client = Clients(
                customer_id_platform = customer_id,
                orders_count = 1
            )

        else:
            client.orders_count += 1

        return client
    
