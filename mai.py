"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Universidad Nacional Abierta y a Distancia (UNAD)
Curso: Programación (Código: 213023) - Fase 4
"""

from abc import ABC, abstractmethod
import logging

# ==============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA DE LOGS (REGISTRO DE EVENTOS Y ERRORES)
# ==============================================================================
ARCHIVO_LOG = "sistema_software_fj.log"

logging.basicConfig(
    filename=ARCHIVO_LOG,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("SoftwareFJ")


# ==============================================================================
# 2. EXCEPCIONES PERSONALIZADAS DEL DOMINIO
# ==============================================================================
class SoftwareFJError(Exception):
    """Excepción base para todos los errores controlados del sistema Software FJ."""
    pass


class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos personales de un cliente incumplen las validaciones."""
    pass


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando un servicio tiene parámetros inválidos o no está disponible."""
    pass


class ReservaError(SoftwareFJError):
    """Se lanza cuando ocurre un fallo al crear, calcular o procesar una reserva."""
    pass


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza al intentar realizar una transición de estado inválida en una reserva."""
    pass


# ==============================================================================
# 3. CLASE ABSTRACTA BASE PARA ENTIDADES DEL SISTEMA
# ==============================================================================
class EntidadSistema(ABC):
    """Clase abstracta que define la estructura mínima de cualquier entidad del sistema."""

    def __init__(self, id_entidad: str):
        if not id_entidad or not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ValueError("El identificador de la entidad no puede estar vacío.")
        self._id_entidad = id_entidad.strip()

    @property
    def id_entidad(self) -> str:
        return self._id_entidad

    @abstractmethod
    def obtener_detalles(self) -> str:
        """Retorna una representación descriptiva de la entidad."""
        pass


# ==============================================================================
# 4. CLASE CLIENTE (ENCAPSULACIÓN Y VALIDACIONES ESTRICTAS)
# ==============================================================================
class Cliente(EntidadSistema):
    """Representa un cliente de Software FJ con validación estricta de datos personales."""

    def __init__(self, id_entidad: str, nombre: str, correo: str, telefono: str):
        super().__init__(id_entidad)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        logger.info(f"Cliente registrado exitosamente: ID={self._id_entidad}, Nombre={self._nombre}")

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ClienteInvalidoError(
                f"Nombre inválido ('{valor}'): debe ser texto con al menos 3 caracteres."
            )
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        if not valor or not isinstance(valor, str) or "@" not in valor or "." not in valor.split("@")[-1]:
            raise ClienteInvalidoError(
                f"Correo electrónico inválido ('{valor}'): formato incorrecto."
            )
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.isdigit() or len(valor) < 7:
            raise ClienteInvalidoError(
                f"Teléfono inválido ('{valor}'): debe contener únicamente dígitos (mínimo 7)."
            )
        self._telefono = valor.strip()

    def obtener_detalles(self) -> str:
        return (
            f"Cliente [ID: {self._id_entidad}] | Nombre: {self._nombre} | "
            f"Correo: {self._correo} | Tel: {self._telefono}"
        )


