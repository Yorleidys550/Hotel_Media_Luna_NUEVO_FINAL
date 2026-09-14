# Hotel Media Luna — Proyecto nuevo

Proyecto web prototipo funcional para el Sistema de Gestión Hotelera de Hotel Media Luna, construido en Python + Flask con una interfaz moderna y responsive.

## Alcance implementado

- Área pública independiente, sin login, para reservas online.
- Área privada con autenticación y roles: Administrador, Recepcionista y Personal de limpieza.
- Dashboard adaptado al rol.
- Clientes: registrar, consultar, ver y crear reserva.
- Habitaciones: tipos, precios, capacidad, características y estados.
- Reservas por Internet y por llamada; una reserva puede incluir varias habitaciones.
- Hospedajes: check-in, asignación, estado activo y check-out.
- Aseo: tareas, prioridades, notificaciones/estado, iniciar y completar.
- Inventario: entradas, consumo, pérdidas/daños, mínimos y alertas.
- Equipaje: estado, daño observado y observaciones.
- Facturación: conceptos, cantidades, precios y total; preparado para integración electrónica.
- Llamadas: registro de información, sin contestación automática.
- Empleados y distribución de tareas.
- Administración y matriz de permisos.
- Auditoría de acciones.
- Diseño responsive y navegación consistente.

## Precios configurados

- Sencilla: $120.000 / noche
- Pareja: $200.000 / noche
- Familiar: $350.000 / noche
- Presidencial: $300.000 / noche — incluye jacuzzi

Las características se pueden editar en `app.py`.

## Ejecutar en Windows

```powershell
cd C:\ruta\Hotel_Media_Luna_NUEVO
python -m pip install -r requirements.txt
python app.py
```

Abrir:

- Área pública principal: `http://127.0.0.1:8000/`
- Área pública alternativa: `http://127.0.0.1:8000/publico`
- Acceso privado de empleados: `http://127.0.0.1:8000/login`

## Credenciales de demo

- Administrador: `medialuna` / `Medialuna2026`
- Recepcionista: `recepcionista01` / `Recepcion2026`
- Limpieza: `aseo01` / `Aseo2026`

## Nota de arquitectura

El documento exige Python o Java, patrón MVC y MySQL con procedimientos almacenados y triggers. Este entregable implementa la interfaz y un backend Flask de demostración con datos en memoria para poder probar todos los flujos sin configurar MySQL. `database/schema.sql` deja preparada la estructura MySQL, procedimiento y triggers para la fase de persistencia real.

La facturación electrónica se deja preparada en interfaz, pero la conexión real con un proveedor tecnológico y las obligaciones aplicables en Colombia requieren una implementación backend específica.
