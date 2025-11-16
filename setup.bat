@echo off
echo === Creando estructura del proyecto ===

REM Carpetas principales
mkdir config
mkdir models
mkdir database
mkdir ui
mkdir services
mkdir utils

REM Archivos __init__.py
echo. 2> config\__init__.py
echo. 2> models\__init__.py
echo. 2> database\__init__.py
echo. 2> ui\__init__.py
echo. 2> services\__init__.py
echo. 2> utils\__init__.py

REM Git
git init

echo.
echo ✅ Estructura creada exitosamente
echo.
echo Ahora copié manualmente tu archivo:
echo   inscripcion_tk_1.96_2.py --> inscripcion_original.py
echo.
pause