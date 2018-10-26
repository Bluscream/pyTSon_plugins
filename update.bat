C:\Users\blusc\AppData\Roaming\TS3Client\plugins\pyTSon\python.exe -m pip install --upgrade pip
C:\Users\blusc\AppData\Roaming\TS3Client\plugins\pyTSon\python.exe -m pip freeze > requirements.txt
C:\Users\blusc\AppData\Roaming\TS3Client\plugins\pyTSon\python.exe -m pip install -r requirements.txt --upgrade
C:\Users\blusc\AppData\Roaming\TS3Client\plugins\pyTSon\python.exe -m pip install pip-review
C:\Users\blusc\AppData\Roaming\TS3Client\plugins\pyTSon\python.exe -m pip-review --local --interactive
pause
for /F "delims===" %i in ('C:\Users\blusc\AppData\Roaming\TS3Client\plugins\pyTSon\python.exe -m pip freeze -l') do "C:\Users\blusc\AppData\Roaming\TS3Client\plugins\pyTSon\python.exe" -m pip install -U %i
for /F "delims= " %i in ('C:\Users\blusc\AppData\Roaming\TS3Client\plugins\pyTSon\python.exe -m pip list --outdated') do "C:\Users\blusc\AppData\Roaming\TS3Client\plugins\pyTSon\python.exe" -m pip install -U %i
pause