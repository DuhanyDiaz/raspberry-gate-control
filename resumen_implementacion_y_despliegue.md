# 🛡️ Resumen Ejecutivo de Implementación de Seguridad y Hoja de Ruta de Despliegue IoT
**Proyecto:** Control de Accesos FIUSAC / Escuela de Ingeniería Mecánica Industrial (EMI)  
**Fecha:** Octubre 2026  
**Entorno:** Backend (FastAPI / Python), Frontend (React / Vite), IoT (Raspberry Pi Edge)

---

## 📌 PARTE 1: Resumen de lo Implementado (Fases 1 a 5)

Durante las sesiones de trabajo se transformó por completo la seguridad y la gestión de datos sensibles del proyecto, mitigando vulnerabilidades críticas en reposo, en tránsito y frente a ataques de fuerza bruta.

### 🔹 Fase 1: Hasheo Criptográfico de Contraseñas y Llaves Temporales
* **Problema resuelto:** Las contraseñas de los alumnos/usuarios y la llave de recuperación del administrador se almacenaban en texto plano.
* **Implementación:**
  * Integración de **Bcrypt** con factor de coste y *salt* aleatorio mediante `auth.get_password_hash()` y `auth.verify_password()`.
  * Verificación resistente a ataques de temporización (*timing attacks*) en `crud.authenticate_user()`.
  * Hasheo con **SHA-256** de la llave temporal de recuperación del Administrador (`recovery_key`) en `crud.set_recovery_key()`.
  * Mecanismo de *auto-upgrade* en caliente: si un usuario con clave heredada en texto plano inicia sesión, se migra automáticamente a hash Bcrypt.

### 🔹 Fase 2: Migración Masiva e Idempotente de la Base de Datos
* **Problema resuelto:** Existían registros activos en la base de datos histórica (`accesos_EMI.db`) con contraseñas en texto plano de 4 caracteres.
* **Implementación:**
  * Creación y ejecución del script `backend/migrate_passwords.py`.
  * **Respaldo preventivo automático:** Generación de copias de seguridad fechadas (`accesos_EMI.db.backup_*`).
  * **Idempotencia total:** Inspección inteligente para evitar el "doble hasheo" de claves ya protegidas con prefijo `$2b$`.
  * El 100% de los usuarios de la base de datos quedaron protegidos con hashes de 60 caracteres.
  * Fijación de la ruta canónica y absoluta a la base de datos en `backend/database.py`.

### 🔹 Fase 3: Cifrado Simétrico del PIN en Reposo (Fernet AES)
* **Problema resuelto:** El PIN de acceso a la puerta (4 dígitos) estaba en texto plano en la base de datos. Como el usuario legítimo y el administrador deben poder seguir viéndolo en su panel, no podía utilizarse un hash irreversible.
* **Implementación:**
  * Creación del módulo `backend/crypto_utils.py` utilizando **Fernet (AES-128-CBC + HMAC-SHA256)** con una llave maestra persistente (`.pin_key`), ignorada por git en `.gitignore`.
  * Creación de un **Descriptor de Propiedad (Getter/Setter)** en `models.AccessRequest`:
    * En disco/SQLite se guarda en `_pin_acceso` como token cifrado de 100 caracteres (`gAAAAA...`).
    * Al leerlo en la API o portal web, se descifra al vuelo en memoria RAM en microsegundos (<0.005 ms).
  * Optimización de `crud.validate_pin()` para comparar el PIN tecleado contra las solicitudes aprobadas descifradas en memoria.
  * Creación y ejecución de `backend/migrate_pins.py` para cifrar todos los PINs existentes en la base de datos.

### 🔹 Fase 4: Control de Acceso con Tokens JWT y Protección de PII
* **Problema resuelto:** Los endpoints administrativos de solicitudes (`/api/solicitudes/aprobadas`, `/pendientes`, `/historial`) eran públicos y exponían nombres, carnés, correos y DPIs a cualquiera en la red.
* **Implementación:**
  * En `/api/admin/login`, emisión de **Tokens JWT (`HS256`)** con expiración de 60 minutos.
  * Blindaje de todas las rutas administrativas en `backend/main.py` mediante la dependencia `Depends(auth.get_current_admin)`. Intentos sin token son rechazados con `401 Unauthorized`.
  * En `frontend/src/AdminPanel.jsx`, gestión del Bearer Token en memoria/local storage y envío automático en el header `Authorization: Bearer <token>`.
  * Filtrado estricto mediante `response_model=schemas.AccessRequestResponse`: la contraseña **nunca viaja hacia el navegador**.

