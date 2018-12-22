@Echo off
:Start
start /wait "TeamSpeak 3 Client (x64)" /AboveNormal "C:\Program Files\TeamSpeak 3 Client\ts3client_win64.exe" -nosingleinstance -console
set mypath="%AppData%\TS3Client\
set log=%tmp%\logs\autorestart.log
echo Program terminated at %Date% %Time% with Error %ErrorLevel%
echo Program terminated at %Date% %Time% with Error %ErrorLevel% 1>> %log% 2>>&1
FOR /F "eol=| delims=" %%I IN ('DIR %mypath%logs\*.log" /A-D /B /O-D /TW 2^>nul') DO (
    SET NewestFile=%%I
    GOTO FoundFile
)
ECHO No logs found!
GOTO CLEAN
:FoundFile
set NewestFile=%mypath%logs\%NewestFile%"
ECHO Last log: %NewestFile%
ECHO ...
powershell -command "& {Get-Content %NewestFile% | Select-Object -last 15}"
:CLEAN
REM start /wait cmd.exe /c "C:\Users\blusc\AppData\Roaming\TS3Client\tools\ts_clear_cache.bat"
cd %mypath%"
rmdir /s /q %mypath%crashdumps"
rmdir /s /q %mypath%logs"
rmdir /s /q %mypath%chats"
rmdir /s /q %mypath%cache\UVRSdFBtWWlTS3BNUzhPeWQ0aHl6dGN2THFVPQ==\icons"
rmdir /s /q %mypath%cache\OVN4NndybFJWNGk5a2xCaVRhbnJrc05GS3ZzPQ==\icons"
rmdir /s /q %mypath%cache\remote"
rmdir /s /q %mypath%cache\qtwebengine_cache"
rmdir /s /q %mypath%cache\qtwebengine_persistant_storage"
del /s /q %mypath%cache\subscription_mode_storage.dat"
del /s /q %mypath%cache\subscribed_channels_storage.dat"
del /s /q %mypath%cache\license_2_en.html"
del /s /q "C:\Program Files\TeamSpeak 3 Client\error_report.exe"
FOR /F "tokens=*" %%G IN ('DIR /B /AD /S *__pycache__*') DO RMDIR /S /Q %%G
:REPEAT
goto Start