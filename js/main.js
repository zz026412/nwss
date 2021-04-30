const xlsx = require('xlsx')
const validate = require('jsonschema').validate
const schema = require('./schema.json')

const fileUpload = document.getElementById('file-upload')
const sheetSelect = document.getElementById('sheet-select')
const outputDiv = document.getElementById('output')

class FileValidator {
    constructor(fileObject, fileBuffer, schema) {
        this.fileObject = fileObject
        this.fileBuffer = fileBuffer
        this.schema = schema
    }

    get workbook() {
        // Cache workbook for repeat access
        if ( this._workbook === undefined ) {
            const fileContent = new Uint8Array(this.fileBuffer)
            this._workbook = xlsx.read(fileContent, {'type': 'array'})
        }
        return this._workbook
    }

    loadFile() {
        const sheets = Object.keys(this.workbook.Sheets)

        if ( sheets.length > 1 ) {
            this.promptForSheet(sheets)
        } else {
            this.validateData(sheets[0])
        }
    }

    promptForSheet(sheets) {
        sheetSelect.classList.contains('d-none')
            ? sheetSelect.classList.remove('d-none')
            : () => {}

        let option

        option = document.createElement('option')
        option.value = ''
        option.innerText = 'Select sheet to validate'
        sheetSelect.appendChild(option)

        sheets.forEach(sheet => {
            option = document.createElement('option')
            option.value = sheet
            option.innerText = sheet
            sheetSelect.appendChild(option)
        })

        sheetSelect.addEventListener('change', event => {
            if ( event.target.value != '' ) {
                outputDiv.innerHTML = ''
                this.validateData(event.target.value)
            }
        })
    }

    validateData(sheetName) {
        const sheetData = xlsx.utils.sheet_to_json(this.workbook.Sheets[sheetName])
        const result = validate(sheetData, this.schema)
        this.render(result)
    }

    render(result) {
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

    renderErrors(result, resultHeader) {
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

        const downloadLink = document.createElement('button')
        downloadLink.className = 'btn btn-primary btn-sm mx-3'
        downloadLink.innerText = 'Download errors (CSV)'

        downloadLink.addEventListener('click', event => {
            const errorWb = xlsx.utils.book_new()
            const errorWs = xlsx.utils.json_to_sheet(errorData)
            xlsx.utils.book_append_sheet(errorWb, errorWs, 'errors')
            xlsx.writeFile(errorWb, `${this.fileObject.name} errors.csv`)
        })

        resultHeader.appendChild(downloadLink)
    }
}

fileUpload.addEventListener('change', changeEvent => {
    outputDiv.innerHTML = ''
    sheetSelect.classList.contains('d-none')
        ? () => {}
        : sheetSelect.classList.add('d-none')

    const fileObject = changeEvent.target.files[0]

    const acceptedFormat = ['xlsx', 'csv'].reduce(
        (accumulator, currentValue) => accumulator
            ? accumulator
            : fileObject.name.endsWith(currentValue),
        false
    )

    if ( acceptedFormat ) {
        const reader = new FileReader()
        reader.onload = loadEvent => {
            const validator = new FileValidator(fileObject, loadEvent.target.result, schema)
            validator.loadFile()
        }
        reader.readAsArrayBuffer(fileObject)
    } else {
        outputDiv.innerHTML = '<h3>Invalid file type. Please upload an XLSX or CSV file.</h3>'
    }
})
