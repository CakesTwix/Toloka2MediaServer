$(document).ready(function() {
    var table = $('#dataTableTitles').DataTable({
        ajax: {
            url: '/get_titles',
            dataSrc: function(json) {
                var result = [];
                Object.keys(json).forEach(function(key) {
                    var item = json[key];
                    item.codename = key;
                    result.push(item);
                });
                return result;
            }
        },
        columns: [
            { data: 'codename', title: 'Codename', visible: true },
            { data: 'torrent_name', title: 'Torrent Name', visible: true },
            { data: 'adjusted_episode_number', title: 'Adjusted Episode Number', visible: false },
            { data: 'download_dir', title: 'Download Dir', visible: false },
            { data: 'episode_index', title: 'Episode Index', visible: false },
            { data: 'ext_name', title: 'Ext Name', visible: false },
            { data: 'guid', title: 'GUID', render: function(data, type, row) {
                return `<a href="https://toloka.to/${data}">${data}</a>`;
            }, visible: true },
            { data: 'hash', title: 'Hash', visible: false },
            { data: 'meta', title: 'Meta', visible: false },
            { data: 'publish_date', title: 'Publish Date', visible: true  },
            { data: 'release_group', title: 'Release Group', visible: false },
            { data: 'season_number', title: 'Season Number' , visible: false},
            { data: null, title: 'Actions', orderable: false, render: function(data, type, row) {
                return `
                    <button class="btn btn-outline-warning" disabled><span class="bi bi-pencil-square" aria-hidden="true"></span><span class="visually-hidden" role="status">Edit</span></button>
                    <button class="btn btn-outline-danger" disabled><span class="bi bi-trash" aria-hidden="true"></span><span class="visually-hidden" role="status">Delete</span></button>
                    <button class="btn btn-outline-primary action-update" ><span class="bi bi-arrow-clockwise" aria-hidden="true"></span><span class="visually-hidden" role="status">Update</span></button>
                `;
            }, visible: true }
        ],
        order: [[9, 'des']],
        columnDefs: [
            {
                searchPanes: {
                    show: true
                },
                targets: [1, 8, 10]
            }
        ],
        layout: {
            topStart: {
                buttons: [
                    {
                        extend: 'colvis',
                        postfixButtons: ['colvisRestore'],
                        text: '<i class="bi bi-table"></i>',
                        titleAttr: 'Column Visibility'
                        
                    },
                    {
                        extend: 'searchPanes',
                        className: 'btn btn-secondary',
                        config: {
                            cascadePanes: true
                        }
                        
                    },
                    { 
                        action: function ( e, dt, node, config ) {dt.ajax.reload();},                        
                        text: '<i class="bi bi-arrow-clockwise"></i>',
                        titleAttr: 'Refresh'
                    },
                    {
                        extend: 'pageLength',
                        className: 'btn btn-secondary'
                    }
                ]
            },
            top1End:
            {
                buttons:[
                    {
                        text: 'Add',
                        className: 'btn btn-primary',
                        action: function () {
                            const leftSideAdd = document.querySelector('#leftSideAdd');
                            leftSideAdd.classList.toggle('d-none');
                            const rightSideTitles = document.querySelector('#rightSideTitles');
                            rightSideTitles.classList.toggle('col-md-12');
                            rightSideTitles.classList.toggle('col-md-8');
                        }
                    },
                    {
                        text: 'Update All',
                        className: 'btn btn-primary',
                        action: function ( e, dt, node, config) {
                            node[0].disabled = true;
                            node[0].innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';

                            fetch('/update_all_releases', { method: 'POST' })
                            .then(response => response.json())
                            .then(result => {
                                node[0].innerHTML = '<i class="bi bi-arrow-clockwise"></i> Update All';
                                node[0].disabled = false;
                
                                const bsOperationOffcanvas = new bootstrap.Offcanvas('#offcanvasOperationResults');
                                generateOffCanvas(result);  // Display operation status
                                bsOperationOffcanvas.toggle();
                                window.refreshTable();
                            });
                        }
                    }
                ]
            }
        },
        language: {
            search: "_INPUT_",
            searchPlaceholder: "Search records"
        }
    });

    window.refreshTable = function() {
        table.ajax.reload();
    };

    document.querySelector('#dataTableTitles tbody').addEventListener('click', function(event) {
        let target = event.target;
            // Traverse up to find the element with 'action-update' class
    while (target && !target.classList.contains('action-update')) {
        if (target === this) { // Stop if we reach the container without finding the class
            return;
        }
        target = target.parentNode;
    }
        if (target.classList.contains('action-update')) {
            let tr = target.closest('tr');
            let row = table.row(tr).data();
    
            target.disabled = true;
            target.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
    
            // Assuming `codename` is a property of the row data
            let formData = new FormData();
            formData.append('codename', row.codename);
    
            fetch('/update_release', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(detail => {
                target.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Update';
                target.disabled = false;
    
                const bsOperationOffcanvas = new bootstrap.Offcanvas('#offcanvasOperationResults');
                generateOffCanvas(detail);  // Display operation status
                bsOperationOffcanvas.toggle();
                window.refreshTable();
            })
            .catch(error => {
                console.error('Error:', error);
                target.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Update';
                target.disabled = false;
            });
        }
    });

    const urlButton = document.querySelector('#urlButton');
    const filenameIndex = document.querySelector('#filenameIndex');
    const filenameIndexGroup = document.querySelector('#filenameIndexGroup');
    const cutButton = document.querySelector('#cutButton');
    const releaseTitle = document.querySelector('#releaseTitle');
    const submitButton = document.querySelector('#submitButton');
    const releaseForm = document.querySelector('#releaseForm');

    urlButton.addEventListener('click', () => {
        filenameIndexGroup.classList.toggle("d-none");
    });

    filenameIndex.addEventListener('input', extractNumbers);
    function extractNumbers() {
        const input = filenameIndex.value;
        const numbers = input.split('').map((ch) => (ch >= '0' && ch <= '9') ? ch : ' ').join('').trim().split(/\s+/);
        const resultList = document.querySelector('#numberList');
        resultList.innerHTML = '';
    
        numbers.forEach((number, index) => {
            if (number !== '') {
                const item = document.createElement('div');
                item.className = 'list-group-item';
                item.textContent = `Index: ${index+1}, Number: ${number}`;
                item.addEventListener('click', () => {
                    document.querySelector('#index').value = index + 1;
                    resultList.style.display = 'none';
                });
                resultList.appendChild(item);
            }
        });
    
        resultList.style.display = numbers.join('').length === 0 ? 'none' : 'block';
    }

    cutButton.addEventListener('click', () => {
        const delimiterIndex = releaseTitle.value.search(/[\/|]/);
        if (delimiterIndex !== -1) {
            releaseTitle.value = releaseTitle.value.substring(delimiterIndex + 1);
        }
    });

    releaseForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
        submitButton.disabled = true;
        const formData = new FormData(releaseForm);
        const response = await fetch('/add_release', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        submitButton.innerHTML = 'Submit';
        submitButton.disabled = false;

        const bsOperationOffcanvas = new bootstrap.Offcanvas('#offcanvasOperationResults')
        generateOffCanvas(result);  // Display operation status
        bsOperationOffcanvas.toggle()
        window.refreshTable();
    });

    releaseForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
        submitButton.disabled = true;
        const formData = new FormData(releaseForm);
        const response = await fetch('/add_release', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        submitButton.innerHTML = 'Submit';
        submitButton.disabled = false;

        const bsOperationOffcanvas = new bootstrap.Offcanvas('#offcanvasOperationResults')
        generateOffCanvas(result);  // Display operation status
        bsOperationOffcanvas.toggle()
        window.refreshTable();
    });
    
    function generateOffCanvas(response) {
        if (!response) return; // Exit if no response data
    
        // Determine alert and badge classes based on the response code
        const alertClass = response.response_code === 'SUCCESS' ? 'alert-success' :
                           response.response_code === 'FAILURE' ? 'alert-danger' : 'alert-warning';
        const badgeClass = response.response_code === 'SUCCESS' ? 'bg-success' :
                           response.response_code === 'FAILURE' ? 'bg-danger' : 'bg-warning';
    
        // Helper function to generate list items for accordion
        function generateListItems(items) {
            return items.map(item => `<li class="list-group-item">${item}</li>`).join('');
        }
    
        // Generate accordion HTML
        function generateAccordion(id, headingText, items) {
            return `
                <div class="accordion mt-3" id="${id}">
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="${id}Heading">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#${id}Collapse" aria-expanded="false" aria-controls="${id}Collapse">
                                ${headingText}
                            </button>
                        </h2>
                        <div id="${id}Collapse" class="accordion-collapse collapse" aria-labelledby="${id}Heading">
                            <div class="accordion-body">
                                <ul class="list-group">
                                    ${generateListItems(items)}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    
        // Generate the entire card with accordions
        const cardHTML = `
            <div class="card alert ${alertClass}">
                <div class="card-body">
                    <h5 class="card-title">Operation Type: ${response.operation_type.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}</h5>
                    <p class="card-text">Response Code: <span class="badge ${badgeClass}">${response.response_code}</span></p>
                    <p class="card-text">Start Time: ${response.start_time}</p>
                    <p class="card-text">End Time: ${response.end_time}</p>
                    ${response.titles_references ? generateAccordion('TitlesAccordion', 'Titles References', response.titles_references) : ''}
                    ${response.torrent_references ? generateAccordion('torrentAccordion', 'Torrent References', response.torrent_references) : ''}
                    ${response.operation_logs ? generateAccordion('logsAccordion', 'Operation Logs', response.operation_logs) : ''}
                    <hr>
                    <p class="mb-0">Create an issue on github if something wrong.</p>
                </div>
            </div>
        `;
    
        // Insert the generated HTML into a predefined container in your HTML
        document.getElementById('offcanvasBody').innerHTML = cardHTML;
    }

});


