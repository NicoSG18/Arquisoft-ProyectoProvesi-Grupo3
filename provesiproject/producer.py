#!/usr/bin/env python
import time
import pika
import random 

rabbit_host = 'host'
rabbit_user = 'monitoring_user'
rabbit_password = 'isis2503'
exchange = 'monitoring_transactions'
topic = 'Pagos.Aprobado'

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=rabbit_host,
        credentials=pika.PlainCredentials(rabbit_user, rabbit_password)
    )
)
channel = connection.channel()

channel.exchange_declare(exchange=exchange, exchange_type='topic')

print('> Sending measurements. To exit press CTRL+C')

trans = 1
bancos = ['Nequi','BancoDeBogota','Bancolombia','Itau','BBVA','Colpatria','Nu']

while True:
    trans_id = random.randint(10000, 99999)
    banco = random.choice(bancos)   
    money = f"${random.randint(10000, 1000000)}"
    
    payload = f"Transaccion #{trans} - Pedido PED-TEST-{trans_id} ({banco}) Monto: {money}"
    
    channel.basic_publish(exchange=exchange,
                          routing_key=topic, body=payload)
    
    print(f"Transaccion {trans_id} aprobada")
    
    trans += 1
    time.sleep(10)

connection.close()