# Laboratorio 3 - Opcion D: GitHub + Vercel

Este laboratorio implementa **SiteLang**, un DSL pequeño que describe un sitio
estatico. ANTLR genera el lexer y el parser; un Listener valida la configuracion,
genera `index.html`, actualiza un repositorio publico mediante la API de GitHub y
crea un deployment de produccion mediante la API REST de Vercel.

El proyecto esta preparado para ejecutarse varias veces. Si el repositorio o el
archivo ya existen, se reutilizan y actualizan en lugar de crear duplicados.

## Requisitos

- Docker Desktop en ejecucion.
- Cuenta de GitHub autenticada como `iancumes`.
- Cuenta de Vercel vinculada a GitHub.
- Tokens locales en `program/.env`. Este archivo esta ignorado por Git.

Crear el archivo local a partir de la plantilla:

```powershell
Copy-Item program/.env.example program/.env
```

Variables disponibles:

```text
GITHUB_TOKEN=...
VERCEL_TOKEN=...
VERCEL_TEAM_ID=...   # opcional cuando el proyecto pertenece a un equipo
```

Nunca se deben incluir estos valores en commits, capturas o videos.

## Parte 1: explorar las APIs con curl

Desde `lab-3/option-vercel/scripts`:

```powershell
docker compose build
docker compose run --rm api-explorer bash create_repo.sh
docker compose run --rm api-explorer bash push_file.sh
docker compose run --rm api-explorer bash deploy_to_vercel.sh
```

Los scripts crean o reutilizan `iancumes/lab3-sitelang-ian-cumes`, publican una
pagina de prueba y crean un deployment en Vercel. El archivo
`repo_full_name.txt` es estado local y no se versiona.

## Parte 2: compilar SiteLang

Desde `lab-3/option-vercel` construir la imagen:

```powershell
docker build --rm . -t lab3-vercel
```

Validar la entrada y generar HTML sin usar APIs externas:

```powershell
docker run --rm --env-file program/.env -v "${PWD}\program:/program" lab3-vercel `
  bash -lc "antlr -Dlanguage=Python3 -listener SiteLang.g4 && python3 Driver.py site.sl --dry-run"
```

Ejecutar el flujo completo:

```powershell
docker run --rm --env-file program/.env -v "${PWD}\program:/program" lab3-vercel `
  bash -lc "antlr -Dlanguage=Python3 -listener SiteLang.g4 && python3 Driver.py site.sl"
```

La salida local queda en `program/generated/index.html`. Una ejecucion completa
tambien imprime el repositorio generado, el archivo publicado y la URL de
produccion de Vercel.

## Estructura del DSL

```text
site "nombre-del-proyecto" {
  title       = "Titulo"
  description = "Descripcion"
  theme       = "dark"
  author      = "Nombre"
  course      = "Curso"
  repository  = "https://github.com/usuario/repositorio"

  page "index" {
    hero        = "Mensaje principal"
    about       = "Descripcion del proyecto"
    stack       = "Tecnologias"
    contact     = "Etiqueta del enlace"
    contact_url = "https://github.com/usuario"
  }
}
```

El compilador rechaza atributos desconocidos, nombres que no son slugs, temas
distintos de `light` o `dark`, URLs no seguras y entradas sin la pagina
`index`. Si hay un error lexico, sintactico o semantico, termina antes de llamar
a GitHub o Vercel.

## Pruebas

Las pruebas incluidas cubren una compilacion valida, un error sintactico, un
error semantico y credenciales ausentes. Dentro del contenedor:

```bash
antlr -Dlanguage=Python3 -listener SiteLang.g4
python3 -m unittest discover -s tests -v
```

Codigos de salida del driver:

- `0`: compilacion o deployment exitoso.
- `1`: error lexico, sintactico, semantico o de API.
- `2`: uso incorrecto, archivo inexistente o credenciales ausentes.

## Archivos principales

- `program/SiteLang.g4`: gramatica combinada del DSL.
- `program/Driver.py`: coordinacion del lexer, parser, Listener y deployment.
- `program/SiteListener.py`: validacion, generacion de HTML y clientes REST.
- `program/site.sl`: sitio personalizado de la entrega.
- `scripts/`: exploracion directa de las APIs con `curl`.
- `docs/`: informe breve en Word y PDF.
- `ENTREGA.md`: enlaces y resumen final de la entrega.