### 🔹 Fase 5: Blindaje contra Fuerza Bruta (Rate Limiting de 5 Intentos)
* **Problema resuelto:** Los PINs de 4 dígitos (10,000 combinaciones) podían ser vulnerados mediante fuerza bruta automatizada en 2 minutos.
* **Implementación:**
  * Creación del motor en memoria `backend/rate_limiter.py`.
  * **Regla estricta:** Al 5to intento fallido consecutivo, la IP o cliente queda bloqueado temporalmente por **60 segundos** (`HTTP 429 Too Many Requests`).
  * Durante el bloqueo, incluso si se ingresa el PIN correcto, la puerta no se abre.
  * Respuestas informativas con cuenta regresiva en segundos en tiempo real.
  * Registro de auditoría automática en `access_history`: alerta al administrador de posibles intentos de intrusión en el laboratorio.
  * Interfaz en `frontend/src/Keypad.jsx` adaptada con advertencia visual de teclado bloqueado.

---

## 🚀 PARTE 2: Plan de Despliegue en la Nube y Edge IoT (Lo que Haremos)

Para garantizar disponibilidad 24/7 de forma gratuita, escalable y sin sobrecargar la Raspberry Pi, se llevará a cabo la siguiente arquitectura desacoplada:

```
[ Usuario / Celular ]         [ Administrador / Laptop ]
         │                               │
         └───────────────┬───────────────┘
                         ▼
             Frontend en Vercel (React)
             (https://emi-accesos.vercel.app)
                         │
                         ▼ HTTPS (JWT / APIs)
             Backend en Render (FastAPI)
             (https://emi-api.onrender.com)
                         │
                         ▼ SQLAlchemy (Driver PostgreSQL)
             Base de Datos en Supabase / Neon
             (PostgreSQL Gestionado en la Nube)
                         ▲
                         │ HTTPS Saliente (POST PIN)
             Cliente IoT en Raspberry Pi
             (cliente_iot.py + Teclado + Relé Físico)
```

---

## 📋 Lista de Tareas para la Migración y Despliegue

### Paso 1: Transición de Base de Datos (SQLite ➔ PostgreSQL)
- [ ] Crear proyecto en **Supabase** o **Neon.tech** y obtener la URL de conexión `postgresql://...`.
- [ ] Instalar `psycopg2-binary` en el backend:
  ```bash
  .venv/bin/pip install psycopg2-binary
  .venv/bin/pip freeze > requirements.txt
  ```
- [ ] Modificar `backend/database.py` para leer `DATABASE_URL` desde variables de entorno y adaptar los parámetros de conexión de PostgreSQL.
- [ ] Exportar los datos existentes de SQLite a PostgreSQL para no perder usuarios, historial ni credenciales actuales.

### Paso 2: Variables de Entorno en Backend (Render / Producción)
Configurar en el panel de **Render** las variables críticas para evitar pérdida de datos entre reinicios del servidor efímero:
* `DATABASE_URL`: Cadena de conexión de Supabase.
* `PIN_ENCRYPTION_KEY`: La clave de 32 bytes de Fernet (para descifrar los PINs en la nube).
* `JWT_SECRET_KEY`: Llave criptográfica secreta para firmar los tokens JWT del Admin.
* `ENVIRONMENT`: `production`.

### Paso 3: Despliegue del Frontend (Vercel)
- [ ] Centralizar la URL de la API en el frontend mediante variables de entorno Vite:
  Crear `.env` local: `VITE_API_URL=http://127.0.0.1:8000`
  En Vercel: `VITE_API_URL=https://emi-api.onrender.com`
- [ ] Conectar el repositorio de GitHub con **Vercel** apuntando a la carpeta `frontend/`.

### Paso 4: Cliente IoT Ligero en Raspberry Pi (`cliente_iot.py`)
- [ ] Crear el script ligero en la Raspberry Pi que prescinde de servidores locales:
  * Lee la entrada del teclado numérico físico (o emulado).
  * Envía un `POST` seguro a `https://emi-api.onrender.com/api/accesos/validar`.
  * Si la respuesta es `200 OK`, activa el pin GPIO del relé por 5 segundos para abrir la cerradura magnética.
  * Si la respuesta es `429 Too Many Requests`, emite una alerta sonora/visual de teclado bloqueado.
- [ ] Configurar el script como servicio de sistema (`systemd`) en la Raspberry Pi para arranque automático en caso de corte eléctrico.

---

## 📊 Matriz de Responsabilidades y Seguridad

| Componente | Plataforma | Rol Principal | Mecanismo de Seguridad |
| :--- | :--- | :--- | :--- |
| **Frontend** | Vercel | Interfaz gráfica y paneles | HTTPS, sin almacenamiento de claves sensibles |
| **Backend** | Render | Reglas de negocio y autenticación | JWT Bearer, Rate Limiting (5 intentos), CORS |
| **Base de Datos** | Supabase | Almacén persistente en la nube | Contraseñas en Bcrypt, PINs en Fernet AES |
| **Hardware** | Raspberry Pi | Control de cerradura y relé | Peticiones salientes HTTPS (sin puertos abiertos) |
