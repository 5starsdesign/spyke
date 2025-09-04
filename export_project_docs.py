# export_project_docs.py
# -*- coding: utf-8 -*-
"""
Genereert een volledige, leesbare documentatie-drop in de map 'mijn project/'.
Draai dit script vanuit je Django project-root (waar manage.py staat).
Docker:  docker compose exec web python export_project_docs.py
Lokaal : python export_project_docs.py

Reminder: maak eerst een backup van code en database.
"""

from __future__ import annotations

import os
import sys
import re
import json
import platform
import textwrap
from pathlib import Path
from datetime import datetime

# --------------------------- Basis setup --------------------------------------

BASE_DIR = Path(__file__).resolve().parent
MANAGE_PY = BASE_DIR / "manage.py"
if not MANAGE_PY.exists():
    print("❌ manage.py niet gevonden. Draai het script in dezelfde map als manage.py.")
    sys.exit(1)

# Kies settings module: gebruik env of val terug op 'config.settings' of 'project.settings'
DJANGO_SETTINGS_CANDIDATES = [
    os.getenv("DJANGO_SETTINGS_MODULE"),
    "config.settings",
    "project.settings",
    "settings",
]
for candidate in DJANGO_SETTINGS_CANDIDATES:
    if candidate:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", candidate)
        break

# Django bootstrappen
try:
    import django  # type: ignore
    django.setup()
except Exception as e:
    print("❌ Django kon niet initialiseren. Zet DJANGO_SETTINGS_MODULE goed of installeer dependencies.")
    print(f"   Fout: {e}")
    sys.exit(1)

from django import get_version as django_version  # type: ignore
from django.apps import apps  # type: ignore
from django.conf import settings  # type: ignore
from django.db import connection  # type: ignore
from django.urls import get_resolver, URLPattern, URLResolver  # type: ignore
from django.db.migrations.executor import MigrationExecutor  # type: ignore
from django.db.models import NOT_PROVIDED  # type: ignore

# --------------------------- Uitvoer map --------------------------------------

OUT_DIR = BASE_DIR / "mijn project"   # met spatie, zoals gevraagd
OUT_DIR.mkdir(parents=True, exist_ok=True)

def wfile(name: str, content: str) -> Path:
    p = OUT_DIR / name
    # Force LF en UTF-8
    p.write_text(content.replace("\r\n", "\n"), encoding="utf-8")
    return p

def header(t: str) -> str:
    return f"{t}\n{'=' * len(t)}\n"

# --------------------------- Masking & JSON helpers ---------------------------

MASK_KEYS = ("SECRET", "PASSWORD", "TOKEN", "KEY", "PRIVATE", "API", "AWS", "GCP", "AZURE")

def _mask_key(k) -> bool:
    k_up = str(k).upper()
    return any(m in k_up for m in MASK_KEYS)

def mask(value):
    """Maak objecten JSON-serialiseerbaar en maskeer gevoelige waarden."""
    from types import MappingProxyType
    if value is None:
        return None
    # Primitieven
    if isinstance(value, (str, int, float, bool)):
        return value
    # Path -> str
    if isinstance(value, Path):
        return str(value)
    # dict-achtig
    if isinstance(value, (dict, MappingProxyType)):
        out = {}
        for k, v in value.items():
            out[str(k)] = "*** MASKED ***" if _mask_key(k) else mask(v)
        return out
    # iterabelen
    if isinstance(value, (list, tuple, set, frozenset)):
        return [mask(x) for x in value]
    # Django/lazy objecten en overige -> str
    try:
        return str(value)
    except Exception:
        return repr(value)

def dumps_pretty(obj) -> str:
    return json.dumps(mask(obj), indent=2, ensure_ascii=False, default=str)

# --------------------------- 0) Overzicht -------------------------------------

def build_overview() -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        header("Projectoverzicht"),
        f"Timestamp        : {now}",
        f"Python           : {platform.python_version()} ({platform.python_implementation()})",
        f"Django           : {django_version()}",
        f"DJANGO_SETTINGS  : {os.environ.get('DJANGO_SETTINGS_MODULE')}",
        f"DEBUG            : {getattr(settings, 'DEBUG', None)}",
        f"ALLOWED_HOSTS    : {', '.join(getattr(settings, 'ALLOWED_HOSTS', []) or [])}",
        f"Time zone        : {getattr(settings, 'TIME_ZONE', None)}",
        f"Language code    : {getattr(settings, 'LANGUAGE_CODE', None)}",
        "",
        header("Apps (INSTALLED_APPS)"),
    ]
    for a in settings.INSTALLED_APPS:
        lines.append(f"- {a}")
    lines.append("")
    return "\n".join(lines)

