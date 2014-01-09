/**
 * JavaScript integration for TablePage
 */
(function($){
	$(document).ready(function() {
		
		// expand/collapse table feature
		var selectAllCommand = $('#selectAll');
		if (selectAllCommand.length>0) {
			var newCommand = $('<a href=""><img src="' + portal_url + '/++resource++collective.tablepage.images/fullscreenexpand_icon.png" alt="" /></a>');
			newCommand.click(function(event) {
				event.preventDefault();
				if (!newCommand.data('expanded')) {
					newCommand.data('expanded', true);
					newCommand.find('img').attr('src', portal_url + '/++resource++collective.tablepage.images/fullscreencollapse_icon.png');
				} else {
					newCommand.data('expanded', false);
					newCommand.find('img').attr('src', portal_url + '/++resource++collective.tablepage.images/fullscreenexpand_icon.png');
				}
				var $table = newCommand.closest('.tablePage');
				$table.toggleClass('helpEdit');
			});
			selectAllCommand.after(newCommand);
		}

		/*
		 * Soft jQuery DataTables integration (in this way collective.js.datatable is not a strong requirement)
		 */		
		if ($.fn.dataTable!=="undefined") {
		    $('table.tablePage').each(function() {
				var columns = $('thead th', this),
				    noDataCols = [],
					$table = $(this),
					allLabelRows = [];

				// manage complexity of having labels (DataTable do not support it at all)
				$('tbody tr', $table).each(function(index) {
					var $labelRow = $(this);
					if ($labelRow.is('.tablePageSubHeader')) {
						allLabelRows.push({index: index, row: $labelRow.remove()});
					}
				});

				// calc which columns will not be sortable (all of them is we have labels)
				columns.each(function(index) {
					if ($(this).is('.noData') || allLabelRows.length>0) {
						noDataCols.push(index)
					}
				});

				// init the DataTables
				if ($table.find('tr.noResults').length===0) {
					$table.dataTable({
						oLanguage: {sUrl: portal_url + '/@@collective.js.datatables.translation'},
						sPaginationType: "full_numbers",
						bSort: allLabelRows.length>0 ? false : true,
						bLengthChange: allLabelRows.length>0 ? false : true,
                		bPaginate: allLabelRows.length>0 ? false : true,
						asStripClasses: null,
						aoColumnDefs: [
          					{ 'bSortable': false, 'aTargets': noDataCols }
       					],
						iDisplayLength: allLabelRows.length>0 ? -1 : 50,
						fnDrawCallback: function( oSettings ) {
							// restoring all labels
							for (var i=0; i<allLabelRows.length; i++) {
								var rowIndex = allLabelRows[i].index;
								var thiefRow = $table.find('tbody tr:eq(' + rowIndex + ')');
								thiefRow.before(allLabelRows[i].row);
							}
    					}
					});
				}
				
			});
		}

	});
		
})(jQuery);
