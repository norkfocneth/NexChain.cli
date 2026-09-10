@echo off
REM NexChain CLI Windows Batch Launcher
set SCRIPT_DIR=%~dp0
"%SCRIPT_DIR%.venv\Scripts\python.exe" "%SCRIPT_DIR%nexchain.py" %*
