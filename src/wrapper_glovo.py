from models import Order, LineItem, Clients
from wrappers import Wrapper

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

    




