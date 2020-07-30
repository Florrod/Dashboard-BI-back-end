from models import Order, LineItem, Clients, Brand, Platform
from wrapper import Wrapper

class WrapperGlovo(Wrapper):

    def wrap(json) -> Order:
        for orderJson in json:

            lineitems = wrapLineItems(orderJson['lines'])
            total_price = orderJson['orderPrice']['amount']
            client = wrapClient(orderJson['addresses'])

            order = Order(
                total_price = total_price,
                lineitems = lineitems,
                client = client,
                platform_id = integration.platform.id,
                brand_id = integration.brand.id
            )

            return order
    
    def wrapLineItems(orderJson): #Para el producto más pedido
        lineitems = []
        lineitems.append(wrapLineItem(orderJson))
        return lineitems

    def wrapLineItem(orderJson) -> LineItem:
        return LineItem(
            product_name = orderJson['description'],
            quantity = orderJson['quantity'],
            price = orderJson['orderPrice']['amount'] / orderJson['quantity']
        )


    def wrapClient(addressesJson) -> Clients:

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

    


{
    "id": 1568879245,
    "state": "DELIVERED",
    "scheduleTime": 1568879245000,
    "description": "Pollito frito",
    "quantity": 2,
    
    "addresses": [
    
      {
        "contactPhone": "+34622334455",
      }
    ],
    "orderPrice": {
      "amount": 2380,
    },
    "total": {
      "amount": 590,
    }
  },




