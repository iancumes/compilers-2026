import base64
import html
import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

from SiteLangListener import SiteLangListener


class DeploymentError(RuntimeError):
    pass


class SiteDeployListener(SiteLangListener):
    SITE_ATTRIBUTES = {"title", "description", "theme", "author", "course", "repository"}
    PAGE_ATTRIBUTES = {"hero", "about", "stack", "contact", "contact_url"}
    REQUIRED_SITE_ATTRIBUTES = {"title", "description", "theme", "author", "repository"}
    REQUIRED_INDEX_ATTRIBUTES = {"hero", "about"}
    REQUEST_TIMEOUT = 30
    VERCEL_POLL_ATTEMPTS = 45
    VERCEL_POLL_SECONDS = 2

    def __init__(self, github_token="", vercel_token="", vercel_team_id=""):
        self.github_token = github_token
        self.vercel_token = vercel_token
        self.vercel_team_id = vercel_team_id
        self.site_name = ""
        self.site_attrs = {}
        self.pages = {}
        self._current_page = None
        self._errors = []
        self.session = requests.Session()

    @staticmethod
    def _expression_value(ctx):
        text = ctx.getText()
        if ctx.STRING() is not None:
            return json.loads(text)
        if ctx.NUMBER() is not None:
            return float(text) if "." in text else int(text)
        return text == "true"

    def enterSite(self, ctx):
        self.site_name = json.loads(ctx.STRING().getText())

    def enterSiteAttr(self, ctx):
        key = ctx.IDENTIFIER().getText()
        if key in self.site_attrs:
            self._errors.append(f"duplicate site attribute '{key}'")
        self.site_attrs[key] = self._expression_value(ctx.expr())

    def enterPage(self, ctx):
        page_name = json.loads(ctx.STRING().getText())
        if page_name in self.pages:
            self._errors.append(f"duplicate page '{page_name}'")
        self._current_page = page_name
        self.pages.setdefault(page_name, {})

    def exitPage(self, ctx):
        self._current_page = None

    def enterPageAttr(self, ctx):
        if self._current_page is None:
            return
        key = ctx.IDENTIFIER().getText()
        page = self.pages[self._current_page]
        if key in page:
            self._errors.append(
                f"duplicate attribute '{key}' in page '{self._current_page}'"
            )
        page[key] = self._expression_value(ctx.expr())

    @staticmethod
    def _valid_https_url(value):
        if not isinstance(value, str):
            return False
        parsed = urlparse(value)
        return parsed.scheme == "https" and bool(parsed.netloc)

    def validate(self):
        errors = list(self._errors)
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,98}[a-z0-9])?", self.site_name):
            errors.append(
                "site name must be a lowercase GitHub/Vercel slug using letters, numbers and hyphens"
            )

        unknown_site = sorted(set(self.site_attrs) - self.SITE_ATTRIBUTES)
        if unknown_site:
            errors.append(f"unknown site attributes: {', '.join(unknown_site)}")

        missing_site = sorted(self.REQUIRED_SITE_ATTRIBUTES - set(self.site_attrs))
        if missing_site:
            errors.append(f"missing site attributes: {', '.join(missing_site)}")

        if self.site_attrs.get("theme") not in {"light", "dark"}:
            errors.append("theme must be either 'light' or 'dark'")

        if not self._valid_https_url(self.site_attrs.get("repository")):
            errors.append("repository must be a valid https URL")

        if "index" not in self.pages:
            errors.append("page 'index' is required")
        else:
            index = self.pages["index"]
            unknown_page = sorted(set(index) - self.PAGE_ATTRIBUTES)
            if unknown_page:
                errors.append(f"unknown index attributes: {', '.join(unknown_page)}")
            missing_index = sorted(self.REQUIRED_INDEX_ATTRIBUTES - set(index))
            if missing_index:
                errors.append(f"missing index attributes: {', '.join(missing_index)}")
            if "contact_url" in index and not self._valid_https_url(index["contact_url"]):
                errors.append("contact_url must be a valid https URL")

        for page_name, attributes in self.pages.items():
            if page_name == "index":
                continue
            unknown = sorted(set(attributes) - self.PAGE_ATTRIBUTES)
            if unknown:
                errors.append(
                    f"unknown attributes in page '{page_name}': {', '.join(unknown)}"
                )
        return errors

    @staticmethod
    def _escape(value):
        return html.escape(str(value), quote=True)

    def _generate_html(self):
        title = self._escape(self.site_attrs["title"])
        description = self._escape(self.site_attrs["description"])
        author = self._escape(self.site_attrs["author"])
        course = self._escape(self.site_attrs.get("course", "Construccion de Compiladores"))
        repository = self._escape(self.site_attrs["repository"])
        theme = self.site_attrs["theme"]

        palette = {
            "dark": {
                "bg": "#07111f",
                "surface": "#0f1f33",
                "card": "#14273e",
                "text": "#e7eef7",
                "muted": "#a9b7c8",
                "accent": "#63e6be",
                "border": "#28425f",
            },
            "light": {
                "bg": "#f5f8fc",
                "surface": "#ffffff",
                "card": "#eef4fa",
                "text": "#17243a",
                "muted": "#52657a",
                "accent": "#087f5b",
                "border": "#d6e0ea",
            },
        }[theme]

        index = self.pages["index"]
        hero = self._escape(index["hero"])
        about = self._escape(index["about"])
        stack = self._escape(index.get("stack", "ANTLR 4 | Python | GitHub REST API | Vercel REST API"))
        contact = self._escape(index.get("contact", "GitHub: iancumes"))
        contact_url = self._escape(index.get("contact_url", self.site_attrs["repository"]))

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{description}" />
  <meta name="author" content="{author}" />
  <title>{title}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{ margin: 0; font-family: Inter, "Segoe UI", system-ui, sans-serif; background: {palette['bg']}; color: {palette['text']}; line-height: 1.65; }}
    a {{ color: {palette['accent']}; }}
    .shell {{ width: min(1040px, calc(100% - 2rem)); margin: 0 auto; }}
    header {{ padding: 5.5rem 0 4rem; background: radial-gradient(circle at 75% 15%, {palette['card']}, {palette['surface']} 52%, {palette['bg']}); border-bottom: 1px solid {palette['border']}; }}
    .eyebrow {{ color: {palette['accent']}; text-transform: uppercase; letter-spacing: .18em; font-size: .78rem; font-weight: 700; }}
    h1 {{ max-width: 850px; margin: .8rem 0 1rem; font-size: clamp(2.25rem, 6vw, 4.5rem); line-height: 1.08; letter-spacing: -.035em; }}
    .lead {{ max-width: 720px; margin: 0; color: {palette['muted']}; font-size: 1.15rem; }}
    .badges {{ display: flex; flex-wrap: wrap; gap: .6rem; margin-top: 1.6rem; }}
    .badge {{ border: 1px solid {palette['border']}; background: {palette['card']}; border-radius: 999px; padding: .35rem .75rem; font-size: .8rem; }}
    main {{ display: grid; gap: 1.25rem; padding: 3rem 0; }}
    section {{ background: {palette['surface']}; border: 1px solid {palette['border']}; border-radius: 18px; padding: clamp(1.5rem, 4vw, 2.4rem); box-shadow: 0 18px 45px rgba(0,0,0,.12); }}
    h2 {{ margin: 0 0 .75rem; color: {palette['accent']}; font-size: 1rem; text-transform: uppercase; letter-spacing: .12em; }}
    p {{ margin: 0; }}
    .pipeline {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: .65rem; margin-top: 1.2rem; }}
    .step {{ padding: .9rem .7rem; text-align: center; border-radius: 12px; background: {palette['card']}; border: 1px solid {palette['border']}; font-size: .85rem; font-weight: 650; }}
    .contact {{ display: inline-block; margin-top: .9rem; font-weight: 700; text-decoration: none; }}
    .contact:hover {{ text-decoration: underline; }}
    footer {{ padding: 2rem 0 3rem; color: {palette['muted']}; text-align: center; font-size: .85rem; }}
    @media (max-width: 720px) {{ .pipeline {{ grid-template-columns: 1fr; }} header {{ padding-top: 4rem; }} }}
  </style>
