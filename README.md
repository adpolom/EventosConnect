# EventosConnect

Sistema integrado de gestión de eventos y aforo, desarrollado en Python para el curso de **Estructuras de Datos**.

El programa simula la operación de un evento: inscribe asistentes, controla su ingreso por un torniquete respetando el aforo de cada actividad y administra el catálogo y la agenda del día. Todo funciona por consola y cada parte se apoya en una estructura de datos implementada a mano con nodos y referencias.

## Responsabilidades del equipo (numeral 12.7)

| Integrante | Módulo | Archivos | Responsabilidad |
|---|---|---|---|
| Andrés David Polo Muñoz | Modelos | `src/modelos/Asistente.py`, `src/modelos/Evento.py` | Clases base con sobrecarga de operadores para que las estructuras puedan comparar y ordenar |
| Mateo Machuca | Estructuras lineales | `src/estructuras/ListaEnlazada.py`, `src/estructuras/Cola.py`, `src/estructuras/Pila.py` | Padrón, fila del torniquete y bitácora de ingresos |
| Luis Gonzales | Árbol BST y Lista Doble | `src/estructuras/ArbolBST.py`, `src/estructuras/ListaDoblementeEnlazada.py` | Catálogo de eventos por ID y agenda navegable en ambos sentidos |
| Juan Ospino | Sistema e integración | `src/sistema/ControlEvento.py`, `src/sistema/Main.py` | Unir las 5 estructuras, aplicar las reglas del negocio (incluido el aforo) y construir el menú por consola |

## Estructuras de datos y su uso

| Estructura | Uso en el sistema | Operaciones principales |
|---|---|---|
| **Lista Enlazada** | Padrón de asistentes inscritos | Insertar, buscar por cédula, eliminar, mostrar |
| **Cola** (FIFO) | Fila de espera en el torniquete: entra primero quien llegó primero | Encolar, desencolar, ver frente |
| **Pila** (LIFO) | Bitácora de ingresos; permite deshacer el ingreso más reciente | Apilar, desapilar, ver tope |
| **Árbol Binario de Búsqueda** (`ArbolBST.py`) | Catálogo de eventos indexado por ID | Insertar sin duplicados, buscar por ID, recorrido in-orden y `eliminar(id_evento)` |
| **Lista Doblemente Enlazada** (`ListaDoblementeEnlazada.py`) | Agenda cronológica: los eventos programados ordenados por hora | Insertar, eliminar por ID, recorrer de inicio a fin y en reversa |

**Eliminación en el Árbol BST.** `eliminar(id_evento)` resuelve los tres casos estándar:

1. **Nodo hoja:** se quita directamente.
2. **Nodo con un hijo:** el hijo ocupa su lugar.
3. **Nodo con dos hijos:** se reemplaza por su **sucesor in-orden** (el menor del subárbol derecho) y luego se elimina ese sucesor.

**Agenda cronológica.** Cada nodo de la Lista Doble apunta al anterior y al siguiente, así que la agenda se recorre de inicio a fin y en reversa. `ControlEvento` ubica cada evento según su hora, de modo que la agenda siempre queda en orden cronológico, aunque los eventos se registren desordenados.

### Complejidad de las operaciones

| Estructura | Operación | Complejidad |
|---|---|---|
| Lista Enlazada | Insertar al final / buscar / eliminar | O(n) |
| Cola | Encolar / desencolar | O(1) |
| Pila | Apilar / desapilar | O(1) |
| Árbol BST | Insertar / buscar / eliminar | O(log n) en promedio, O(n) en el peor caso |
| Lista Doble | Insertar al final | O(1) |
| Lista Doble | Insertar en su lugar según la hora | O(n) |
| Lista Doble | Buscar / eliminar por ID | O(n) |
| Lista Doble | Recorrer adelante o en reversa | O(n) |

## Modelos de datos

- **Asistente** (`Asistente.py`): cédula, nombre, categoría (General, VIP u Organizador) y estado de ingreso (DENTRO o FUERA). Se compara por cédula.
- **Evento** (`Evento.py`): ID, nombre, capacidad, escenario y **hora** (formato 24 horas, por ejemplo `"14:00"`). La hora es lo que da el orden cronológico de la agenda. Se compara y ordena por ID.

## Control de aforo

La **capacidad** de cada evento es su aforo máximo, y `ControlEvento.py` la valida en el torniquete:

- Al llegar a la fila, el asistente indica a qué evento va a entrar. Si los cupos de ese evento ya están ocupados (personas dentro) o apartados (personas en la fila), el sistema no lo deja hacer la fila.
- Al dar ingreso se vuelve a revisar el aforo antes de dejar pasar a la persona.
- "Deshacer último ingreso" libera el cupo de ese evento.
- El resumen del sistema (opción 4) muestra, para cada evento de la agenda, cuántas personas hay dentro frente a su capacidad.

## Estructura del proyecto

