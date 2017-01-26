#!C:\Users\blusc\AppData\Roaming\TS3Client\plugins\pyTSon\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'pip==7.1.0','console_scripts','pip'
__requires__ = 'pip==7.1.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('pip==7.1.0', 'console_scripts', 'pip')()
    )
