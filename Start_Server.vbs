Set WinScriptHost = CreateObject("WScript.Shell")
WinScriptHost.Run Chr(34) & "python" & Chr(34) & " " & Chr(34) & "server.py" & Chr(34), 0
Set WinScriptHost = Nothing
