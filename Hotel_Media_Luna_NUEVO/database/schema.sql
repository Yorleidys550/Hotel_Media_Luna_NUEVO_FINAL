-- Hotel Media Luna · Base MySQL de referencia
CREATE DATABASE IF NOT EXISTS media_luna CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE media_luna;
CREATE TABLE usuarios(id INT AUTO_INCREMENT PRIMARY KEY, usuario VARCHAR(60) UNIQUE NOT NULL, password_hash VARCHAR(255) NOT NULL, rol VARCHAR(40) NOT NULL, activo TINYINT(1) DEFAULT 1);
CREATE TABLE clientes(id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(120) NOT NULL, documento VARCHAR(40) UNIQUE NOT NULL, nacionalidad VARCHAR(80), telefono VARCHAR(30), email VARCHAR(120));
CREATE TABLE habitaciones(id INT AUTO_INCREMENT PRIMARY KEY, numero VARCHAR(10) UNIQUE NOT NULL, tipo ENUM('Sencilla','Pareja','Familiar','Presidencial') NOT NULL, precio DECIMAL(12,2) NOT NULL, capacidad INT NOT NULL, estado ENUM('DISPONIBLE','OCUPADA','EN PROCESO DE ASEO','RESERVADA','SUSPENDIDA','EN PROCESO DE FACTURACIÓN') NOT NULL DEFAULT 'DISPONIBLE');
CREATE TABLE reservas(id INT AUTO_INCREMENT PRIMARY KEY, codigo VARCHAR(30) UNIQUE NOT NULL, cliente_id INT NOT NULL, entrada DATE NOT NULL, salida DATE NOT NULL, origen ENUM('Internet','Llamada') NOT NULL, estado VARCHAR(40) NOT NULL DEFAULT 'Pendiente', huespedes INT NOT NULL, FOREIGN KEY(cliente_id) REFERENCES clientes(id));
CREATE TABLE reserva_habitaciones(reserva_id INT NOT NULL, habitacion_id INT NOT NULL, PRIMARY KEY(reserva_id,habitacion_id), FOREIGN KEY(reserva_id) REFERENCES reservas(id), FOREIGN KEY(habitacion_id) REFERENCES habitaciones(id));
CREATE TABLE hospedajes(id INT AUTO_INCREMENT PRIMARY KEY, reserva_id INT NOT NULL, checkin DATETIME, checkout DATETIME, estado VARCHAR(30), FOREIGN KEY(reserva_id) REFERENCES reservas(id));
CREATE TABLE empleados(id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(120), rol VARCHAR(60), estado VARCHAR(30));
CREATE TABLE tareas_limpieza(id INT AUTO_INCREMENT PRIMARY KEY, habitacion_id INT NOT NULL, empleado_id INT, tarea VARCHAR(120), prioridad VARCHAR(20), estado VARCHAR(30), observaciones TEXT, FOREIGN KEY(habitacion_id) REFERENCES habitaciones(id), FOREIGN KEY(empleado_id) REFERENCES empleados(id));
CREATE TABLE inventario(id INT AUTO_INCREMENT PRIMARY KEY, producto VARCHAR(120), categoria VARCHAR(80), existencia INT, minimo INT, unidad VARCHAR(30));
CREATE TABLE movimientos_inventario(id INT AUTO_INCREMENT PRIMARY KEY, inventario_id INT NOT NULL, usuario_id INT NOT NULL, tipo VARCHAR(40), cantidad INT, fecha DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(inventario_id) REFERENCES inventario(id), FOREIGN KEY(usuario_id) REFERENCES usuarios(id));
CREATE TABLE equipaje(id INT AUTO_INCREMENT PRIMARY KEY, cliente_id INT, habitacion_id INT, estado VARCHAR(50), observaciones TEXT, fecha DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE facturas(id INT AUTO_INCREMENT PRIMARY KEY, cliente_id INT, fecha DATETIME DEFAULT CURRENT_TIMESTAMP, total DECIMAL(12,2), estado_electronico VARCHAR(80));
CREATE TABLE factura_detalle(id INT AUTO_INCREMENT PRIMARY KEY, factura_id INT NOT NULL, concepto VARCHAR(150), cantidad INT, precio DECIMAL(12,2), FOREIGN KEY(factura_id) REFERENCES facturas(id));
CREATE TABLE llamadas(id INT AUTO_INCREMENT PRIMARY KEY, usuario_id INT, cliente_id INT, telefono VARCHAR(30), asunto VARCHAR(150), notas TEXT, fecha DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE auditoria(id BIGINT AUTO_INCREMENT PRIMARY KEY, usuario_id INT, accion VARCHAR(120), detalle TEXT, fecha DATETIME DEFAULT CURRENT_TIMESTAMP);
DELIMITER $$
CREATE PROCEDURE sp_registrar_movimiento(IN p_inventario INT, IN p_usuario INT, IN p_tipo VARCHAR(40), IN p_cantidad INT)
BEGIN
 INSERT INTO movimientos_inventario(inventario_id,usuario_id,tipo,cantidad) VALUES(p_inventario,p_usuario,p_tipo,p_cantidad);
 IF p_tipo='Entrada' THEN UPDATE inventario SET existencia=existencia+p_cantidad WHERE id=p_inventario;
 ELSE UPDATE inventario SET existencia=GREATEST(0,existencia-p_cantidad) WHERE id=p_inventario;
 END IF;
END$$
CREATE TRIGGER trg_auditoria_reserva AFTER UPDATE ON reservas FOR EACH ROW
BEGIN INSERT INTO auditoria(accion,detalle) VALUES('Modificación de reserva',CONCAT(OLD.codigo,' → ',NEW.estado)); END$$
CREATE TRIGGER trg_alerta_inventario AFTER UPDATE ON inventario FOR EACH ROW
BEGIN IF NEW.existencia < NEW.minimo THEN INSERT INTO auditoria(accion,detalle) VALUES('Alerta de inventario',CONCAT(NEW.producto,' por debajo del mínimo')); END IF; END$$
DELIMITER ;
