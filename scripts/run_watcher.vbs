Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd.exe /c cd /d D:\_CampusLife\ProjectCampus\6ProjectPribadi\TidyFile && .venv\Scripts\python.exe -m src.main --watch", 0, False
Set WshShell = Nothing
