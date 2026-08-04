Set WinScriptHost = CreateObject("WScript.Shell")
WinScriptHost.Run "cmd /c python server.py", 0
Set WinScriptHost = Nothing