# --------------------------- 1) Settings (geschoond) --------------------------

SETTINGS_KEYS_CORE = [
    "DEBUG", "ALLOWED_HOSTS", "DATABASES", "CACHES", "EMAIL_BACKEND", "EMAIL_HOST",
    "STATIC_URL", "STATIC_ROOT", "STATICFILES_DIRS", "MEDIA_URL", "MEDIA_ROOT",
    "TEMPLATES", "MIDDLEWARE", "AUTH_USER_MODEL", "SITE_ID", "LANGUAGE_CODE",
    "TIME_ZONE", "ROOT_URLCONF",
]
SETTINGS_KEYS_EXTRA = [
    "REST_FRAMEWORK", "CORS_ALLOWED_ORIGINS", "CSRF_TRUSTED_ORIGINS",
    "SOCIALACCOUNT_PROVIDERS", "LOGIN_REDIRECT_URL", "ACCOUNT_EMAIL_REQUIRED",
    "ACCOUNT_EMAIL_VERIFICATION", "SECURE_PROXY_SSL_HEADER", "USE_X_FORWARDED_HOST",
]

def build_settings() -> str:
    data = {}
    for key in SETTINGS_KEYS_CORE + SETTINGS_KEYS_EXTRA:
        if hasattr(settings, key):
            data[key] = getattr(settings, key)
    # Voeg custom settings toe die ALL CAPS zijn (excl. interne Django dingen)
    for key in dir(settings):
        if not key.isupper():
            continue
        if key in data:
            continue
        if key.startswith("_"):
            continue
        try:
            val = getattr(settings, key)
            # Sla grote/onnodige objecten over
            if key in ("LOGGING_CONFIG", "WSGI_APPLICATION", "ASGI_APPLICATION"):
                continue
            data[key] = val
        except Exception:
            pass

    return header("Settings (geschoond)") + dumps_pretty(data) + "\n"

# --------------------------- 2) URL’s / routes --------------------------------

def build_urls() -> str:
    resolver = get_resolver()
    rows = [header("URL’s & routes")]

    def walk(patterns, prefix=""):
        for p in patterns:
            if isinstance(p, URLPattern):
                route = prefix + str(p.pattern)
                cb = p.callback
                name = p.name or ""
                view_obj = getattr(cb, "view_class", cb)
                view = f"{getattr(view_obj, '__module__', '')}.{getattr(view_obj, '__name__', getattr(view_obj, '__class__', type(view_obj)).__name__)}".strip(".")
                methods = ""
                if hasattr(cb, "view_class"):
                    hm = getattr(cb.view_class, "http_method_names", None)
                    if hm:
                        methods = ",".join(hm)
                rows.append(f"{route:50}  name={name:25}  view={view}  methods=[{methods}]")
            elif isinstance(p, URLResolver):
                walk(p.url_patterns, prefix + str(p.pattern))

    try:
        walk(resolver.url_patterns, "")
    except Exception as e:
        rows.append(f"[Fout bij uitlezen urls]: {e}")

    return "\n".join(rows) + "\n"

# --------------------------- 3) Views -----------------------------------------

def build_views() -> str:
    resolver = get_resolver()
    found = {}

    def walk(patterns):
        for p in patterns:
            if isinstance(p, URLPattern):
                cb = p.callback
                view_obj = getattr(cb, "view_class", cb)
                key = f"{getattr(view_obj, '__module__', '')}.{getattr(view_obj, '__name__', getattr(view_obj, '__class__', type(view_obj)).__name__)}".strip(".")
                if key not in found:
                    doc = (getattr(view_obj, "__doc__", "") or "").strip()
                    doc = textwrap.shorten(re.sub(r"\s+", " ", doc), width=300, placeholder="…") if doc else ""
                    methods = ""
                    if hasattr(cb, "view_class"):
                        hm = getattr(cb.view_class, "http_method_names", None)
                        if hm:
                            methods = ",".join(hm)
                    found[key] = {"doc": doc, "methods": methods}
            elif isinstance(p, URLResolver):
                walk(p.url_patterns)

    try:
        walk(resolver.url_patterns)
    except Exception:
        pass

    lines = [header("Views (afgeleid uit URL’s)")]
    for k in sorted(found.keys()):
        d = found[k]
        lines.append(f"{k}\n  methods: [{d['methods']}]\n  doc   : {d['doc']}\n")
    return "\n".join(lines)

