# 🧪 Laboratorio 3 — Opción D: GitHub + Vercel (✅ 100% Gratuita)

## 📋 Descripción General

En esta opción escribirás un **DSL propio llamado SiteLang** que define la estructura y contenido de un sitio web. Tu compilador — construido con ANTLR — parseará ese archivo, generará HTML, creará un repositorio en GitHub, subirá el código, y desplegará el sitio en Vercel. Al terminar, obtendrás una **URL pública real y accesible desde cualquier lugar del mundo**.

Así es exactamente como funcionan herramientas como **Vercel CLI** y **Netlify CLI** por dentro: parsean un archivo de configuración (que es un DSL), generan un plan, y llaman a APIs REST para desplegar tu aplicación. Tú estás construyendo exactamente ese pipeline, desde cero, con ANTLR.

* **Modalidad: Individual**
* **Costo: $0.00** — No se requiere tarjeta de crédito.

---

## 💰 ¿Por qué esta opción es completamente gratuita?

- **GitHub:** cuenta gratuita, repositorios públicos ilimitados, API gratuita.
- **Vercel:** el plan Hobby (gratuito) permite deployments ilimitados de sitios estáticos, sin expiración y sin tarjeta de crédito.
- No hay instancias de cómputo que generen cargos por hora.

---

## 🧰 Parte 1: Explorar las APIs Directamente con curl

Antes de que ANTLR lo haga por ti, debes llamar a la API de GitHub y la API de Vercel tú mismo usando **curl** desde un contenedor Docker — exactamente igual a como funciona la opción de DigitalOcean con los scripts de Bash.

### 1. Prerequisito: Tener tu `.env`

Completa primero los pasos de "Crear tokens" de la sección siguiente y crea `program/.env`. Los scripts lo leen desde ahí.

### 2. Construir la Imagen

Desde la carpeta `scripts/`:
```bash
docker-compose build
```

### 3. Crear un Repositorio en GitHub vía API

```bash
docker-compose run api-explorer bash create_repo.sh
```

Observa la respuesta JSON de la API de GitHub. Se crea un repo real en tu cuenta.

### 4. Subir un Archivo al Repositorio vía API

```bash
docker-compose run api-explorer bash push_file.sh
```

Esto llama al endpoint `PUT /repos/{owner}/{repo}/contents/{path}` de GitHub para subir `index.html` con un commit — sin `git`, sin `git push`.

### 5. Desplegar a Vercel vía API

```bash
docker-compose run api-explorer bash deploy_to_vercel.sh
```

Esto llama directamente al endpoint `POST /v13/deployments` de Vercel. Observa la URL que se imprime y ábrela en tu navegador.

> 🔍 **Observa lo que pasa:** Tres llamadas `curl`, tres APIs, un sitio publicado en internet. En la Parte 2, tu compilador ANTLR va a leer un archivo `.sl`, generar el HTML, y hacer exactamente estas mismas llamadas de forma automática.

---

## 🤖 Parte 2: Compilador con ANTLR

### 1. Crear tu Personal Access Token de GitHub

