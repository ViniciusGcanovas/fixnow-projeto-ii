@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  python -m venv .venv
  if errorlevel 1 goto erro
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto erro
echo Abra http://127.0.0.1:5000 no navegador. Para encerrar, pressione Ctrl+C.
.venv\Scripts\python.exe app.py
pause
exit /b
:erro
echo Nao foi possivel preparar o ambiente. Confira Python e conexao com a internet.
pause
