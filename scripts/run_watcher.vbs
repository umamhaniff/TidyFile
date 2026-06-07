Set WshShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
scriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
projectDir = objFSO.GetParentFolderName(scriptDir)
WshShell.Run "cmd.exe /c cd /d """ & projectDir & """ && .venv\Scripts\python.exe -m src.main --watch", 0, False
Set WshShell = Nothing
Set objFSO = Nothing
