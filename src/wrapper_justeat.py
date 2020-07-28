from models import Order, LineItem, Clients, Brand, Platform, DatabaseManager, Integration

class WrapperJustEat():
    def __init__(platform):
        self.platform=platform
        # ¿Esto por qué? si en realidad estamos creando un wrapper para cada API

    @staticmethod
    def translateAndSave(json):
        ordersJson = json["orders"]
        for orderJson in ordersJson:
            total_price=0

            lineitemsJson= orderJson["lines"]
            lineitems = []
            for lineitemJson in lineitemsJson:
                total_price += (lineitemJson["price"] * lineitemJson["quantity"])
                lineitem = LineItem(
                    product_name= lineitemJson["name"],
                    quantity= lineitemJson["quantity"],
                    price=lineitemJson["price"]
                )

            order = Order (
                total_price = total_price,
            )
                #revisar codigo de arriba
                
                #Esto sirve para contabilizar si los clientes son nuevos o recurrentes mediante el correo. QUIZÁ HAY QUE CAMBIARLO POR OTRO IDENTIFICADOR ¿TELÉFONO?
            client = Clients.getWithEmail(email=orderJson["client"]["email"]) #usar otro identificador para el cliente , telefono o nombre
            if client == None:
                client = Clients(
                    email=orderJson["client"]["email"],
                    orders_count=1
                )
            else:
                client.orders_count += 1
            
            client.save()
            order.platform_id = Platform.query.all()[0].id
            order.brand_id = Brand.query.all()[0].id
            order.integration_id = Integration.query.all()[0].id
            #Necesitamos saber cual es el Platform y el Brand -> desde el main
            order.client_id = client.id
            
            order.save()

            for lineitem in lineitems:
                order.lineitems.append(lineitem)
            
            DatabaseManager.commit()








