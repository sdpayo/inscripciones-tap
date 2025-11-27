@echo off
rem Lanzador: usa .venv_build\Scripts\pythonw.exe si existe, si no usa python.exe
setlocal

rem Ruta fija al python del venv (ajustada a tu salida de where)
set "VENV_PYW=C:\Users\GUSTAVO\Documents\inscripciones-tap\.venv_build\Scripts\pythonw.exe"
set "VENV_PY=C:\Users\GUSTAVO\Documents\inscripciones-tap\.venv_build\Scripts\python.exe"

rem Intentar pythonw del venv (sin consola)
if exist "%VENV_PYW%" (
    start "" "%VENV_PYW%" "%~dp0\main.py"
    endlocal
    exit /b 0
)

rem Si no hay pythonw, usar python del venv (mostrará consola)
if exist "%VENV_PY%" (
    start "" "%VENV_PY%" "%~dp0\main.py"
    endlocal
    exit /b 0
)

echo ERROR: No se encontró python en .venv_build\Scripts.
echo Crea el venv con: python -m venv .venv_build
echo Activa y instala dependencias: .venv_build\Scripts\activate && pip install -r requirements.txt
pause
endlocal
exit /b 1