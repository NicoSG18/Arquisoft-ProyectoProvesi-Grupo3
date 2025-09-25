
from rest_framework import serializers
from .models import Pedido, TransaccionBancaria


class TransaccionBancariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransaccionBancaria
        # Lista de campos del modelo que queremos mostrar.
        fields = ['id', 'monto', 'fecha_transaccion', 'banco_origen', 'validada']


class PedidoConTransaccionesSerializer(serializers.ModelSerializer):
    
    transacciones = TransaccionBancariaSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'codigo', 'estado', 'fecha_creacion', 'transacciones']