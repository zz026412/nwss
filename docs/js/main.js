const xlsx = require('xlsx')
const schema = require('./schema.json')
const Ajv = require("ajv").default;
const addFormats = require('ajv-formats').default;

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
            this._workbook = xlsx.read(fileContent, {type: 'array', dateNF: 'YYYY-MM-DD'})
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
        const sheetData = xlsx.utils.sheet_to_json(this.workbook.Sheets[sheetName], {raw: false})

        const ajv = new Ajv({
            allErrors: true,
            strict: 'log',
            coerceTypes: ['number']
        })

        addFormats(ajv)

        ajv.addFormat('integer', {
            type: 'number',
            validate: data => Number.isInteger(data)
        })

        ajv.addFormat('time', {
            type: 'string',
            validate: data => new RegExp('^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$').test(data)
        })

        ajv.addKeyword({
            keyword: 'units'
        })

        ajv.addKeyword({
            keyword: 'enumNames'
        })

        ajv.addKeyword({
            keyword: 'case_insensitive_enums',
            before: 'enum',
            modifying: true,
            validate: function (kwVal, data, metadata, dataCxt) {
                for (const entry of metadata.enum) {
                    if (data.toLowerCase() === entry?.toLowerCase()) {
                        dataCxt.parentData[dataCxt.parentDataProperty] = entry
                        break;
                    }
                }

                return true;
            }
        })

        const validate = ajv.compile(this.schema)
        validate(sheetData)
        this.render(validate)
    }

    render(result) {
        const resultHeader = document.createElement('h3')

        if ( result.errors?.length > 0 ) {
            resultHeader.innerText = 'Upload contains errors'
            outputDiv.appendChild(resultHeader)
            this.renderErrors(result.errors, resultHeader)
        } else {
            resultHeader.innerText = 'Upload is valid!'
            outputDiv.appendChild(resultHeader)
        }
    }

    renderErrors(errors, resultHeader) {
        const errorTable = document.createElement('table')
        errorTable.className = 'table table-striped'
        errorTable.innerHTML = `
            <thead>
                <tr>
                    <th>Line number</th>
                    <th>Column</th>
                    <th>Error</th>
                </tr>
            </thead>
            <tbody id="errors"></tbody>
        `

        const errorTableBody = errorTable.getElementsByTagName('tbody')[0]

        const errorData = []

        errors.forEach(error => {
            // Skip an "if" error and render all other errors,
            // because an "if" error object doesn't provide any
            // relevant error information. In this case, we will 
            // capture and render the associated "then" error.
            if (error.keyword === 'if') {
                return
            }

            const lineAndColumn = error.instancePath.split('/')
            const lineNumber = parseInt(lineAndColumn[1]) + 1
            const additionalInfo = Object.values({...error.params})[0]
            const column = lineAndColumn[2] ? lineAndColumn[2] : additionalInfo

            errorTableBody.insertAdjacentHTML(
                'beforeend',
                `<tr>
                    <td>${lineNumber}</td>
                    <td>${column}</td>
                    <td>${error.message}</td>
                </tr>`
            )

            errorData.push({
                'line_number': lineNumber,
                'column': column,
                'message': error.message})
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
