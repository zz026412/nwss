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
        var resultHeader = document.createElement('h3');

        if ( result.errors.length > 0 ) {
            resultHeader.innerText = 'Upload contains errors';

            var errorTable = document.createElement('table');
            errorTable.className = 'table table-striped';
            errorTable.innerHTML = `
                <thead>
                    <tr>
                        <th>Line number</th>
                        <th>Error</th>
                    </tr>
                </thead>
                <tbody id="errors"></tbody>
            `;

            var errorTableBody = errorTable.getElementsByTagName('tbody')[0];

            var errorData = [];

            result.errors.forEach(error => {
                var recordIndex = error.path[0];

                errorTableBody.insertAdjacentHTML(
                    'beforeend',
                    `<tr>
                        <td>${recordIndex + 2}</td>
                        <td>${error.message}</td>
                    </tr>`
                );

                errorData.push({'line_number': recordIndex + 2, 'message': error.message});
            });

            var downloadLink = document.createElement('a');
            downloadLink.href = '#';
            downloadLink.innerText = 'Download errors (CSV)';

            downloadLink.addEventListener('click', (event) => {
                var errorWb = xlsx.utils.book_new();
                var errorWs = xlsx.utils.json_to_sheet(errorData);
                xlsx.utils.book_append_sheet(errorWb, errorWs, 'errors');
                xlsx.writeFile(errorWb, `${file.name } errors.csv`);
            });

            output.appendChild(resultHeader);
            output.appendChild(downloadLink);
            output.appendChild(errorTable);
        } else {
            resultHeader.innerText = 'Upload is valid!';
            output.appendChild(resultHeader);
        };
    };

    reader.readAsArrayBuffer(file);
});