```
EventosConnect/
├── src/
│   ├── modelos/
│   │   ├── Asistente.py                 # Participante: cédula, nombre, categoría y estado de ingreso
│   │   └── Evento.py                    # Actividad: ID, nombre, capacidad, escenario y hora
│   ├── estructuras/
│   │   ├── ListaEnlazada.py
│   │   ├── Cola.py
│   │   ├── Pila.py
│   │   ├── ArbolBST.py
│   │   └── ListaDoblementeEnlazada.py
│   └── sistema/
│       ├── ControlEvento.py             # Une las 5 estructuras y aplica las reglas del negocio
│       └── Main.py                      # Menú interactivo por consola
├── .gitignore
└── README.md
```

## Requisitos

- Python 3.8 o superior.
- No se necesita instalar ninguna librería externa.

## Cómo ejecutarlo

Desde la carpeta principal del proyecto:

```
python -m src.sistema.Main
```

En Windows, si `python` no funciona, usar `py -m src.sistema.Main`. También se puede ejecutar con el botón ▶ de VS Code abriendo `src/sistema/Main.py`.

## Menú del sistema

```
1. Asistentes (padrón)
     Inscribir, buscar por cédula, ver padrón, eliminar
2. Torniquete de acceso (fila y bitácora)
     Llegada a la fila (credencial, evento y aforo), ver quién sigue,
     dar ingreso, ver fila, ver bitácora, deshacer último ingreso
3. Eventos (catálogo y agenda)
     Registrar (con hora), buscar por ID, ver catálogo ordenado,
     ver agenda adelante y en reversa, retirar, volver a programar
     y eliminar evento
4. Resumen del sistema (incluye el aforo de cada evento)
5. Cargar datos de demostración
0. Salir
```

### Datos de demostración (opción 5)

La opción **5** carga:

- **Asistentes:** cédulas `11111`, `22222`, `33333`, `44444` y `55555`.
- **Eventos**, con sus horarios:

| ID | Hora | Evento | Capacidad | Escenario |
|---|---|---|---|---|
| 105 | 08:00 | Apertura y Registro | 300 | Auditorio Principal |
| 102 | 10:00 | Taller de Python | 3 | Sala 2 |
| 108 | 11:30 | Ponencia de IA | 150 | Sala 1 |
| 101 | 14:00 | Feria de Proyectos | 200 | Plaza Central |
| 110 | 17:00 | Cierre y Premiación | 300 | Auditorio Principal |

Los eventos se registran desordenados a propósito. El catálogo (Árbol BST) los muestra ordenados por ID, y la agenda los muestra ordenados por hora.

El Taller de Python tiene solo 3 cupos para poder demostrar el control de aforo: si las cédulas `11111`, `22222` y `33333` hacen la fila para el evento `102`, la cédula `44444` es rechazada por aforo completo.

## Reglas del negocio

- No puede haber dos asistentes con la misma cédula ni dos eventos con el mismo ID.
- Solo puede hacer la fila quien está inscrito en el padrón, no está dentro del recinto y no está ya en la fila.
- El evento elegido debe existir, estar en la agenda y tener cupos disponibles.
- Al dar ingreso, la persona sale de la Cola, se revisa el aforo, queda marcada como DENTRO y se registra en la Pila.
- "Deshacer último ingreso" revierte siempre el ingreso más reciente; la persona queda FUERA y su cupo se libera.
- No se puede eliminar del padrón a alguien que está dentro del recinto o esperando en la fila.
- Al registrar un evento se guarda en el catálogo (Árbol BST) y se ubica en la agenda según su hora.
- Retirar un evento de la agenda no lo borra del catálogo; se puede volver a programar en su hora.
- Eliminar un evento lo borra del catálogo y de la agenda. No se permite si hay personas dentro o en la fila para ese evento.
- Las cédulas solo admiten números (entre 5 y 12 dígitos). El ID y la capacidad de un evento deben ser enteros mayores que 0, y la hora debe tener el formato `HH:MM` de 24 horas.

## Restricciones de implementación

- Todas las estructuras están construidas con nodos y referencias propias.
- No se usan listas, tuplas, diccionarios ni conjuntos de Python para almacenar datos.
- Las clases `Asistente` y `Evento` sobrecargan operadores (`==`, `<`, `>`) para que las estructuras puedan comparar y ordenar sus elementos.

## Declaración de uso de Inteligencia Artificial (numeral 14)

El equipo usó herramientas de inteligencia artificial como apoyo durante el desarrollo. Cada integrante declara a continuación para qué las usó; todo lo generado con ayuda de IA fue revisado, ejecutado y probado antes de subirse al repositorio.

| Integrante | Herramienta | Uso |
|---|---|---|
| Juan Ospino | Claude (Anthropic) | Generación del código del módulo de sistema (`ControlEvento.py` y `Main.py`) a partir de las estructuras del equipo; revisión de inconsistencias del proyecto; casos de prueba; comentarios explicativos y documentación técnica (este README) |
| Andrés David Polo Muñoz | *(por completar)* | *(por completar)* |
| Mateo Machuca | *(por completar)* | *(por completar)* |
| Luis Gonzales | *(por completar)* | *(por completar)* |
