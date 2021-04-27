const xlsx = require('xlsx');
const validate = require('jsonschema').validate;
const schema = require('./schema.json');

const uploadForm = document.getElementById('upload-form');
var outputDiv = document.getElementById('output');

uploadForm.addEventListener('change', (event) => {
    outputDiv.innerHTML = '';
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        var data = new Uint8Array(e.target.result);
        var workbook = xlsx.read(data, {type: 'array'});
        // TODO: Show prompt allowing user to pick sheet
        var firstSheet = Object.keys(workbook.Sheets)[0];
        var arrayData = xlsx.utils.sheet_to_json(workbook.Sheets[firstSheet]);

        var result = validate(arrayData, schema);
        if ( result.errors.length > 0 ) {
            result.errors.forEach(error => {
                outputDiv.insertAdjacentHTML(
                    'beforeend',
                    `Error in record ${error.path[0]}: ${error.message}<br />`
                );
            });
        } else {
            output.innerHTML = 'Upload is valid!';
        };
    };

    reader.readAsArrayBuffer(file);
});
