# Edge Service — IoT Telemetry Ingestion

Servicio edge para la ingesta de telemetría ambiental (CO2 y PM2.5) desde dispositivos IoT. Autentica dispositivos, valida los datos y los persiste localmente en SQLite.

## Stack Tecnológico

| Tecnología | Propósito |
|---|---|
| **Python 3.13** | Lenguaje principal |
| **uv** | Gestor de paquetes y entornos virtuales |
| **Flask** | Framework web para los endpoints REST |
| **Peewee** | ORM ligero para mapear entidades a SQLite |
| **SQLite** | Base de datos embebida local |

## Arquitectura

El proyecto sigue **Domain-Driven Design (DDD)** con dos bounded contexts:

```
edge-service/
├── app.py                         # Punto de entrada Flask
├── iam/                           # Bounded Context: Identity & Access Management
│   ├── domain/
│   │   ├── entities.py            # Entidad Device (aggregate root, 7 atributos)
│   │   └── services.py            # AuthService: valida credenciales + status ACTIVE
│   ├── application/
│   │   └── services.py            # AuthApplicationService: orquesta autenticación
│   ├── infrastructure/
│   │   ├── models.py              # DeviceModel (Peewee) → tabla 'devices'
│   │   └── repositories.py        # DeviceRepository: find, get_or_create, update_last_seen
│   └── interfaces/
│       └── services.py            # Blueprint iam_api + authenticate_request()
├── device/                        # Bounded Context: Device Telemetry
│   ├── domain/
│   │   ├── entities.py            # Entidad DeviceTelemetry (CO2, PM2.5)
│   │   └── services.py            # Validación de rangos (CO2: 0-5000, PM2.5: 0-500)
│   ├── application/
│   │   └── services.py            # DeviceTelemetryAppService: orquesta validación y guardado
│   ├── infrastructure/
│   │   ├── models.py              # DeviceTelemetryModel → tabla 'device_telemetry'
│   │   └── repositories.py        # DeviceTelemetryRepository: persistencia
│   └── interfaces/
│       └── api.py                 # Blueprint device_api + POST /api/v1/device/telemetry
└── shared/                        # Infraestructura compartida
    └── infrastructure/
        └── database.py            # SqliteDatabase('smart_band.db') + init_db()
```

## Requisitos Previos

- **Python 3.13+**
- **uv** (gestor de paquetes)

### Instalar uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Cómo Ejecutar

```bash
# Entrar al directorio del proyecto
cd edge-service

# Sincronizar dependencias (crea .venv automáticamente)
uv sync

# Ejecutar el servicio
uv run python app.py
```

El servidor arranca en `http://127.0.0.1:5000` con debug mode activado.

## API Endpoints

### `POST /api/v1/device/telemetry`

Crea un nuevo registro de telemetría ambiental para un dispositivo autenticado.

**Headers requeridos:**

```
Content-Type: application/json
X-API-Key: <api_key del dispositivo>
```

**Body (JSON):**

```json
{
  "device_id": "smart-band-001",
  "co2": 420.5,
  "pm25": 35.2,
  "created_at": "2026-05-16T22:30:00-05:00"
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `device_id` | string | Sí | Identificador del dispositivo |
| `co2` | number | Sí | Concentración de CO2 en ppm (rango: 0–5000) |
| `pm25` | number | Sí | Material particulado PM2.5 en µg/m³ (rango: 0–500) |
| `created_at` | string | No | Timestamp ISO 8601; si se omite usa UTC actual |

**Respuestas:**

| Código | Condición | Body |
|---|---|---|
| `201` | Registro creado | `{"id": 1, "device_id": "...", "co2": 420.5, "pm25": 35.2, "created_at": "..."}` |
| `400` | Campos faltantes o valores inválidos | `{"error": "..."}` |
| `401` | Credenciales inválidas o dispositivo no ACTIVE | `{"error": "..."}` |

### Probar con curl

```bash
curl -X POST http://127.0.0.1:5000/api/v1/device/telemetry \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: test-api-key-123' \
  -d '{
    "device_id": "smart-band-001",
    "co2": 420.5,
    "pm25": 35.2,
    "created_at": "2026-05-16T22:30:00-05:00"
  }'
```

## Dispositivo de Prueba (Seed)

Al iniciar, se crea automáticamente un dispositivo de desarrollo:

| Campo | Valor |
|---|---|
| `device_id` | `smart-band-001` |
| `hardware_id` | `HW-SB-001-ABC123` |
| `api_key` | `test-api-key-123` |
| `status` | `ACTIVE` |

> ⚠️ Credenciales solo para desarrollo local. No usar en producción.

## Inspeccionar la Base de Datos

```bash
sqlite3 smart_band.db ".tables"
sqlite3 smart_band.db "SELECT * FROM devices;"
sqlite3 smart_band.db "SELECT * FROM device_telemetry;"
```
