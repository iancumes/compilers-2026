# Entrega del Laboratorio 3 - Opcion D

## Enlaces finales

- Codigo fuente: https://github.com/iancumes/compilers-2026/tree/main/lab-3/option-vercel
- Repositorio generado: https://github.com/iancumes/lab3-sitelang-ian-cumes
- Sitio en produccion: https://lab3-sitelang-ian-cumes.vercel.app
- Video de YouTube: pendiente de grabacion por el estudiante.

## Resultado

SiteLang analiza `program/site.sl` con ANTLR, valida la configuracion mediante
un Listener, genera `index.html`, crea o reutiliza el repositorio publico de
GitHub y publica un deployment de produccion en Vercel. La ejecucion es
idempotente: si el repositorio y el archivo ya existen, se actualizan.

La Parte 1 tambien fue ejecutada con los scripts `curl`. Primero se publico una
pagina de prueba mediante las APIs y despues el compilador la reemplazo por el
sitio final.

## Entregables incluidos

- `program/SiteLang.g4`: gramatica del DSL.
- `program/Driver.py`: punto de entrada y control de errores.
- `program/SiteListener.py`: validacion, generacion de HTML y APIs REST.
- `program/site.sl`: entrada personalizada.
- `program/tests/`: casos valido, sintacticamente invalido y semanticamente invalido.
- `scripts/`: exploracion directa de GitHub y Vercel con `curl`.
- `docs/Informe_Laboratorio_3_Ian_Cumes.docx`: escrito breve editable.
- `docs/Informe_Laboratorio_3_Ian_Cumes.pdf`: version final para entrega.

## Ejecucion verificada

Desde `lab-3/option-vercel`:

```powershell
docker build --rm . -t lab3-vercel
docker run --rm --env-file program/.env -v "${PWD}\program:/program" lab3-vercel `
  bash -lc "antlr -Dlanguage=Python3 -listener SiteLang.g4 && python3 Driver.py site.sl"
```

El archivo `program/.env` es local, esta ignorado por Git y no forma parte de
la entrega.
