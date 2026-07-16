# Entrega del Laboratorio 1

## Contenido

- `program/MiniLang.g4`: gramática combinada de ANTLR para MiniLang.
- `program/Driver.py`: driver con validación de argumentos, reporte de errores y códigos de salida.
- `program/program_test.txt`: caso válido base.
- `program/program_test_precedence.txt`: caso válido con precedencia y paréntesis.
- `program/program_test_invalid.txt`: caso inválido con errores léxicos y sintácticos intencionales.
- `Analisis_Gramatica_y_Driver.docx`: análisis solicitado de la gramática y el driver.

## Ejecución rápida con Docker

Desde `lab-1`:

```bash
docker build --rm . -t lab1-image
docker run --rm -v "$(pwd)/program:/program" lab1-image sh -lc \
  "antlr -Dlanguage=Python3 MiniLang.g4 && python3 Driver.py program_test.txt"
```

Para ejecutar los tres casos en un contenedor interactivo:

```bash
docker run --rm -it -v "$(pwd)/program:/program" lab1-image
antlr -Dlanguage=Python3 MiniLang.g4
python3 Driver.py program_test.txt
python3 Driver.py program_test_precedence.txt
python3 Driver.py program_test_invalid.txt
```

El driver devuelve `0` si la entrada es válida, `1` si encuentra errores léxicos o sintácticos y `2` si el uso del programa o la ruta del archivo son incorrectos.
