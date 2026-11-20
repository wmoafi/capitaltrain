Set WshShell = CreateObject("WScript.Shell")
' Run Watchdog which automatically monitors and keeps both WebServer and TelegramBot alive forever
WshShell.Run "cmd /c ""cd /d I:\CapitalTrain && set PYTHONIOENCODING=utf-8 && ""C:\Python314\python.exe"" watchdog.py""", 0, False
