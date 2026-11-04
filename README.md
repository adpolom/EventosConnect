# EventosConnect

Sistema integrado de gestión de eventos y aforo, desarrollado en Python para el curso de **Estructuras de Datos**.

El programa simula la operación de un evento: inscribe asistentes, controla su ingreso por un torniquete y administra el catálogo y la agenda de actividades. Todo funciona por consola y cada parte se apoya en una estructura de datos implementada a mano con nodos y referencias.

## Integrantes

| Integrante | Módulo | Archivos |
|---|---|---|
| Andrés David Polo Muñoz | Modelos | `src/modelos/Asistente.py`, `src/modelos/Evento.py` |
| Mateo Machuca | Estructuras lineales | `src/estructuras/ListaEnlazada.py`, `src/estructuras/Cola.py`, `src/estructuras/Pila.py` |
| Luis Gonzales | Estructuras de búsqueda y navegación | `src/estructuras/ArbolBST.py`, `src/estructuras/ListaDoblementeEnlazada.py` |
| Juan Ospino | Sistema e integración | `src/sistema/ControlEvento.py`, `src/sistema/Main.py` |

## Estructuras de datos y su uso

| Estructura | Uso en el sistema | Operaciones principales |
|---|---|---|
| **Lista Enlazada** | Padrón de asistentes inscritos | Insertar, buscar por cédula, eliminar, mostrar |
| **Cola** (FIFO) | Fila de espera en el torniquete: entra primero quien llegó primero | Encolar, desencolar, ver frente |
| **Pila** (LIFO) | Bitácora de ingresos; permite deshacer el ingreso más reciente | Apilar, desapilar, ver tope |
| **Árbol Binario de Búsqueda** | Catálogo de eventos indexado por ID | Insertar sin duplicados, buscar por ID, recorrido in-orden |
| **Lista Doblemente Enlazada** | Agenda de eventos programados | Insertar al final, eliminar por ID, recorrer adelante y atrás |

### Complejidad de las operaciones

| Estructura | Operación | Complejidad |
|---|---|---|
| Lista Enlazada | Insertar al final / buscar / eliminar | O(n) |
| Cola | Encolar / desencolar | O(1) |
| Pila | Apilar / desapilar | O(1) |
| Árbol BST | Insertar / buscar | O(log n) en promedio, O(n) en el peor caso |
| Lista Doble | Insertar al final | O(1) |
| Lista Doble | Buscar / eliminar por ID | O(n) |

## Estructura del proyecto

```
EventosConnect/
├── src/
│   ├── modelos/
│   │   ├── Asistente.py                 # Participante: cédula, nombre, categoría y estado de ingreso
│   │   └── Evento.py                    # Actividad: ID, nombre, capacidad y escenario
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
     Llegada a la fila, ver quién sigue, dar ingreso,
     ver fila, ver bitácora, deshacer último ingreso
3. Eventos (catálogo y agenda)
     Registrar, buscar por ID, ver catálogo ordenado,
     ver agenda adelante y en reversa, retirar y volver a programar
4. Resumen del sistema
5. Cargar datos de demostración
0. Salir
```

### Datos de demostración

La opción **5** carga datos de prueba:

- **Asistentes:** cédulas `11111`, `22222`, `33333`, `44444` y `55555`.
- **Eventos:** IDs `105`, `102`, `108`, `101` y `110`, registrados en ese orden. La agenda los muestra en ese mismo orden y el catálogo (Árbol BST) los muestra ordenados de menor a mayor.

## Reglas del negocio

- No puede haber dos asistentes con la misma cédula ni dos eventos con el mismo ID.
- Solo puede hacer la fila quien está inscrito en el padrón, no está dentro del recinto y no está ya en la fila.
- Al dar ingreso, la persona sale de la Cola, queda marcada como DENTRO y se registra en la Pila.
- "Deshacer último ingreso" revierte siempre el ingreso más reciente; la persona queda FUERA y puede volver a la fila.
- No se puede eliminar del padrón a alguien que está dentro del recinto o esperando en la fila.
- Al registrar un evento se guarda en el catálogo (Árbol BST) y se programa al final de la agenda.
- Retirar un evento de la agenda no lo borra del catálogo; se puede volver a programar.
- Las cédulas solo admiten números (entre 5 y 12 dígitos); el ID y la capacidad de un evento deben ser enteros mayores que 0.

## Restricciones de implementación

- Todas las estructuras están construidas con nodos y referencias propias.
- No se usan listas, tuplas, diccionarios ni conjuntos de Python para almacenar datos.
- Las clases `Asistente` y `Evento` sobrecargan operadores (`==`, `<`, `>`) para que las estructuras puedan comparar y ordenar sus elementos.