# --------------------------- 4) Models & velden -------------------------------

def build_models() -> str:
    lines = [header("Models & velden")]
    for model in sorted(apps.get_models(), key=lambda m: f"{m._meta.app_label}.{m.__name__}"):
        meta = model._meta
        lines.append(f"{meta.app_label}.{model.__name__}  (db_table={meta.db_table})")
        for f in meta.get_fields():
            try:
                base = f"{f.name}: {f.__class__.__name__}"
                extras = []
                if hasattr(f, "null"):
                    extras.append(f"null={getattr(f, 'null')}")
                if hasattr(f, "blank"):
                    extras.append(f"blank={getattr(f, 'blank')}")
                if getattr(f, "primary_key", False):
                    extras.append("primary_key=True")
                if getattr(f, "unique", False):
                    extras.append("unique=True")
                rel = getattr(f, "remote_field", None)
                if rel and getattr(rel, "model", None):
                    target = getattr(rel.model, "__name__", str(rel.model))
                    extras.append(f"to={target}")
                default = getattr(f, "default", None)
                if default not in (None, NOT_PROVIDED):
                    extras.append(f"default={default!r}")
                lines.append(f"  - {base}  ({', '.join(extras)})")
            except Exception as e:
                lines.append(f"  - {getattr(f, 'name', '?')}: <error: {e}>")
        lines.append("")
    return "\n".join(lines)

# --------------------------- 5) Migrations status -----------------------------

def build_migrations() -> str:
    lines = [header("Migrations status")]
    try:
        executor = MigrationExecutor(connection)
        applied = set(executor.loader.applied_migrations)
        graph = executor.loader.graph
        per_app = {}
        for node in graph.nodes:
            app_label, name = node
            per_app.setdefault(app_label, []).append((name, (app_label, name) in applied))
        for app_label in sorted(per_app):
            lines.append(f"{app_label}:")
            for name, ok in sorted(per_app[app_label]):
                lines.append(f"  [{'X' if ok else ' '}] {name}")
            lines.append("")
    except Exception as e:
        lines.append(f"[Fout bij uitlezen migrations]: {e}")
    return "\n".join(lines)

# --------------------------- 6) Templates index -------------------------------

def build_templates_index() -> str:
    lines = [header("Templates index")]
    template_dirs = []
    for cfg in getattr(settings, "TEMPLATES", []):
        template_dirs.extend(cfg.get("DIRS", []))
    for app_config in apps.get_app_configs():
        p = Path(app_config.path) / "templates"
        if p.exists():
            template_dirs.append(p)
    seen = set()
    for d in map(Path, template_dirs):
        if not d.exists():
            continue
        lines.append(f"Dir: {d}")
        for f in sorted(d.rglob("*.html")):
            rel_str = str(f)
            if rel_str in seen:
                continue
            seen.add(rel_str)
            try:
                first_k = ""
                with f.open("r", encoding="utf-8", errors="ignore") as fh:
                    head = fh.read(2048)
                    m = re.search(r"{%\s*extends\s+['\"]([^'\"]+)['\"]\s*%}", head)
                    if m:
                        first_k = f" (extends: {m.group(1)})"
                lines.append(f"  - {rel_str}{first_k}")
            except Exception:
                lines.append(f"  - {rel_str}")
        lines.append("")
    return "\n".join(lines)

# --------------------------- 7) Projectboom (tree) ----------------------------

EXCLUDE_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", "node_modules", ".venv", "venv", "env",
    "media", "staticfiles", ".mypy_cache", ".pytest_cache", ".idea", ".vscode",
}

INCLUDE_SUFFIXES = {".py", ".html", ".txt", ".md", ".json", ".yml", ".yaml", ".ini", ".env", ".cfg"}

CORE_FILES = {"Dockerfile", "docker-compose.yml", "requirements.txt", "manage.py"}

