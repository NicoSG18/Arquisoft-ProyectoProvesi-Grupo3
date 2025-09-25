# provesi_app/models.py
from django.db import models
from django.contrib.auth.models import User

# ---------------------------------------------------------------------------
# Modelo para gestionar las Bodegas
# El enunciado menciona que la empresa planea abrir bodegas en otras ciudades.
# ---------------------------------------------------------------------------
class Bodega(models.Model):
    nombre = models.CharField(max_length=150, help_text="Ej: Bodega Principal Cúcuta")
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

# ---------------------------------------------------------------------------
# Modelo para la Ubicación física de un producto dentro de una Bodega
# Esto es clave para resolver problemas de inventario extraviado y desorden[cite: 51, 52].
# Corresponde al proceso de "desenglobe"[cite: 62].
# ---------------------------------------------------------------------------
class Ubicacion(models.Model):
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name='ubicaciones')
    estante = models.CharField(max_length=50)
    fila = models.CharField(max_length=50)
    columna = models.CharField(max_length=50)
    
    class Meta:
        unique_together = ('bodega', 'estante', 'fila', 'columna') # No puede haber dos ubicaciones idénticas

    def __str__(self):
        return f"{self.bodega.nombre} - Estante {self.estante}, Fila {self.fila}, Columna {self.columna}"

# ---------------------------------------------------------------------------
# Modelo para los Productos
# ---------------------------------------------------------------------------
class Producto(models.Model):
    sku = models.CharField(max_length=100, unique=True, help_text="Identificador único del producto")
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    # Un producto puede estar en una ubicación específica. Si es null, no está asignado.
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.sku})"

# ---------------------------------------------------------------------------
# Modelo para extender el Usuario de Django y asignarle roles
# El sistema necesita roles para sus colaboradores.
# ---------------------------------------------------------------------------
class Colaborador(models.Model):
    ROLES = [
        ('vendedor', 'Vendedor'),
        ('operario_bodega', 'Operario de Bodega'),
        ('verificador', 'Verificador'),
        ('admin', 'Administrador'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='colaborador')
    rol = models.CharField(max_length=50, choices=ROLES)

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"

# ---------------------------------------------------------------------------
# Modelo de Pedido, la entidad central del WMS
# ---------------------------------------------------------------------------
class Pedido(models.Model):
    # Los estados se basan directamente en el flujo descrito en el documento[cite: 48].
    ESTADOS = [
        ('transito', 'Tránsito'),
        ('alistamiento', 'Alistamiento'),
        ('por_verificar', 'Por Verificar'),
        ('rechazado_x_verificar', 'Rechazado x Verificar'),
        ('verificado', 'Verificado'),
        ('empacado_x_despachar', 'Empacado x Despachar'),
        ('despachado_x_facturar', 'Despachado x Facturar'),
        ('despachado', 'Despachado'),
        ('entregado', 'Entregado'),
        ('devuelto', 'Devuelto'),
        ('anulado', 'Anulado'),
    ]
    
    codigo = models.CharField(max_length=100, unique=True)
    estado = models.CharField(max_length=50, choices=ESTADOS, default='transito')
    # Usamos el modelo Colaborador para saber quién está a cargo
    colaborador_asignado = models.ForeignKey(Colaborador, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # Aquí irían otros campos como la información del cliente, dirección de envío, etc.

    def __str__(self):
        return f"Pedido {self.codigo} - {self.get_estado_display()}"

# ---------------------------------------------------------------------------
# Modelo para los items dentro de un pedido
# ---------------------------------------------------------------------------
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT) # Proteger el producto si está en un pedido
    cantidad = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ('pedido', 'producto') # No se puede añadir el mismo producto dos veces al mismo pedido

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Pedido {self.pedido.codigo}"

# ---------------------------------------------------------------------------
# Modelo de Transacción, CRUCIAL para tu ASR de latencia
# Necesario para el paso donde se debe verificar el pago del cliente[cite: 24, 25].
# ---------------------------------------------------------------------------
class TransaccionBancaria(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='transacciones', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_transaccion = models.DateTimeField()
    banco_origen = models.CharField(max_length=100)
    url_comprobante = models.URLField(blank=True, null=True)
    validada = models.BooleanField(default=False)
    # Quién validó la transacción
    validada_por = models.ForeignKey(Colaborador, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_validacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Transacción de ${self.monto} para Pedido {self.pedido.codigo}"