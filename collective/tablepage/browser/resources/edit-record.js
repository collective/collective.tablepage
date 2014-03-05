/**
 * Helper JS for editing a record
 */

(function ($) {
    $(document).ready(function () {
        /**
         * add new file in multiple file selection widget
         */

        var fieldInc = 1;
        var patt = /_\d+$/;
        function incAttribute(elem, name) {
            var attr = elem.attr(name);
            var oldVal = parseInt(patt.exec(attr)[0].substr(1, attr.length-1), 10);
            elem.attr(name, attr.replace( patt, '_' + (oldVal + fieldInc) ));
        }
        
        // Save the new field model for later
		$('.fieldFieldContainer').each(function () {
			var mainContainer = $(this);
	        var subFieldFile = $('.fileField', mainContainer).clone();
	        $('.newFile', mainContainer).click(function(event) {
	            event.preventDefault();
	            var newFileField = subFieldFile.clone().hide();
	            $('.fileField:last', mainContainer).after(newFileField);
	            newFileField.find(':input').each(function() {
	                incAttribute($(this), 'id');
	                incAttribute($(this), 'name');
	            });
	            newFileField.find('label').each(function() {
	                incAttribute($(this), 'for');
	            });
	            newFileField.slideDown('fast');
	            newFileField.find(':input:first').focus();
	            fieldInc++;
	        });

		})

        /**
         * Sorting multiple files
         */

        function moveRow($element, direction) {
            var $myParent = $element.parents('li.storageFile');
            var $siblingParent = null;
            if (direction==='up') {
                $siblingParent = $myParent.prev();
                $myParent.insertBefore($siblingParent);
            } else if (direction==='down') {
                $siblingParent = $myParent.next();            
                $myParent.insertAfter($siblingParent);
            }
            // Now switching buttons (I can't use "detach" until Plone 3.3 is supported)
            var myButtons = $myParent.find('.commandSelectedFile').clone(true);
            $myParent.find('.commandSelectedFile').remove();
            $siblingParent.find('.commandSelectedFile').appendTo($myParent);
            $siblingParent.append(myButtons);
        }

        $('a.moveUp').click(function(event) {
            event.preventDefault();
            moveRow($(this), 'up');
        });
        $('a.moveDown').click(function(event) {
            event.preventDefault();
            moveRow($(this), 'down');
        });
        $('a.removeRow').click(function(event) {
            event.preventDefault()
            var row = $(this).parents('li.storageFile');
            
            // if is the first or last row, some buttons must be changed
            if (row.prevAll('li').length==0) {
                row.next().find('a.moveUp').remove();
            }
            if (row.nextAll('li').length==0) {
                row.prev().find('a.moveDown').remove();
            }
            row.remove();
            $('.availableFiles li[data-uid=' + row.attr('data-uid') + ']').show();

        });
        $('a.addRow').click(function(event) {
            event.preventDefault();
            var row = $(this).parents('li.storageFile');
            row.hide();
            var activeFiles = $(this).parents('.subField').find('.savedFiles');
            var fieldId = activeFiles.attr('data-fieldname');
            var newRow = $('<li class="storageFile"><\/li>');
            newRow.attr('data-uid', row.data('uid'));
            var newInput = row.find('input').clone();
            newRow.append(newInput);
            newInput.attr('name', 'existing_' + fieldId + ':list');
            newRow.append(row.find('a:first').clone());
            if ($('li', activeFiles).length>0) {
                newRow.append($('#buttonModels').find('a.moveUp').clone(true));
                $('li:last', activeFiles).prepend($('#buttonModels').find('a.moveDown').clone(true));
            }
            newRow.append($('#buttonModels').find('a.removeRow').clone(true));
            activeFiles.append(newRow);
        });
        
        /*
         * Multiple file upload and validation error is a nighmare. We have the uuid in the request
         * and also stored in the "data-submitted-values" HTML 5 attribute, but we need to "click"
         * on add commands to select those values.
         */
         
        $('.savedFiles[data-submitted-values]').each(function() {
            var $this = $(this),
                container = $this.parents('.subField'),
                uuids = $this.attr('data-submitted-values').split(','),
                selectable = container.find('.availableFiles');
            for (var i=0;i<uuids.length;i++) {
                $('.storageFile input[value=' + uuids[i] + ']', selectable).nextAll('.commandSelectedFile').click();
            }
        });
         
    });
})(jQuery);