def build_tree() -> str:
    lines = [header("Projectboom")]
    def is_excluded(p: Path) -> bool:
        return any(part in EXCLUDE_DIRS for part in p.parts)

    for root, dirs, files in os.walk(BASE_DIR):
        r = Path(root)
        if is_excluded(r):
            dirs[:] = []
            continue
        rel_parts = r.relative_to(BASE_DIR).parts
        indent = "  " * len(rel_parts)
        if r != BASE_DIR:
            lines.append(f"{indent}{r.name}/")
        dirs[:] = sorted([d for d in dirs if not is_excluded(Path(root) / d)])
        for f in sorted(files):
            if f == Path(__file__).name:
                continue
            fp = Path(root) / f
            if fp.suffix.lower() in INCLUDE_SUFFIXES or f in CORE_FILES:
                fin = "  " * (len(fp.relative_to(BASE_DIR).parts) - 1)
                size = fp.stat().st_size
                lines.append(f"{fin}├─ {f} ({size} bytes)")
    return "\n".join(lines)

# --------------------------- 8) Requirements ----------------------------------

def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="ignore")

def build_requirements() -> str:
    txt = read_text(BASE_DIR / "requirements.txt")
    if not txt:
        try:
            import pkg_resources  # type: ignore
            txt = "\n".join(sorted(f"{d.project_name}=={d.version}" for d in pkg_resources.working_set))
        except Exception:
            txt = "(geen requirements.txt en pip freeze niet beschikbaar)"
    return header("Requirements") + txt + "\n"

# --------------------------- 9) Docker bundle ---------------------------------

def build_docker_bundle() -> str:
    parts = [header("Docker bundle")]
    for fname in ("Dockerfile", "docker-compose.yml"):
        p = BASE_DIR / fname
        txt = read_text(p)
        if txt:
            parts.append(f"--- {fname} ---\n{txt}\n")
    return "\n".join(parts)

# --------------------------- 10) Management commands --------------------------

def build_management_commands() -> str:
    lines = [header("Custom management commands")]
    any_found = False
    for appcfg in apps.get_app_configs():
        cmd_dir = Path(appcfg.path) / "management" / "commands"
        if cmd_dir.exists():
            cmds = [p.stem for p in cmd_dir.glob("*.py") if p.name not in {"__init__.py"}]
            if cmds:
                any_found = True
                lines.append(f"{appcfg.label}: " + ", ".join(sorted(cmds)))
    if not any_found:
        lines.append("(geen custom commands gevonden)")
    return "\n".join(lines)

# --------------------------- 11) Omgevingsvariabelen --------------------------

def build_env() -> str:
    env = dict(os.environ)
    return header("Proces-omgeving (gemaskeerd)") + dumps_pretty(env) + "\n"

# --------------------------- 12) Database schema ------------------------------

def build_db_schema() -> str:
    lines = [header("Database schema (globaal)")]
    try:
        introspection = connection.introspection
        with connection.cursor() as cursor:
            tables = introspection.table_names(cursor)
        for t in sorted(tables):
            lines.append(f"- {t}")
        lines.append("")
    except Exception as e:
        lines.append(f"[Fout bij introspectie]: {e}")
    return "\n".join(lines)

# --------------------------- Kopieën kernbestanden ----------------------------

def write_core_copies():
    for fname in ("manage.py", "requirements.txt", "Dockerfile", "docker-compose.yml", "README.md"):
        p = BASE_DIR / fname
        txt = read_text(p)
        if txt:
            wfile(f"copy_{fname.replace('/', '_')}.txt", txt)

# --------------------------- Main ---------------------------------------------

def main():
    outputs = {
        "00_overzicht.txt": build_overview(),
        "01_settings.txt": build_settings(),
        "02_urls.txt": build_urls(),
        "03_views.txt": build_views(),
        "04_models.txt": build_models(),
        "05_migrations.txt": build_migrations(),
        "06_templates_index.txt": build_templates_index(),
        "07_projectboom.txt": build_tree(),
        "08_requirements.txt": build_requirements(),
        "09_docker.txt": build_docker_bundle(),
        "10_management_commands.txt": build_management_commands(),
        "11_env.txt": build_env(),
        "12_db_schema.txt": build_db_schema(),
    }

    for name, content in outputs.items():
        wfile(name, content)

    write_core_copies()

    print(f"✅ Documentatie gegenereerd in: {OUT_DIR}")

if __name__ == "__main__":
    main()
