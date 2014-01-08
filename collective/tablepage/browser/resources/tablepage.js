/**
 * JavaScript integration for TablePage
 */
(function($){
	/*
	 * Soft jQuery DataTables integration (in this way collective.js.datatable is not a strong requirement)
	 */
	if ($.fn.dataTable!=="undefined") {
		$(document).ready(function() {
		    $('table.tablePage').each(function() {
				var columns = $('thead th', this),
				    noDataCols = [];
				// calc which columns will not be sortable
				columns.each(function(index) {
					if ($(this).is('.noData')) {
						noDataCols.push(index)
					}
				});
				var $table = $(this);
				if ($table.find('tr.noResults').length===0) {
					$table.dataTable({
						oLanguage: {sUrl: portal_url + '/@@collective.js.datatables.translation'},
						sPaginationType: "full_numbers",
						aoColumnDefs: [
          					{ 'bSortable': false, 'aTargets': noDataCols }
       					],
						iDisplayLength: 50
					});
				}
			});
		});
	}
})(jQuery);
