@echo off
echo Installing pyTSon package %* with pip...
python.exe -m pip install %* --target include
echo Installed %*!
pause