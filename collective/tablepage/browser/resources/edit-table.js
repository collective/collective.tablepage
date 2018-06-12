/**
 * Helper JS for editing a Table Page's table
 */

(function ($) {
    $(document).ready(function () {
        /**
         * select/unselect all
         */ 
        $('#selectAll').click(function(event) {
            $('.selectRow').prop('checked', $(this).prop('checked'));
        });

		/**
		 * "Delete selected items" command
		 */ 
        $('#massDelete').click(function(event) {
            event.preventDefault();
            if ($('.selectRow:checked').length>0) {
                $('#tableForm').submit();
            }
        });
    });
})(jQuery);
