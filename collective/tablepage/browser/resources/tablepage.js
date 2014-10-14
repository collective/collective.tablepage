/**
 * JavaScript integration for TablePage
 */
(function($){
    $(document).ready(function() {
        var dataTable = null,
            wWidth = $("#portal-columns").width(),
            wWidth995 = parseInt(wWidth/100*95, 10), 
            innerW = $('#content').width(),
            innerW998 = parseInt(innerW/100*98, 10),
            wHeidht = $(window).height(),
            wHeidht995 = parseInt(wHeidht/100*95, 10);

        // expand/collapse table feature
        var selectAllCommand = $('#selectAll');
        if (selectAllCommand.length>0) {
            var newCommand = $('<a href=""><img src="' + portal_url + '/++resource++collective.tablepage.images/fullscreenexpand_icon.png" alt="" class="controlWidth" /></a>');
            newCommand.click(function(event) {
                event.preventDefault();
                var $table = newCommand.closest('.tablePage');
                $table.toggleClass('helpEdit');
                if (!newCommand.data('expanded')) {
                    newCommand.data('expanded', true);
                    $('#portal-column-one,#portal-column-two,#portal-top,#portal-footer-wrapper').hide();
                    if (dataTable) {
                        //dataTable.fnSettings().sScrollXInner = $("#portal-columns").width()+"px";
                        $('.dataTables_wrapper').css('width', wWidth995+'px');
                        $('.dataTables_scrollHeadInner').css('width', wWidth995+'px');
                        //dataTable.fnDraw(false);
                    }
                    newCommand.find('img').attr('src', portal_url + '/++resource++collective.tablepage.images/fullscreencollapse_icon.png');
                } else {
                    newCommand.data('expanded', false);
                    $('#portal-column-one,#portal-column-two,#portal-top,#portal-footer-wrapper').show();
                    newCommand.find('img').attr('src', portal_url + '/++resource++collective.tablepage.images/fullscreenexpand_icon.png');
                    if (dataTable) {
                        //dataTable.fnSettings().sScrollXInner = "95%";
                        $('.dataTables_wrapper').css('width', '100%');
                        $('.dataTables_scrollHeadInner').css('width', '100%');
                        //dataTable.fnDraw(false);
                    }
                }
            });
            selectAllCommand.after(newCommand);
        }

        /*
         * Soft jQuery DataTables integration (this way collective.js.datatable is not a strong requirement)
         */        
        if ($.fn.dataTable) {
            $('table.tablePage').each(function() {
                var columns = null,
                    noDataCols = [],
                    $table = $(this),
                    allLabelRows = [],
                    rowCount = $table.find('tbody tr').length;
                
                $table.css('width', innerW998+'px');

                /*
                 * We manage complexity of having labels (DataTable do not support it at all)
                 * So we use the DataTables Row Grouping Add-on (if enabled)
                 */
                var $labels = $('tr.tablePageSubHeader', $table);
                if ($.fn.rowGrouping && $labels.length>0) {
                    // add a new, first position, column
                    $('thead tr', $table).prepend($('<th class="noData labelColumn"></th>'));
                    
                    // Be sure the we have a first position label. If not: create a new one with empy contents
                    if (!$('tbody tr:first', $table).is('.tablePageSubHeader')) {
                        var generatedLabel = $('<tr class="tablePageSubHeader"><td>---</td></tr>');
                        $('tbody', $table).prepend(generatedLabel);
                        // re-calc label iterable; .add() method is not working as excepted 
                        $labels = $('tr.tablePageSubHeader', $table);
                    }
                    
                    // Now "clone" every label as a new, first position column, in every row of the group
                    $labels.each(function() {
                        var label = $(this),
                            myGroup = label.nextUntil('.tablePageSubHeader'),
                            commandContainer = null;

                        // If in edit mode, we could have label commands
                        if (label.find('.rowCommands')) {
                            commandContainer = $('<div class="labelCommandContainer"></div>');
                            commandContainer.append(label.find('.rowCommands').children());
                        }

                        myGroup.each(function() {
                            var $row = $(this),
                                newCell = $('<td class="labelCell"></td>');
                            $row.prepend(newCell);
                            newCell.html(label.children().html());
                            if (commandContainer) {
                                newCell.append(commandContainer.clone());
                            }
                        });
                        label.remove();
                    });
                }

                /*
                 * Usability. If we don't use labels (so we don't have row groups)
                 * we move the "+" in the non-scrollable section at bottom
                 */
                if ($labels.length===0) {
                    var addCommand = $table.find("tbody .rowCommands a[href$='@@edit-record']");
                    addCommand.appendTo('tfoot .rowCommands td');
                }

                // Calc which columns will not be sortable (all of them if we have labels)
                // BBB: sorting with dates is disabled by default to prevent issues
                // see http://legacy.datatables.net/usage/columns#sType
                // probably some plugins is needed: http://datatables.net/plug-ins/sorting/
                columns = $('thead th', this);
                columns.each(function(index) {
                    if ($(this).is('.noData') || $(this).is('.coltype-text') || $(this).is('.coltype-date')
                                || $(this).is('.coltype-date-time')) {
                        noDataCols.push(index);
                    }
                });

                // Init the DataTables, but only if we have some rows
                if ($table.find('tr.noResults').length===0) {
                    var hasLabels = allLabelRows.length>0,
                        wHeidht = $(window).height(),
                        batchingEnabled = !!$table.attr('data-batching-enabled');
                    
                    dataTable = $table.dataTable({
                        oLanguage: {sUrl: portal_url + '/@@collective.js.datatables.translation'},
                        sPaginationType: "full_numbers",
                        aaSorting: [],
                        bSort: true,
                        bLengthChange: hasLabels ? false : true,
                        bPaginate: hasLabels || batchingEnabled ? false : true,
                        asStripClasses: null,
                        sScrollX: innerW998+"px",
                        // sScrollXInner: "95%",
                        sScrollY: wHeidht995 + "px",
                        bScrollCollapse: true,
                        bAutoWidth: false,
                        bInfo: batchingEnabled ? false : true,
                        aoColumnDefs: [
                              { 'bSortable': false, 'aTargets': noDataCols }
                           ],
                        iDisplayLength: 100,
                        fnInitComplete: function() {
                            // Force a min-height when few rows are available
                            var tbodyContainer = $('div.dataTables_scrollBody');
                            if (tbodyContainer.find('tr').length<3) {
                                tbodyContainer.css('height', "100px");    
                            }
                            if ($labels.length > 0) {
                                dataTable.rowGrouping();
                            }
                        }
/*
                        fnDrawCallback: function( oSettings ) {

                        }
*/
                    });
                }
                
            });
        }

    });
        
})(jQuery);
