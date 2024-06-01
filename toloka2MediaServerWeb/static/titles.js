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
            { data: 'publish_date', title: 'Publish Date' },
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
        columnDefs: [
            { targets: '_all', visible: false },
            { targets: [0, 1, 6, 12], visible: true }
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
});