# 🧪 Laboratorio 3 — Opción C: GCP Compute Engine con ANTLR + google-cloud-compute

## 📋 Descripción General

En esta opción escribirás una **gramática ANTLR** para un DSL de infraestructura similar a Terraform. El parser generará un árbol sintáctico, y el listener recorrerá ese árbol para llamar a la **API de Compute Engine de Google Cloud** usando `google-cloud-compute`, creando una VM real en la nube.

Así es exactamente como funciona Terraform por dentro: parsea archivos `.tf`, construye un plan de ejecución, y llama a las APIs de cada proveedor para crear la infraestructura declarada. Tú estás construyendo una versión simplificada de ese mismo pipeline.

* **Modalidad: Individual**

---

## 💰 Opciones de Costo

- **GCP Free Trial:** las cuentas nuevas de Google Cloud reciben **$300 USD de crédito por 90 días**. Requiere tarjeta de crédito para verificación de identidad, pero no se realiza ningún cobro automático al terminar el período de prueba.
- **Créditos estudiantiles:** disponibles via [Google Cloud for Students](https://cloud.google.com/edu/students). Consulta con tu catedrático si la universidad tiene convenio.
- **Free Tier permanente:** la instancia `e2-micro` es elegible para el free tier de GCP — **1 instancia por mes sin costo** en las regiones `us-west1`, `us-central1`, y `us-east1`.
- **Tu propio dinero:** `e2-micro` cuesta aproximadamente $0.0084/hora. Si la eliminas de inmediato, el costo es mínimo.

---

## 🧰 Parte 1: Explorar la API de GCP Directamente

Antes de que ANTLR lo haga por ti, debes llamar a la API de Compute Engine tú mismo usando **gcloud CLI** desde un contenedor Docker. Esto te permite entender exactamente qué operación está automatizando el compilador.

### 1. Prerequisito: Tener `credentials.json`

Completa primero los pasos de "Crear una Cuenta de Servicio" de la sección siguiente y coloca tu `credentials.json` en la carpeta `program/`. Los scripts lo necesitan.

### 2. Configurar el Contenedor

Edita `scripts/docker-compose.yml` y reemplaza los placeholders:

```yaml
environment:
  - GCP_PROJECT=TU_PROJECT_ID
  - GCP_ZONE=us-central1-a
```

### 3. Construir la Imagen

Desde la carpeta `scripts/`:
```bash
docker-compose build
```

### 4. Crear la Instancia Directamente

```bash
docker-compose run gcp bash create_instance.sh
```

Observa la respuesta de la API: nombre, estado, zona.

### 5. Eliminar la Instancia

```bash
docker-compose run gcp bash delete_instance.sh
```

> 🔍 **Observa lo que pasa:** Estás llamando a `gcloud compute instances create` y `delete` directamente. En la Parte 2, tu compilador ANTLR va a hacer lo mismo, pero leyendo los parámetros desde un archivo de infraestructura.

---

## 🤖 Parte 2: Parser con ANTLR

### 1. Crear una Cuenta de Servicio en GCP

1. Ve a la [consola de Google Cloud](https://console.cloud.google.com).
2. Crea un proyecto nuevo o selecciona uno existente. Anota el **Project ID**.
3. Navega a **IAM & Admin → Service Accounts**.
4. Haz clic en **Create Service Account**.
5. Dale un nombre descriptivo (ej. `lab3-compiler`) y haz clic en **Create and continue**.
6. Asigna el rol **Compute Admin** y haz clic en **Done**.
7. Haz clic en la cuenta de servicio creada → **Keys → Add Key → Create new key → JSON**.
8. Descarga el archivo JSON y colócalo en la carpeta `program/` con el nombre `credentials.json`.

> ⚠️ **ADVERTENCIA:** Nunca subas `credentials.json` a GitHub. Este archivo está en `.gitignore` por esa razón.

### 2. Configurar el Archivo de Infraestructura

Edita `program/infra.gcp` y reemplaza el Project ID:

```
variable "gcp_project" {
  default = "TU_PROJECT_ID_AQUI"
}
```

El Project ID lo encuentras en la consola de GCP en la pantalla de inicio: **Home → Dashboard → Project info → Project ID**.

### 3. Construir y Ejecutar el Contenedor Docker

Desde el directorio raíz de esta opción (`option-gcp/`), ejecuta:

```bash
docker build --rm . -t lab3-gcp && docker run --rm -ti -v "$(pwd)/program":/program lab3-gcp
```

---

## 🔧 Dentro del Contenedor

Una vez dentro del contenedor interactivo, ejecuta los pasos en orden:

**Paso 1 — Generar el lexer y parser con ANTLR:**
```bash
antlr -Dlanguage=Python3 -listener InfraLang.g4
```

**Paso 2 — Ejecutar el compilador:**
```bash
python3 Driver.py infra.gcp
```

- ✅ Si las credenciales son correctas, verás el nombre de la instancia creada en GCP.
- ❌ Si hay un error de autenticación, verifica que `credentials.json` esté en la carpeta `program/` y que el Project ID sea correcto.

---

## 📤 Salida Esperada

```
[var] gcp_project = tu-proyecto-123
[var] gcp_zone = us-central1-a
[var] gcp_credentials_file = credentials.json
[*] Loading GCP credentials from credentials.json...
[*] Creating GCP instance 'my-web-server' (e2-micro) in us-central1-a...
[✓] Instance 'my-web-server' created in project 'tu-proyecto-123', zone 'us-central1-a'.
[!] Remember to delete it to avoid charges.
```

---

## 🚨 IMPORTANTE: Eliminar la Instancia

Después de verificar que el laboratorio funciona, **elimina la instancia para evitar cargos**. Puedes hacerlo desde la consola de GCP:

**Compute Engine → VM instances → selecciona la instancia → Delete**

O con el SDK de gcloud:

```bash
gcloud compute instances delete my-web-server --zone=us-central1-a --project=TU_PROJECT_ID
```

---

## 📁 Estructura de Archivos

```
option-gcp/
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
├── python-venv.sh
├── commands/
│   ├── antlr
│   └── grun
└── program/
    ├── InfraLang.g4          # La gramática ANTLR — el corazón del DSL
    ├── Driver.py             # Punto de entrada del compilador
    ├── GCPInfraListener.py   # El listener que llama a la API de GCP
    ├── infra.gcp             # Tu programa en el DSL (edita esto)
    └── credentials.json      # Tu service account key (NO subir a GitHub)
```

---

## 📋 Entregables

- **Video de YouTube no listado** mostrando el compilador corriendo y la VM siendo creada en GCP.
- **Repositorio de GitHub** con tu código. No subas `credentials.json` ni ninguna credencial.
- **Escrito breve:** explica cómo tu listener se compara con lo que hace Terraform internamente al ejecutar `terraform apply` en un provider de GCP.
