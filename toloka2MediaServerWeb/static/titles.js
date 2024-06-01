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
            { data: 'adjusted_episode_number', title: 'Adjusted Episode Number' },
            { data: 'download_dir', title: 'Download Dir' },
            { data: 'episode_index', title: 'Episode Index' },
            { data: 'ext_name', title: 'Ext Name' },
            { data: 'guid', title: 'GUID', render: function(data, type, row) {
                return `<a href="https://toloka.to/${data}">${data}</a>`;
            }, visible: true },
            { data: 'hash', title: 'Hash' },
            { data: 'meta', title: 'Meta' },
            { data: 'publish_date', title: 'Publish Date', visible: true  },
            { data: 'release_group', title: 'Release Group' },
            { data: 'season_number', title: 'Season Number' },
            { data: null, title: 'Actions', orderable: false, render: function(data, type, row) {
                return `
                    <button class="btn btn-outline-warning" disabled><span class="bi bi-pencil-square" aria-hidden="true"></span><span class="visually-hidden" role="status">Edit</span></button>
                    <button class="btn btn-outline-danger" disabled><span class="bi bi-trash" aria-hidden="true"></span><span class="visually-hidden" role="status">Delete</span></button>
                    <button class="btn btn-outline-primary" disabled><span class="bi bi-arrow-clockwise" aria-hidden="true"></span><span class="visually-hidden" role="status">Update</span></button>
                `;
            }, visible: true }
        ],
        order: [[9, 'des']],
        columnDefs: [
            { targets: '_all', visible: false },
            { targets: [0, 1, 6, 9, 12], visible: true }
        ],
        layout: {
            topStart: {
                buttons: [
                    {
                        extend: 'colvis',
                        postfixButtons: ['colvisRestore']
                    },
                    { text: 'Refresh', action: function ( e, dt, node, config ) {
                        dt.ajax.reload();
                    }}
                ]
            }
        }
    });

    window.refreshTable = function() {
        table.ajax.reload();
    };

    function extractNumbers() {
        const input = document.getElementById('numberInput').value;
        const numbers = input.split('').map((ch) => (ch >= '0' && ch <= '9') ? ch : ' ').join('').trim().split(/\s+/);
        const resultList = document.getElementById('result');
        resultList.innerHTML = '';
    
        numbers.forEach((number, index) => {
            if (number !== '') {
                const item = document.createElement('div');
                item.className = 'list-group-item';
                item.textContent = `Index: ${index+1}, Number: ${number}`;
                item.addEventListener('click', () => {
                    document.getElementById('index').value = index + 1;
                    resultList.style.display = 'none';
                });
                resultList.appendChild(item);
            }
        });
    
        if (numbers.join('').length === 0) {
            resultList.style.display = 'none';
        } else {
            resultList.style.display = 'block';
        }
    }
    // Get the input element
    const numberInput = document.querySelector('#numberInput');
    
    // Event listener for input event
    numberInput.addEventListener('input', extractNumbers);
    
    // Event listener for change event
    numberInput.addEventListener('change', extractNumbers);
    
});


