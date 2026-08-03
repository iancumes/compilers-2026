# Este archivo es la entrada del compilador SiteLang.
site "lab3-sitelang-ian-cumes" {
  title       = "SiteLang: de un DSL a Vercel"
  description = "Un sitio generado desde un lenguaje propio, publicado en GitHub y desplegado en Vercel con APIs REST."
  theme       = "dark"
  author      = "Ian Cumes"
  course      = "Construccion de Compiladores - UVG 2026"
  repository  = "https://github.com/iancumes/compilers-2026"

  page "index" {
    hero        = "Construí y desplegué este sitio con mi propio compilador"
    about       = "Definí el contenido en SiteLang. ANTLR produjo el lexer y el parser, un Listener generó el HTML y el mismo programa actualizó GitHub antes de crear un deployment real en Vercel."
    stack       = "ANTLR 4 · Python · GitHub REST API · Vercel REST API · Docker"
    contact     = "Ver mi perfil en GitHub"
    contact_url = "https://github.com/iancumes"
  }
}
