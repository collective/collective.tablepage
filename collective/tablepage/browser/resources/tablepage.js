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
				if (!newCommand.data('expanded')) {
					newCommand.data('expanded', true);
					$('#portal-column-one').hide();
					$('#portal-column-two').hide();
					if (dataTable) {
						//dataTable.fnSettings().sScrollXInner = $("#portal-columns").width()+"px";
						$('.dataTables_wrapper').css('width', wWidth995+'px');
						$('.dataTables_scrollHeadInner').css('width', wWidth995+'px');
						dataTable.fnDraw(false);
					}
					newCommand.find('img').attr('src', portal_url + '/++resource++collective.tablepage.images/fullscreencollapse_icon.png');
				} else {
					newCommand.data('expanded', false);
					$('#portal-column-one').show();
					$('#portal-column-two').show();
					newCommand.find('img').attr('src', portal_url + '/++resource++collective.tablepage.images/fullscreenexpand_icon.png');
					if (dataTable) {
						//dataTable.fnSettings().sScrollXInner = "95%";
						$('.dataTables_wrapper').css('width', '100%');
						$('.dataTables_scrollHeadInner').css('width', '100%');
						dataTable.fnDraw(false);
					}
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
				
				$table.css('width', innerW+'px');

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
					var hasLabels = allLabelRows.length>0;
					var wHeidht = $(window).height();
					
					dataTable = $table.dataTable({
						oLanguage: {sUrl: portal_url + '/@@collective.js.datatables.translation'},
						sPaginationType: "full_numbers",
						aaSorting: [],
						bSort: hasLabels ? false : true,
						bLengthChange: hasLabels ? false : true,
                		bPaginate: hasLabels ? false : true,
						asStripClasses: null,
						sScrollX: innerW+"px",
						// sScrollXInner: "95%",
						sScrollY: wHeidht990 + "px",
						bScrollCollapse: true,
						bAutoWidth: false,
						aoColumnDefs: [
          					{ 'bSortable': false, 'aTargets': noDataCols }
       					],
						iDisplayLength: hasLabels ? -1 : 50,
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
