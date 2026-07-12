# NutriSync - Plataforma de Gestión Profesional para Nutricionistas

Plataforma web basada en **Django** con arquitectura modular para la gestión integral de consultas nutricionales.

El sistema está diseñado específicamente como un CRM/ERP para profesionales de la nutrición, permitiendo gestionar el expediente de los pacientes, citas, planes nutricionales, seguimiento de medidas corporales y notas clínicas.

Este proyecto se ejecuta en un entorno de desarrollo en contenedores (Docker) que incluye la aplicación web, una base de datos PostgreSQL y la herramienta gráfica pgAdmin4.

---

## 🏛️ Estructura del Proyecto

El sistema está dividido de forma modular en 5 aplicaciones principales:

1. **`core`**: Base del sistema, autenticación, `PerfilNutricionista` y dashboard general.
2. **`pacientes`**: Gestión de expedientes de pacientes, historial médico y datos de contacto.
3. **`citas`**: Calendario, programación de consultas y recordatorios.
4. **`nutricion`**: Base de datos de alimentos, diseño de dietas y menús semanales.
5. **`seguimiento`**: Registro de medidas antropométricas, evolución, logs y notas clínicas.

---

## 🚀 Requisitos Previos

Asegúrate de tener instalado lo siguiente en tu sistema antes de comenzar:

* **Docker Desktop** (Debe estar ejecutándose)
* **Git** (Para clonar/actualizar el repositorio)

---

## 🛠️ Instrucciones de Instalación y Ejecución

Sigue estos pasos en orden para levantar el proyecto:

### 1. Levantar los contenedores

Abre una terminal en la raíz del proyecto (donde se encuentra el archivo `docker-compose.yml`) y ejecuta:

```bash
docker compose up -d --build
```

> *Nota: Este comando descarga las imágenes (Python, Postgres, pgAdmin), instala las dependencias y arranca los contenedores en segundo plano.*

### 2. Aplicar las migraciones a la Base de Datos

Una vez que los contenedores estén corriendo, debes crear las tablas en PostgreSQL ejecutando:

```bash
docker compose exec web python manage.py migrate
```

### 3. Crear al Superusuario (Nutricionista inicial)

Para tener una cuenta administrativa y poder iniciar sesión en el sistema:

```bash
docker compose exec web python manage.py createsuperuser
```

*(Sigue las instrucciones en la consola para asignar un usuario, correo y contraseña).*

---

## 🌐 Enlaces de Acceso

Una vez levantado y configurado el entorno, puedes acceder a las plataformas desde tu navegador:

### 1. Sistema NutriSync y Panel Administrativo

* **URL:** [http://localhost:8000/](http://localhost:8000/)
* Inicia sesión con el usuario que creaste en el paso anterior.
* Para el panel clásico de Django: [http://localhost:8000/admin/](http://localhost:8000/admin/)

### 2. Gestor de Base de Datos (pgAdmin4)

* **URL:** [http://localhost:5050/](http://localhost:5050/)
* **Email:** `admin@admin.com`
* **Contraseña:** `admin`

#### ¿Cómo conectar pgAdmin a la base de datos PostgreSQL por primera vez?

Cuando entres a pgAdmin por primera vez, deberás registrar el servidor:

1. Haz clic derecho en **"Servers"** > **"Register"** > **"Server..."**.
2. En la pestaña **General**, ponle como nombre `NutriSync DB`.
3. En la pestaña **Connection**, llena los datos exactamente así:
   * **Host name/address:** `db`
   * **Port:** `5432`
   * **Maintenance database:** `nutrisync_db`
   * **Username:** `postgres`
   * **Password:** `postgres`
   * Marca la casilla **"Save password?"** y haz clic en **Save**.

---

## 🛑 Comandos Útiles de Docker

Para detener los contenedores temporalmente sin perder nada:

```bash
docker compose stop
```

Para encenderlos nuevamente:

```bash
docker compose start
```

Para reiniciar el servidor web (por ejemplo, si se queda colgado al inicio por esperar a la base de datos):

```bash
docker compose restart web
```

Para destruir los contenedores (la base de datos persistirá en los volúmenes, por lo que no perderás la información guardada):

```bash
docker compose down
```

Para ver los logs del sistema en tiempo real en caso de error:

```bash
docker compose logs -f web
```

---

## 📱 Aplicación Móvil (Flutter)

La aplicación móvil está desarrollada con **Flutter** y se comunica directamente con el backend de Django a través del API REST expuesto.

### Requisitos Previos

Antes de encender la aplicación, asegúrate de contar con:
* **Flutter SDK** instalado y configurado (`flutter doctor` limpio).
* Un **Emulador** (Android/iOS) ejecutándose o un **Dispositivo Físico** conectado con la Depuración USB activada.

### Pasos para Ejecutar

1. Abre una terminal y sitúate en la carpeta del proyecto móvil:
   ```bash
   cd mobile
   ```

2. Descarga y actualiza los paquetes y dependencias del proyecto:
   ```bash
   flutter pub get
   ```

3. Lanza la aplicación en tu emulador o dispositivo conectado:
   ```bash
   flutter run
   ```

> [!NOTE]
> **Dirección de la API local en Emuladores:**
> * Si usas el **Emulador de Android**, recuerda que accede al servidor local de Django usando la IP especial de puente **`http://10.0.2.2:8000/`**.
> * Si usas el **Simulador de iOS** o ejecutas en la web, la dirección estándar es **`http://localhost:8000/`**.
> * Asegúrate de que el backend de Django esté corriendo antes de iniciar la app móvil.
