@Echo off
:Start
title TS3Client Auto Restart [%date% - %time%]
start /wait "TeamSpeak 3 Client (x64) [Console|Plugins]" /AboveNormal "C:\Program Files\TeamSpeak 3 Client\ts3client_win64.exe" -nosingleinstance -console
SET LAST_TS_ERROR=%ErrorLevel%
set mypath="%AppData%\TS3Client\
REM set log=%tmp%\logs\autorestart.log
call "%~dp0\exit_codes.bat"
setlocal EnableDelayedExpansion
set ERRORMSG=!ERROR_%LAST_TS_ERROR%!
REM echo %ERRORMSG%
echo Program terminated at %Date% %Time% with Error %LAST_TS_ERROR% (%ERRORMSG%)
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
ECHO Cleaning Caches in "%mypath%"...
rmdir /s /q %mypath%crashdumps" >NUL 2>NUL
rmdir /s /q %mypath%logs" >NUL 2>NUL
rmdir /s /q %mypath%chats" >NUL 2>NUL
rmdir /s /q %mypath%cache\UVRSdFBtWWlTS3BNUzhPeWQ0aHl6dGN2THFVPQ==\icons" >NUL 2>NUL
rmdir /s /q %mypath%cache\OVN4NndybFJWNGk5a2xCaVRhbnJrc05GS3ZzPQ==\icons" >NUL 2>NUL
rmdir /s /q %mypath%cache\remote" >NUL 2>NUL
rmdir /s /q %mypath%cache\qtwebengine_cache" >NUL 2>NUL
rmdir /s /q %mypath%cache\qtwebengine_persistant_storage" >NUL 2>NUL
del /s /q %mypath%cache\subscription_mode_storage.dat" >NUL 2>NUL
del /s /q %mypath%cache\subscribed_channels_storage.dat" >NUL 2>NUL
del /s /q %mypath%cache\license_2_en.html" >NUL 2>NUL
del /s /q "C:\Program Files\TeamSpeak 3 Client\error_report.exe" >NUL 2>NUL
FOR /F "tokens=*" %%G IN ('DIR /B /AD /S *__pycache__*') DO RMDIR /S /Q %%G >NUL 2>NUL
:REPEAT
goto Start