1. Crea una cuenta en [github.com](https://github.com) si no tienes una — es gratis.
2. Ve a [github.com/settings/tokens](https://github.com/settings/tokens).
3. Haz clic en **Generate new token (classic)**.
4. Dale un nombre descriptivo (ej. `lab3-compiler`).
5. Selecciona el scope: ✅ **repo** (acceso completo a repositorios).
6. Haz clic en **Generate token** y copia el token — **solo se muestra una vez**.

### 2. Crear tu API Token de Vercel

1. Crea una cuenta en [vercel.com](https://vercel.com) si no tienes una — es gratis. Puedes registrarte con tu cuenta de GitHub.
2. Ve a [vercel.com/account/tokens](https://vercel.com/account/tokens).
3. Haz clic en **Create** y dale un nombre (ej. `lab3-compiler`).
4. Copia el token generado.

### 3. Configurar las Variables de Entorno

Copia el archivo de ejemplo y llena tus tokens:

```bash
cp program/.env.example program/.env
```

Edita `program/.env`:

```
GITHUB_TOKEN=ghp_tuTokenDeGitHubAqui
VERCEL_TOKEN=tuTokenDeVercelAqui
```

> ⚠️ **ADVERTENCIA:** El archivo `program/.env` contiene tus tokens de acceso. Está en `.gitignore` y **nunca debe subirse a GitHub**. Si alguien obtiene tus tokens, puede crear repositorios y deployments en tu nombre.

### 4. Personalizar tu Sitio

Edita `program/site.sl` con tu información. Este archivo es tu **programa** — el input de tu compilador. Cambia el nombre del sitio, título, descripción, y el contenido de la página:

```
site "mi-portfolio" {
  title       = "Tu Nombre — UVG 2026"
  description = "Estudiante de CS construyendo compiladores"
  theme       = "dark"

  page "index" {
    hero    = "Hola, construí este sitio con un compilador que yo escribí"
    about   = "Soy estudiante de la Universidad del Valle de Guatemala..."
    contact = "tu@email.com"
  }
}
```

### 5. Construir la Imagen Docker

Desde el directorio raíz de esta opción (`option-vercel/`), ejecuta:

```bash
docker build --rm . -t lab3-vercel
```

---

## 🔧 Ejecutar el Compilador

Una vez construida la imagen, ejecuta el compilador completo con un solo comando:

```bash
docker run --rm \
  --env-file program/.env \
  -v "$(pwd)/program":/program \
  lab3-vercel bash -c "antlr -Dlanguage=Python3 -listener SiteLang.g4 && python3 Driver.py site.sl"
```

Este comando en un solo paso:
1. Genera el lexer y parser a partir de tu gramática.
2. Parsea tu archivo `site.sl` y construye el árbol sintáctico.
3. El listener recorre el árbol y genera HTML estilizado.
4. Crea un repositorio público en tu cuenta de GitHub.
5. Sube el HTML generado al repositorio.
6. Despliega el repositorio en Vercel vía su API.
7. Imprime la URL pública de tu sitio.

- ✅ Si los tokens son correctos, verás la URL de tu sitio al final.
- ❌ Si hay un error de autenticación, revisa que los valores en `program/.env` sean correctos.

---

## 📤 Salida Esperada

```
[*] Compiling site definition 'mi-portfolio'...
[+] GitHub repo created: https://github.com/tu-usuario/mi-portfolio
[+] index.html pushed to GitHub
[✓] Deployed to Vercel: https://mi-portfolio-abc123.vercel.app

[✓] Done! Your compiler just deployed a live website.
```

Abre la URL de Vercel en tu navegador — tu compilador acaba de construir y publicar un sitio web real.

---

## 📁 Estructura de Archivos

```
option-vercel/
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
├── python-venv.sh
├── commands/
│   ├── antlr
│   └── grun
└── program/
    ├── SiteLang.g4       # La gramática ANTLR — el corazón del DSL
    ├── Driver.py         # Punto de entrada del compilador
    ├── SiteListener.py   # El listener que genera HTML y despliega
    ├── site.sl           # Tu programa: define el sitio a desplegar (edita esto)
    ├── .env.example      # Plantilla de variables de entorno
    └── .env              # Tus tokens reales (NO subir a GitHub)
```

---

## 📋 Entregables

- **Video de YouTube no listado** mostrando el compilador corriendo, la URL de Vercel siendo impresa, y el sitio abierto en el navegador.
- **Repositorio de GitHub** con tu código fuente. No subas el archivo `.env`.
- **Escrito breve:** explica cómo tu compilador mapea al funcionamiento real de Vercel CLI o Netlify CLI. ¿Qué hace tu listener que es análogo a lo que hacen estas herramientas cuando ejecutas `vercel deploy`?

---

## 🚀 ¿Qué Está Pasando por Dentro?

Cuando ejecutas el compilador, el flujo es:

1. **ANTLR** tokeniza y parsea tu archivo `site.sl` usando la gramática `SiteLang.g4`.
2. El `SiteListener` recorre el árbol sintáctico y extrae título, descripción, tema y contenido.
3. Se genera un archivo `index.html` completo — esto es la **generación de código** de tu compilador.
4. Se llama a la **API de GitHub** para crear un repositorio y subir el HTML.
5. Se llama a la **API de Vercel** para desplegar el archivo directamente.
6. Tu sitio queda vivo en internet en cuestión de segundos.

Esto es exactamente lo que hace **Vercel CLI** cuando ejecutas `vercel deploy`: parsea tu configuración, genera los archivos necesarios, y llama a la misma API que usamos aquí.
