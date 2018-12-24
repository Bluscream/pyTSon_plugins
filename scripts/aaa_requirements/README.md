# aaa_requirements pyTSon script

This is a library that can be used to load [requirements.txt](https://pip.readthedocs.io/en/1.1/requirements.html) files in script's root directories

Example directory structure:
````
scripts/YourScript
│   requirements.txt
│   __init__.py
└───__pycache__

````

Example requirements.txt:
```
psutil>=3.0.0
-e git+https://github.com/ExampleUser/ExampleRepo#egg=example-branch
```