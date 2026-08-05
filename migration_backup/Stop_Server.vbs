Set WinScriptHost = CreateObject("WScript.Shell")
WinScriptHost.Run "taskkill /f /im python.exe /fi ""WINDOWTITLE eq ABIRs Downloader*""", 0, True
Set WinScriptHost = Nothing
