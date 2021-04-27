const xlsx = require('xlsx')
const validate = require('jsonschema').validate
const schema = require('./schema.json')

const uploadForm = document.getElementById('upload-form')
const outputDiv = document.getElementById('output')

class FileValidator {
    constructor(fileObject, fileBuffer, schema) {
        this.fileObject = fileObject
        this.fileBuffer = fileBuffer
        this.schema = schema
    }

    readFile() {
        const fileContent = new Uint8Array(this.fileBuffer)
        const workbook = xlsx.read(fileContent, {'type': 'array'})
        const firstSheet = Object.keys(workbook.Sheets)[0]

        return xlsx.utils.sheet_to_json(workbook.Sheets[firstSheet])
    }

    validateData() {
        const fileData = this.readFile()
        return validate(fileData, this.schema)
    }

    renderErrors(result, resultHeader) {
        const downloadLink = document.createElement('button')
        downloadLink.className = 'btn btn-primary btn-sm mx-3'
        downloadLink.innerText = 'Download errors (CSV)'

        downloadLink.addEventListener('click', (event) => {
            const errorWb = xlsx.utils.book_new()
            const errorWs = xlsx.utils.json_to_sheet(errorData)
            xlsx.utils.book_append_sheet(errorWb, errorWs, 'errors')
            xlsx.writeFile(errorWb, `${this.fileObject.name} errors.csv`)
        })

        resultHeader.appendChild(downloadLink)

        const errorTable = document.createElement('table')
        errorTable.className = 'table table-striped'
        errorTable.innerHTML = `
            <thead>
                <tr>
                    <th>Line number</th>
                    <th>Error</th>
                </tr>
            </thead>
            <tbody id="errors"></tbody>
        `

        const errorTableBody = errorTable.getElementsByTagName('tbody')[0]

        const errorData = []

        result.errors.forEach(error => {
            const lineNumber = error.path[0] + 2
            const errorMessage = error.message

            errorTableBody.insertAdjacentHTML(
                'beforeend',
                `<tr>
                    <td>${lineNumber}</td>
                    <td>${errorMessage}</td>
                </tr>`
            )

            errorData.push({'line_number': lineNumber, 'message': errorMessage})
        })

        outputDiv.appendChild(errorTable)
    }

    renderResult() {
        const result = this.validateData()
        const resultHeader = document.createElement('h3')

        if ( result.errors.length > 0 ) {
            resultHeader.innerText = 'Upload contains errors'
            outputDiv.appendChild(resultHeader)
            this.renderErrors(result, resultHeader)
        } else {
            resultHeader.innerText = 'Upload is valid!'
            outputDiv.appendChild(resultHeader)
        }
    }
}

uploadForm.addEventListener('change', changeEvent => {
    outputDiv.innerHTML = ''
    const fileObject = changeEvent.target.files[0]

    const reader = new FileReader()
    reader.onload = loadEvent => {
        const validator = new FileValidator(fileObject, loadEvent.target.result, schema)
        validator.renderResult()
    }

    reader.readAsArrayBuffer(fileObject)
})
