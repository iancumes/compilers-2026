# 🧪 Laboratorio 3 — Opción B: AWS EC2 con ANTLR + boto3

## 📋 Descripción General

En esta opción escribirás una **gramática ANTLR** para un DSL de infraestructura similar a Terraform. El parser generará un árbol sintáctico, y el listener recorrerá ese árbol para llamar a la **API de EC2 de AWS** usando `boto3`, lanzando una instancia real en la nube.

Así es exactamente como funciona Terraform por dentro: parsea archivos `.tf`, construye un plan de ejecución, y llama a las APIs de cada proveedor para crear la infraestructura declarada. Tú estás construyendo una versión simplificada de ese mismo pipeline.

* **Modalidad: Individual**

---

## 💰 Opciones de Costo

- **AWS Educate / AWS Academy:** si tu universidad tiene convenio con AWS, tienes créditos estudiantiles gratuitos. Consulta con tu catedrático.
- **AWS Free Tier:** las cuentas nuevas de AWS incluyen una instancia `t2.micro` por **12 meses sin costo adicional**. Si nunca has creado una cuenta de AWS, este lab te cuesta $0.
- **Tu propio dinero:** una instancia `t2.micro` cuesta $0.0116/hora. Si la terminas en los primeros minutos tras verificar el lab, el costo total es de centavos.

---

## 🧰 Parte 1: Explorar la API de AWS Directamente

Antes de que ANTLR lo haga por ti, debes llamar a la API de EC2 tú mismo usando la **AWS CLI** desde un contenedor Docker. Esto te permite entender exactamente qué operación está automatizando el compilador.

### 1. Configurar el Contenedor

Edita `scripts/docker-compose.yml` y reemplaza los placeholders con tus credenciales reales:

```yaml
environment:
  - AWS_ACCESS_KEY=TU_ACCESS_KEY_ID
  - AWS_SECRET_KEY=TU_SECRET_ACCESS_KEY
  - AWS_REGION=us-east-1
```

### 2. Construir la Imagen

Desde la carpeta `scripts/`:
```bash
docker-compose build
```

### 3. Crear la Instancia EC2 Directamente

```bash
docker-compose run aws bash create_instance.sh
```

Observa el JSON de respuesta de la API. Guarda el **Instance ID** que se imprime — lo necesitarás para terminarla.

### 4. Terminar la Instancia

```bash
docker-compose run aws bash terminate_instance.sh
```

> 🔍 **Observa lo que pasa:** Estás llamando a `ec2.run-instances` y `ec2.terminate-instances` directamente. En la Parte 2, tu compilador ANTLR va a hacer exactamente lo mismo, pero leyendo los parámetros desde un archivo `.tf`.

---

## 🤖 Parte 2: Parser con ANTLR

### 1. Obtener Credenciales de AWS

1. Inicia sesión en la [consola de AWS](https://console.aws.amazon.com).
2. Haz clic en tu nombre de usuario (esquina superior derecha) → **Security credentials**.
3. En la sección **Access keys**, haz clic en **Create access key**.
4. Guarda el **Access Key ID** y el **Secret Access Key** — solo se muestran una vez.

> ⚠️ **ADVERTENCIA:** Nunca subas estas claves a GitHub. El archivo `infra.aws` usa referencias a variables — rellena los valores en ese archivo pero **no lo incluyas en tu commit**.

### 2. Configurar el Archivo de Infraestructura

Edita `program/infra.aws` y reemplaza los placeholders con tus credenciales reales:

```
variable "aws_access_key" {
  default = "TU_ACCESS_KEY_ID_AQUI"
}

variable "aws_secret_key" {
  default = "TU_SECRET_ACCESS_KEY_AQUI"
}
```

La AMI por defecto (`ami-0c55b159cbfafe1f0`) es Amazon Linux 2 en `us-east-1`. Si cambias la región, busca una AMI válida para esa región en la consola de AWS.

### 3. Construir y Ejecutar el Contenedor Docker

Desde el directorio raíz de esta opción (`option-aws/`), ejecuta:

```bash
docker build --rm . -t lab3-aws && docker run --rm -ti -v "$(pwd)/program":/program lab3-aws
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
python3 Driver.py infra.aws
```

- ✅ Si las credenciales son correctas, verás el ID de la instancia EC2 lanzada.
- ❌ Si hay un error de autenticación, revisa que tus claves en `infra.aws` sean correctas.

---

## 📤 Salida Esperada

```
[var] aws_region = us-east-1
[var] aws_access_key = ****
[var] aws_secret_key = ****
[*] Connecting to AWS (us-east-1)...
[*] Launching EC2 instance 'my-web-server' (t2.micro)...
[✓] EC2 instance launched: i-0abc123def456789
[!] Remember to terminate it: aws ec2 terminate-instances --instance-ids i-0abc123def456789 --region us-east-1
```

---

## 🚨 IMPORTANTE: Terminar la Instancia

Después de verificar que el laboratorio funciona, **termina la instancia para evitar cargos**. Puedes hacerlo desde la consola de AWS:

**EC2 → Instances → selecciona la instancia → Instance State → Terminate instance**

O con el comando que imprime el compilador al finalizar:

```bash
aws ec2 terminate-instances --instance-ids <INSTANCE_ID> --region us-east-1
```

---

## 📁 Estructura de Archivos

```
option-aws/
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── python-venv.sh
├── commands/
│   ├── antlr
│   └── grun
└── program/
    ├── InfraLang.g4         # La gramática ANTLR — el corazón del DSL
    ├── Driver.py            # Punto de entrada del compilador
    ├── AWSInfraListener.py  # El listener que llama a la API de AWS
    └── infra.aws            # Tu programa en el DSL (edita esto)
```

---

## 📋 Entregables

- **Video de YouTube no listado** mostrando el compilador corriendo y la instancia siendo creada en AWS.
- **Repositorio de GitHub** con tu código. No subas tus credenciales de AWS.
- **Escrito breve:** explica cómo tu listener se compara con lo que hace Terraform internamente al ejecutar `terraform apply` en un provider de AWS.