# ==============================================================================
# 5. CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS (HERENCIA Y POLIMORFISMO)
# ==============================================================================
class Servicio(EntidadSistema, ABC):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    def __init__(self, id_entidad: str, nombre_servicio: str, costo_base: float, disponible: bool = True):
        super().__init__(id_entidad)
        self.nombre_servicio = nombre_servicio
        self.costo_base = costo_base
        self.disponible = disponible

    @property
    def nombre_servicio(self) -> str:
        return self._nombre_servicio

    @nombre_servicio.setter
    def nombre_servicio(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ServicioNoDisponibleError("El nombre del servicio debe tener al menos 3 caracteres.")
        self._nombre_servicio = valor.strip()

    @property
    def costo_base(self) -> float:
        return self._costo_base

    @costo_base.setter
    def costo_base(self, valor: float):
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ServicioNoDisponibleError(
                f"Costo base inválido ({valor}): debe ser un valor numérico mayor a 0."
            )
        self._costo_base = float(valor)

    @abstractmethod
    def validar_parametros(self, **kwargs) -> None:
        """Valida los parámetros específicos requeridos por cada tipo de servicio."""
        pass

    @abstractmethod
    def calcular_costo(self, *args, **kwargs) -> float:
        """Método polimórfico y sobrecargado mediante argumentos opcionales."""
        pass


class ReservaSala(Servicio):
    """Servicio especializado para reserva de salas de reuniones y capacitación."""

    def __init__(self, id_entidad: str, nombre_servicio: str, costo_base: float, capacidad: int, disponible: bool = True):
        super().__init__(id_entidad, nombre_servicio, costo_base, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioNoDisponibleError("La capacidad de la sala debe ser un entero positivo.")
        self.capacidad = capacidad
        logger.info(f"Servicio ReservaSala creado: {self.obtener_detalles()}")

    def validar_parametros(self, horas: int = 1, asistentes: int = 1, **kwargs) -> None:
        if not isinstance(horas, int) or horas <= 0:
            raise ValueError("La duración en horas debe ser un número entero mayor a cero.")
        if not isinstance(asistentes, int) or asistentes <= 0 or asistentes > self.capacidad:
            raise ValueError(
                f"Número de asistentes ({asistentes}) fuera de rango (1 a {self.capacidad})."
            )

    def calcular_costo(
        self,
        horas: int = 1,
        asistentes: int = 1,
        impuesto: float = 0.19,
        descuento: float = 0.0,
    ) -> float:
        """Sobrecarga funcional: calcula costo por horas con impuestos y descuentos opcionales."""
        try:
            self.validar_parametros(horas=horas, asistentes=asistentes)
            if not (0.0 <= descuento < 1.0) or impuesto < 0:
                raise ValueError("Porcentaje de descuento o impuesto fuera de rango válido.")
            subtotal = self.costo_base * horas
            subtotal_con_descuento = subtotal * (1 - descuento)
            total = subtotal_con_descuento * (1 + impuesto)
            return round(total, 2)
        except Exception as e:
            logger.error(f"Error al calcular costo en ReservaSala ({self.id_entidad}): {e}")
            raise ReservaError(f"Cálculo inconsistente en sala '{self.nombre_servicio}'.") from e

    def obtener_detalles(self) -> str:
        return (
            f"Sala [ID: {self.id_entidad}] '{self.nombre_servicio}' | "
            f"Tarifa/h: ${self.costo_base:.2f} | Capacidad: {self.capacidad} pers."
        )


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de hardware y equipos tecnológicos."""

    def __init__(self, id_entidad: str, nombre_servicio: str, costo_base: float, serial: str, disponible: bool = True):
        super().__init__(id_entidad, nombre_servicio, costo_base, disponible)
        if not serial or not serial.strip():
            raise ServicioNoDisponibleError("El serial del equipo es obligatorio.")
        self.serial = serial.strip()
        logger.info(f"Servicio AlquilerEquipo creado: {self.obtener_detalles()}")

    def validar_parametros(self, dias: int = 1, **kwargs) -> None:
        if not isinstance(dias, int) or dias <= 0:
            raise ValueError("Los días de alquiler deben ser un entero mayor a cero.")

    def calcular_costo(
        self,
        dias: int = 1,
        seguro_equipo: float = 15.0,
        impuesto: float = 0.19,
    ) -> float:
        """Sobrecarga funcional: calcula costo por días más póliza de seguro e impuesto."""
        try:
            self.validar_parametros(dias=dias)
            if seguro_equipo < 0 or impuesto < 0:
                raise ValueError("El seguro e impuesto no pueden ser negativos.")
            subtotal = (self.costo_base * dias) + seguro_equipo
            total = subtotal * (1 + impuesto)
            return round(total, 2)
        except Exception as e:
            logger.error(f"Error al calcular costo en AlquilerEquipo ({self.id_entidad}): {e}")
            raise ReservaError(f"Fallo en tarificación del equipo '{self.nombre_servicio}'.") from e

    def obtener_detalles(self) -> str:
        return (
            f"Equipo [ID: {self.id_entidad}] '{self.nombre_servicio}' | "
            f"Tarifa/día: ${self.costo_base:.2f} | Serial: {self.serial}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para consultoría y asesoría de ingeniería."""

    def __init__(self, id_entidad: str, nombre_servicio: str, costo_base: float, especialista: str, disponible: bool = True):
        super().__init__(id_entidad, nombre_servicio, costo_base, disponible)
        if not especialista or len(especialista.strip()) < 3:
            raise ServicioNoDisponibleError("Debe asignar un especialista válido.")
        self.especialista = especialista.strip()
        logger.info(f"Servicio AsesoriaEspecializada creado: {self.obtener_detalles()}")

    def validar_parametros(self, sesiones: int = 1, **kwargs) -> None:
        if not isinstance(sesiones, int) or sesiones <= 0:
            raise ValueError("La cantidad de sesiones debe ser mayor a cero.")

    def calcular_costo(
        self,
        sesiones: int = 1,
        recargo_urgencia: float = 0.0,
        descuento_corporativo: float = 0.0,
    ) -> float:
        """Sobrecarga funcional: calcula costo por sesiones con recargo de urgencia o descuento."""
        try:
            self.validar_parametros(sesiones=sesiones)
            if recargo_urgencia < 0 or not (0.0 <= descuento_corporativo < 1.0):
                raise ValueError("Parámetros financieros de asesoría inválidos.")
            base = (self.costo_base * sesiones) + recargo_urgencia
            total = base * (1 - descuento_corporativo)
            return round(total, 2)
        except Exception as e:
            logger.error(f"Error al calcular costo en AsesoriaEspecializada ({self.id_entidad}): {e}")
            raise ReservaError(f"Error calculando honorarios de '{self.nombre_servicio}'.") from e

    def obtener_detalles(self) -> str:
        return (
            f"Asesoría [ID: {self.id_entidad}] '{self.nombre_servicio}' | "
            f"Tarifa/sesión: ${self.costo_base:.2f} | Especialista: {self.especialista}"
        )


# ==============================================================================
# 6. CLASE RESERVA (INTEGRACIÓN Y MANEJO AVANZADO DE EXCEPCIONES)
# ==============================================================================
class Reserva(EntidadSistema):
    """Integra Cliente, Servicio, duración y estado con bloques try/except/else/finally."""

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: int):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise ReservaError("Se requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ReservaError("Se requiere una instancia válida de Servicio.")
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "PENDIENTE"
        self.costo_total = 0.0

    def procesar_reserva(self, **parametros_costo) -> None:
        """
        Procesa y confirma una reserva aplicando:
        - try / except / else / finally
        - Encadenamiento de excepciones (raise ... from ...)
        - Registro detallado en logs
        """
        logger.info(f"Iniciando procesamiento de Reserva {self.id_entidad} para {self.cliente.nombre}.")
        try:
            if self.estado != "PENDIENTE":
                raise OperacionNoPermitidaError(
                    f"La reserva {self.id_entidad} no puede procesarse en estado '{self.estado}'."
                )
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(
                    f"El servicio '{self.servicio.nombre_servicio}' no está disponible actualmente."
                )

            # Invocación polimórfica de calcular_costo según el subtipo de servicio
            self.costo_total = self.servicio.calcular_costo(**parametros_costo)

        except ServicioNoDisponibleError as err_disp:
            self.estado = "RECHAZADA"
            logger.warning(f"Reserva {self.id_entidad} rechazada por disponibilidad: {err_disp}")
            raise ReservaError(f"Fallo de disponibilidad en reserva {self.id_entidad}.") from err_disp

        except OperacionNoPermitidaError as err_op:
            logger.error(f"Operación no permitida en reserva {self.id_entidad}: {err_op}")
            raise ReservaError(f"Estado inválido en reserva {self.id_entidad}.") from err_op

        except ReservaError as err_res:
            self.estado = "FALLIDA"
            logger.error(f"Error de cálculo/parámetros en reserva {self.id_entidad}: {err_res}")
            raise

        except Exception as err_gral:
            self.estado = "FALLIDA"
            logger.critical(f"Error inesperado procesando reserva {self.id_entidad}: {err_gral}")
            raise ReservaError(f"Error crítico inesperado en reserva {self.id_entidad}.") from err_gral

        else:
            # Se ejecuta únicamente si el bloque try finalizó sin excepciones
            self.estado = "CONFIRMADA"
            logger.info(
                f"Reserva {self.id_entidad} CONFIRMADA | Cliente: {self.cliente.nombre} | "
                f"Servicio: {self.servicio.nombre_servicio} | Total: ${self.costo_total:.2f}"
            )
            print(
                f"  [OK] Reserva {self.id_entidad} CONFIRMADA -> Cliente: {self.cliente.nombre} | "
                f"Servicio: {self.servicio.nombre_servicio} | Total: ${self.costo_total:.2f}"
            )

        finally:
            # Se ejecuta siempre para garantizar auditoría continua
            logger.info(f"Auditoría finally -> Reserva {self.id_entidad} finalizó ciclo en estado: {self.estado}")

    def cancelar_reserva(self) -> None:
        """Cancela una reserva confirmada o pendiente con control de excepciones."""
        try:
            if self.estado == "CANCELADA":
                raise OperacionNoPermitidaError(f"La reserva {self.id_entidad} ya se encuentra cancelada.")
            if self.estado in ("RECHAZADA", "FALLIDA"):
                raise OperacionNoPermitidaError(
                    f"No se puede cancelar una reserva en estado '{self.estado}'."
                )
        except OperacionNoPermitidaError as e:
            logger.warning(f"Intento inválido de cancelación: {e}")
            raise ReservaError("No fue posible cancelar la reserva.") from e
        else:
            self.estado = "CANCELADA"
            logger.info(f"Reserva {self.id_entidad} CANCELADA correctamente.")
            print(f"  [OK] Reserva {self.id_entidad} ha sido CANCELADA.")
        finally:
            logger.info(f"Finalizó verificación de cancelación para reserva {self.id_entidad}.")

    def obtener_detalles(self) -> str:
        return (
            f"Reserva [ID: {self.id_entidad}] | Estado: {self.estado} | "
            f"Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre_servicio} | "
            f"Total: ${self.costo_total:.2f}"
        )


# ==============================================================================
# 7. EJECUCIÓN DE 10 SIMULACIONES COMPLETAS (VÁLIDAS E INVÁLIDAS)
# ==============================================================================
def ejecutar_simulacion():
    print("=" * 75)
    print(" SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ (SIMULACIÓN DE 10 OPERACIONES)")
    print("=" * 75)

    clientes = []
    servicios = []
    reservas = []

    # --- SIMULACIÓN 1: Registro válido de Cliente ---
    print("\n1. [Simulación 1] Registro válido de cliente (Laura Méndez):")
    try:
        c1 = Cliente("CLI-001", "Laura Sofía Méndez", "laura.mendez@unad.edu.co", "3104567890")
        clientes.append(c1)
        print(f"  [OK] {c1.obtener_detalles()}")
    except SoftwareFJError as e:
        print(f"  [ERROR CONTROLADO] {e}")

    # --- SIMULACIÓN 2: Registro inválido de Cliente (correo mal formado) ---
    print("\n2. [Simulación 2] Registro inválido de cliente (correo sin dominio válido):")
    try:
        c_err1 = Cliente("CLI-002", "Pedro Gómez", "pedro.gomez_sin_arroba", "3209876543")
        clientes.append(c_err1)
    except ClienteInvalidoError as e:
        logger.error(f"Simulación 2 - Captura de ClienteInvalidoError: {e}")
        print(f"  [EXCEPCIÓN CAPTURADA] {e}")

    # --- SIMULACIÓN 3: Registro inválido de Cliente (teléfono no numérico) ---
    print("\n3. [Simulación 3] Registro inválido de cliente (teléfono con letras):")
    try:
        c_err2 = Cliente("CLI-003", "Andrés Felipe Rojas", "andres@empresa.com", "315ABC123")
        clientes.append(c_err2)
    except ClienteInvalidoError as e:
        logger.error(f"Simulación 3 - Captura de ClienteInvalidoError: {e}")
        print(f"  [EXCEPCIÓN CAPTURADA] {e}")

    # --- SIMULACIÓN 4: Registro válido de segundo Cliente ---
    print("\n4. [Simulación 4] Registro válido de segundo cliente (Carlos Andrade):")
    try:
        c2 = Cliente("CLI-004", "Carlos Eduardo Andrade", "carlos.andrade@techcol.co", "3001122334")
        clientes.append(c2)
        print(f"  [OK] {c2.obtener_detalles()}")
    except SoftwareFJError as e:
        print(f"  [ERROR CONTROLADO] {e}")

    # --- SIMULACIÓN 5: Creación correcta de los 3 tipos de Servicios ---
    print("\n5. [Simulación 5] Creación válida de servicios especializados (Sala, Equipo, Asesoría):")
    try:
        sala = ReservaSala("SRV-101", "Auditorio Innovación", 80.0, capacidad=25)
        equipo = AlquilerEquipo("SRV-102", "Workstation Dell Precision", 45.0, serial="DL-99482-CO")
        asesoria = AsesoriaEspecializada("SRV-103", "Arquitectura de Microservicios", 150.0, "Ing. Diana Vargas")
        servicios.extend([sala, equipo, asesoria])
        for s in servicios:
            print(f"  [OK] {s.obtener_detalles()}")
    except SoftwareFJError as e:
        print(f"  [ERROR CONTROLADO] {e}")

    # --- SIMULACIÓN 6: Creación incorrecta de Servicio (costo base negativo) ---
    print("\n6. [Simulación 6] Creación inválida de servicio (costo base negativo):")
    try:
        sala_invalida = ReservaSala("SRV-104", "Sala Fantasma", -50.0, capacidad=10)
        servicios.append(sala_invalida)
    except ServicioNoDisponibleError as e:
        logger.error(f"Simulación 6 - Captura de ServicioNoDisponibleError: {e}")
        print(f"  [EXCEPCIÓN CAPTURADA] {e}")

    # --- SIMULACIÓN 7: Reserva exitosa de Sala con descuento e IVA ---
    print("\n7. [Simulación 7] Reserva exitosa de Sala (4 horas, 15 asistentes, 10% descuento):")
    try:
        r1 = Reserva("RES-001", clientes[0], servicios[0], duracion=4)
        r1.procesar_reserva(horas=4, asistentes=15, impuesto=0.19, descuento=0.10)
        reservas.append(r1)
    except ReservaError as e:
        print(f"  [EXCEPCIÓN CAPTURADA] {e} | Causa raíz: {e.__cause__}")

    # --- SIMULACIÓN 8: Reserva fallida por exceso de capacidad en Sala ---
    print("\n8. [Simulación 8] Reserva fallida (asistentes exceden capacidad máxima de la sala):")
    try:
        r2 = Reserva("RES-002", clientes[1], servicios[0], duracion=2)
        r2.procesar_reserva(horas=2, asistentes=40)  # Capacidad máxima es 25
        reservas.append(r2)
    except ReservaError as e:
        print(f"  [EXCEPCIÓN CAPTURADA] {e} | Causa raíz: {e.__cause__}")

    # --- SIMULACIÓN 9: Reserva fallida por servicio no disponible y posterior recuperación ---
    print("\n9. [Simulación 9] Intento de reserva sobre servicio no disponible:")
    try:
        servicios[1].disponible = False  # Se marca el equipo como no disponible
        r3 = Reserva("RES-003", clientes[0], servicios[1], duracion=3)
        r3.procesar_reserva(dias=3, seguro_equipo=20.0)
    except ReservaError as e:
        print(f"  [EXCEPCIÓN CAPTURADA] {e} | Causa raíz: {e.__cause__}")
    finally:
        servicios[1].disponible = True  # Se habilita nuevamente el equipo

    # --- SIMULACIÓN 10: Reserva exitosa de Asesoría + Cancelación controlada de Reserva 1 ---
    print("\n10. [Simulación 10] Reserva exitosa de Asesoría y cancelación de Reserva RES-001:")
    try:
        r4 = Reserva("RES-004", clientes[1], servicios[2], duracion=2)
        r4.procesar_reserva(sesiones=2, recargo_urgencia=30.0, descuento_corporativo=0.05)
        reservas.append(r4)

        # Cancelación válida de r1 y prueba de doble cancelación controlada
        reservas[0].cancelar_reserva()
        reservas[0].cancelar_reserva()  # Debe lanzar ReservaError encadenado
    except ReservaError as e:
        print(f"  [EXCEPCIÓN CAPTURADA EN DOBLE CANCELACIÓN] {e} | Causa raíz: {e.__cause__}")

    print("\n" + "=" * 75)
    print(f" EJECUCIÓN COMPLETADA SIN INTERRUPCIONES. LOG GUARDADO EN: {ARCHIVO_LOG}")
    print("=" * 75)


if __name__ == "__main__":
    ejecutar_simulacion()