</head>
<body>
  <header>
    <div class="shell">
      <div class="eyebrow">{course} · Laboratorio 3</div>
      <h1>{hero}</h1>
      <p class="lead">{description}</p>
      <div class="badges"><span class="badge">SiteLang DSL</span><span class="badge">ANTLR Listener</span><span class="badge">Deployment real</span></div>
    </div>
  </header>
  <main class="shell">
    <section>
      <h2>Que construi</h2>
      <p>{about}</p>
    </section>
    <section>
      <h2>Del DSL a produccion</h2>
      <p>El mismo comando analiza la entrada, genera HTML, actualiza GitHub y publica el resultado en Vercel.</p>
      <div class="pipeline"><div class="step">1. SiteLang</div><div class="step">2. ANTLR</div><div class="step">3. Listener</div><div class="step">4. GitHub</div><div class="step">5. Vercel</div></div>
    </section>
    <section>
      <h2>Tecnologias</h2>
      <p>{stack}</p>
      <a class="contact" href="{contact_url}" target="_blank" rel="noreferrer">{contact} →</a>
    </section>
  </main>
  <footer class="shell">{author} · {course} · Generado desde <a href="{repository}" target="_blank" rel="noreferrer">un compilador propio</a></footer>
</body>
</html>
"""

    def compile(self, output_path):
        html_content = self._generate_html()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding="utf-8")
        return html_content

    @staticmethod
    def _error_message(response):
        try:
            payload = response.json()
            error = payload.get("error", payload)
            if isinstance(error, dict):
                return error.get("message") or error.get("code") or response.reason
            return str(error)
        except ValueError:
            return response.reason or f"HTTP {response.status_code}"

    def _github_headers(self):
        return {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _vercel_headers(self):
        return {
            "Authorization": f"Bearer {self.vercel_token}",
            "Content-Type": "application/json",
        }

    def _vercel_params(self):
        return {"teamId": self.vercel_team_id} if self.vercel_team_id else None

    def _create_or_reuse_github_repo(self):
        user_response = self.session.get(
            "https://api.github.com/user",
            headers=self._github_headers(),
            timeout=self.REQUEST_TIMEOUT,
        )
        if not user_response.ok:
            raise DeploymentError(f"GitHub authentication failed: {self._error_message(user_response)}")
        login = user_response.json()["login"]
        full_name = f"{login}/{self.site_name}"

        repo_response = self.session.get(
            f"https://api.github.com/repos/{full_name}",
            headers=self._github_headers(),
            timeout=self.REQUEST_TIMEOUT,
        )
        if repo_response.status_code == 404:
            repo_response = self.session.post(
                "https://api.github.com/user/repos",
                headers=self._github_headers(),
                json={
                    "name": self.site_name,
                    "description": self.site_attrs["description"],
                    "private": False,
                    "auto_init": False,
                },
                timeout=self.REQUEST_TIMEOUT,
            )
            if repo_response.status_code != 201:
                raise DeploymentError(f"GitHub repository creation failed: {self._error_message(repo_response)}")
        elif not repo_response.ok:
            raise DeploymentError(f"GitHub repository lookup failed: {self._error_message(repo_response)}")

        repository = repo_response.json()
        if repository["owner"]["login"].lower() != login.lower():
            raise DeploymentError("Refusing to update a repository owned by another account")
        return full_name, repository["html_url"]

    def _push_html(self, full_name, html_content):
        endpoint = f"https://api.github.com/repos/{full_name}/contents/index.html"
        existing = self.session.get(
            endpoint, headers=self._github_headers(), timeout=self.REQUEST_TIMEOUT
        )
        payload = {
            "message": "Deploy generated SiteLang page",
            "content": base64.b64encode(html_content.encode("utf-8")).decode("ascii"),
            "committer": {
                "name": "iancumes",
                "email": "87866288+iancumes@users.noreply.github.com",
            },
            "author": {
                "name": "iancumes",
                "email": "87866288+iancumes@users.noreply.github.com",
            },
        }
        if existing.status_code == 200:
            payload["sha"] = existing.json()["sha"]
        elif existing.status_code != 404:
            raise DeploymentError(f"GitHub file lookup failed: {self._error_message(existing)}")

        response = self.session.put(
            endpoint,
            headers=self._github_headers(),
            json=payload,
            timeout=self.REQUEST_TIMEOUT,
        )
        if response.status_code not in {200, 201}:
            raise DeploymentError(f"GitHub file update failed: {self._error_message(response)}")
        return response.json()["content"]["html_url"]

    @staticmethod
    def _deployment_url(payload):
        aliases = payload.get("alias") or []
        if isinstance(aliases, str):
            aliases = [aliases]
        hostname = aliases[0] if aliases else payload.get("url")
        return f"https://{hostname}" if hostname else ""

    def _deploy_to_vercel(self, html_content):
        response = self.session.post(
            "https://api.vercel.com/v13/deployments",
            headers=self._vercel_headers(),
            params=self._vercel_params(),
            json={
                "name": self.site_name,
                "files": [{"file": "index.html", "data": html_content}],
                "projectSettings": {"framework": None},
                "target": "production",
            },
            timeout=self.REQUEST_TIMEOUT,
        )
        if not response.ok:
            raise DeploymentError(f"Vercel deployment creation failed: {self._error_message(response)}")

        deployment = response.json()
        deployment_id = deployment.get("id")
        if not deployment_id:
            raise DeploymentError("Vercel response did not include a deployment id")

        for _ in range(self.VERCEL_POLL_ATTEMPTS):
            state = deployment.get("readyState") or deployment.get("state")
            if state == "READY":
                url = self._deployment_url(deployment)
                if not url:
                    raise DeploymentError("Vercel deployment is ready but has no URL")
                return url
            if state in {"ERROR", "CANCELED"}:
                raise DeploymentError(f"Vercel deployment ended in state {state}")
            time.sleep(self.VERCEL_POLL_SECONDS)
            status_response = self.session.get(
                f"https://api.vercel.com/v13/deployments/{deployment_id}",
                headers=self._vercel_headers(),
                params=self._vercel_params(),
                timeout=self.REQUEST_TIMEOUT,
            )
            if not status_response.ok:
                raise DeploymentError(f"Vercel status check failed: {self._error_message(status_response)}")
            deployment = status_response.json()
        raise DeploymentError("Vercel deployment did not become READY within 90 seconds")

    def deploy(self, html_content):
        try:
            full_name, repository_url = self._create_or_reuse_github_repo()
            file_url = self._push_html(full_name, html_content)
            deployment_url = self._deploy_to_vercel(html_content)
        except requests.RequestException as error:
            raise DeploymentError(f"Network request failed: {error}") from error
        return {
            "repository_url": repository_url,
            "file_url": file_url,
            "deployment_url": deployment_url,
        }
