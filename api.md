# Printing
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
