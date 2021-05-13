const xlsx = require('xlsx')
const validate = require('jsonschema').validate
const schema = require('./schema.json')

const fileUpload = document.getElementById('file-upload')
const sheetSelect = document.getElementById('sheet-select')
const outputDiv = document.getElementById('output')

function formatDate(date) {
    // https://stackoverflow.com/a/23593099
    let d = new Date(date)
        month = '' + (d.getMonth() + 1)
        day = '' + d.getDate()
        year = d.getFullYear()

    if (month.length < 2) 
        month = '0' + month
    if (day.length < 2) 
        day = '0' + day

    return [year, month, day].join('-')
}

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
            this._workbook = xlsx.read(fileContent, {type: 'array', cellText: false, cellDates: true})
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

    getSheetData(sheet) {
        Object.keys(sheet).forEach(function(cell) {
            // Replace date objects with string representation from spreadsheet
            // Reference: https://github.com/SheetJS/sheetjs/issues/531#issuecomment-640798625
            if (sheet[cell].t === 'd') {
                // Store the original Excel value (a Date) under the z key
                sheet[cell].z = sheet[cell].v;
                // Overwrite the Excel value with the formatted date

                sheet[cell].v = formatDate(sheet[cell].z);
                // Update the cell type to string
                sheet[cell].t = 's';
            }
        })

        return xlsx.utils.sheet_to_json(sheet).map((row) => {
            return {
                // The sheet conversion casts these fields, so cast
                // them into a type expected by the JSON schema
                ...row,
                sample_collect_time: `${row.sample_collect_time}:00`,
                num_no_target_control: row.num_no_target_control.toString(),
                zipcode: row.zipcode.toString()
            }
        })
    }

    validateData(sheetName) {
        const sheetData = this.getSheetData(this.workbook.Sheets[sheetName])
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
                    <th>Column</th>
                    <th>Error</th>
                </tr>
            </thead>
            <tbody id="errors"></tbody>
        `

        const errorTableBody = errorTable.getElementsByTagName('tbody')[0]

        const errorData = []

        result.errors.forEach(error => {
            const nestedError = error.argument.valid
            const errorMessage = nestedError ? error.argument.valid.errors[0].message : error.message
            const column = error.path[1] ? error.path[1] : (nestedError 
                                                            ? error.argument.valid.errors[0].argument 
                                                            : error.argument)
            const lineNumber = error.path[0] + 2

            errorTableBody.insertAdjacentHTML(
                'beforeend',
                `<tr>
                    <td>${lineNumber}</td>
                    <td>${column}</td>
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
