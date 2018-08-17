# Automatic Proxy pyTSon script

## Known bugs that **can** be fixed
- None yet

## Known bugs that can't be fixed
- Connection times out after ~ 4 hours:
  - That happens because the proxy provided by ts3.cloud is automatically being closed even if it's still in use.
- The passworded channel i wanted to connect to is not being used
  - TeamSpeak want's the password unencrypted but only provides it encrypted, sorry :(