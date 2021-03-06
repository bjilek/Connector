# Connector

## Printing
### Print PDF with default printer
```
fetch('http://localhost:5050/api/v1/print', {
    method: 'POST',
    body: JSON.stringify({pdf: pdfFile}),  # Base64 encoded PDF
    headers: {
        'Content-Type': 'application/json'
}
```
### Print PDF with specified printer
```
fetch('http://localhost:5050/api/v1/print/printer+name', {
    method: 'POST',
    body: JSON.stringify({pdf: pdfFile, printer: 'Name of the Printer'}),
    headers: {
        'Content-Type': 'application/json'
}
```
### List available printer
Request:
```
fetch('http://localhost:5050/api/v1/list_printer')
```
Response:
```
{"data":{"default":"Printer2","printer":["Printer1", "Printer2", "Printer3"]}}
```
## Build
### Windows
pyinstaller -F --add-data testpage_a4.pdf;. --add-data testpage_bon_80.pdf;. --add-data connector\templates;connector\templates --add-data connector\static;connector\static --add-data gsdll64.dll;. --add-binary gswin64c.exe;. --noconsole --hidden-imports requests main.py -n connector_win.exe
### Linux
pyinstaller -F  --add-data testpage_a4.pdf:. --add-data testpage_bon_80.pdf:. --add-data connector/templates:connector/templates --add-data connector/static:connector/static -n connector_linux main.py
