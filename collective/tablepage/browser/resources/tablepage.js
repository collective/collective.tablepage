/**
 * JavaScript integration for TablePage
 */
(function($){
    $(document).ready(function() {
        var dataTable = null;
        var wWidth = $("#portal-columns").width();
        var wWidth995 = parseInt(wWidth/100*95); 
        var innerW = $('#content').width();
        var wHeidht = $(window).height();
        var wHeidht990 = parseInt(wHeidht/100*90);

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
                    minRows = 4,
                    rowCount = $table.find('tbody tr').length;
                
                $table.css('width', innerW+'px');

                /*
                 * We manage complexity of having labels (DataTable do not support it at all)
                 * So we use the DataTables Row Grouping Add-on 
                 */
                var $labels = $('tr.tablePageSubHeader', $table);
                if ($.fn.rowGrouping && $labels.length>0 && rowCount>=minRows) {
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

                // Calc which columns will not be sortable (all of them is we have labels)
                columns = $('thead th', this);
                columns.each(function(index) {
                    if ($(this).is('.noData') || $(this).is('.coltype-Text')) {
                        noDataCols.push(index)
                    }
                });

                // Init the DataTables, but only if we have some rows
                if ($table.find('tr.noResults').length===0 && rowCount>=minRows) {
                    var hasLabels = allLabelRows.length>0,
                        wHeidht = $(window).height()
					    batchingEnabled = !!$table.attr('data-batching-enabled');
                    
                    dataTable = $table.dataTable({
                        oLanguage: {sUrl: portal_url + '/@@collective.js.datatables.translation'},
                        sPaginationType: "full_numbers",
                        aaSorting: [],
                        bSort: true,
                        bLengthChange: hasLabels ? false : true,
                        bPaginate: hasLabels || batchingEnabled ? false : true,
                        asStripClasses: null,
                        sScrollX: innerW+"px",
                        // sScrollXInner: "95%",
                        sScrollY: wHeidht990 + "px",
                        bScrollCollapse: true,
                        bAutoWidth: false,
						bInfo: batchingEnabled ? false : true,
                        aoColumnDefs: [
                              { 'bSortable': false, 'aTargets': noDataCols }
                           ],
                        iDisplayLength: 100,
                        fnInitComplete: function() {
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
