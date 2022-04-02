# Connector
## Build
### Windows
pyinstaller -F --add-data testpage.pdf;. --add-data connector\templates;connector\templates --add-data connector\static;connector\static --add-binary gswin64c.exe;. --noconsole --hidden-imports requests main.py -n connector.exe
### Linux
pyinstaller -F  --add-data testpage.pdf:. --add-data connector/templates:connector/templates --add-data connector/static:connector/static -n connector main.py