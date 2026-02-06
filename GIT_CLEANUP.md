# Comandos Git para limpiar archivos sensibles del repositorio

## ⚠️ IMPORTANTE: Lee esto antes de ejecutar

Este archivo contiene comandos para remover archivos sensibles que ya están trackeados en git.
**EJECUTA ESTOS COMANDOS CON CUIDADO** y asegúrate de tener un backup.

## 📋 Paso 1: Verificar qué archivos serán removidos

```bash
# Ver archivos que git debería ignorar pero están trackeados
git ls-files -i --exclude-standard
```

## 🧹 Paso 2: Remover archivos sensibles del historial

### Opción A: Remover solo del índice (mantener archivos localmente)

```bash
# Remover credenciales
git rm --cached credentials.json
git rm --cached smtp_config.json
git rm --cached data/config.json

# Remover datos de usuarios
git rm --cached inscripciones.csv
git rm --cached "InscripcionesTAP - Inscripciones.csv"
git rm --cached data/inscripciones.csv
git rm --cached data/inscripciones_backup.csv
git rm --cached data/inscripciones_sheets.csv
git rm --cached data/inscripciones_sheets_timestamp.txt

# Remover archivos de desarrollo/testing
git rm --cached FINAL_SUMMARY.txt
git rm --cached inscripcion_original.py
git rm --cached config_tab.py
git rm --cached test_sync.py

# Remover certificados generados
git rm --cached -r data/certificates/*.pdf

# Remover __pycache__ si existen
git rm --cached -r **/__pycache__/
```

### Opción B: Remover todo el caché y re-agregar según .gitignore

```bash
# CUIDADO: Esto remueve TODO del índice y re-agrega según .gitignore
git rm -r --cached .
git add .
```

## 💾 Paso 3: Commit los cambios

```bash
git commit -m "🔒 Remover archivos sensibles y actualizar .gitignore"
```

## 🚀 Paso 4: Push al repositorio

```bash
git push origin main
```

## 🗑️ Paso 5: Limpiar historial (OPCIONAL - AVANZADO)

⚠️ **SOLO si necesitas remover archivos sensibles del historial completo**

```bash
# Instalar BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/

# O usar git filter-branch (más lento)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch credentials.json" \
  --prune-empty --tag-name-filter cat -- --all

# Forzar push (CUIDADO: reescribe historial)
git push origin --force --all
```

## ✅ Verificar que funcionó

```bash
# Verificar archivos trackeados
git ls-files

# No deberías ver:
# - credentials.json
# - data/config.json
# - inscripciones*.csv
# - __pycache__/
```

## 📝 Notas

- Los archivos permanecen en tu PC, solo se remueven del repositorio git
- Archivos `.example` SÍ deben estar en el repo como plantillas
- Después de hacer push, otros colaboradores deben hacer:
  ```bash
  git pull
  ```
