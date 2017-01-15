if (typeof jQuery === 'undefined') {
    throw new Error('bootstrap-imageupload\'s JavaScript requires jQuery.');
}

(function($) {
    'use strict';

    var options = {};

    var methods = {
        init: init
    };
    var added_image_count = 0;

    // -----------------------------------------------------------------------------
    // Plugin Definition
    // -----------------------------------------------------------------------------

    $.fn.imageupload = function(methodOrOptions) {
        var givenArguments = arguments;

        return this.filter('div').each(function() {
            if (methods[methodOrOptions]) {
                methods[methodOrOptions].apply($(this), Array.prototype.slice.call(givenArguments, 1));
            }
            else if (typeof methodOrOptions === 'object' || !methodOrOptions) {
                methods.init.apply($(this), givenArguments);
            }
            else {
                throw new Error('Method "' + methodOrOptions + '" is not defined for imageupload.');
            }
        });
    };

    $.fn.imageupload.defaultOptions = {
        allowedFormats: [ 'jpg', 'jpeg', 'png', 'gif' ],
        maxWidth: 250,
        maxHeight: 250,
        maxFileSizeKb: 2048
    };

    // -----------------------------------------------------------------------------
    // Public Methods
    // -----------------------------------------------------------------------------

    function init(givenOptions) {
        options = $.extend({}, $.fn.imageupload.defaultOptions, givenOptions);

        var $imageupload = this;
        var $fileTab = $imageupload.find('.file-tab');
        var $browseFileButton = $fileTab.find('input[type="file"]');
        var $removeFileButton = $fileTab.find('.remove_btn');

        resetFileTab($fileTab);

        $browseFileButton.off();
        $removeFileButton.off();

        $browseFileButton.on('change', function() {
            $(this).blur();
            submitImageFile($fileTab);
        });

        $removeFileButton.on('click', function() {
            $(this).blur();
            resetFileTab($fileTab);
        });

    }


    // -----------------------------------------------------------------------------
    // Private Methods
    // -----------------------------------------------------------------------------

    function getAlertHtml(message) {
        var html = [];
        html.push('<div class="alert alert-danger alert-dismissible">');
        html.push('<button type="button" class="close" data-dismiss="alert">');
        html.push('<span>&times;</span>');
        html.push('</button>' + message);
        html.push('</div>');
        return html.join('');
    }

    function getImageThumbnailHtml(src) {
        return '<img src="' + src + '" alt="Image preview" class="thumbnail" style="width: ' + options.maxWidth + 'px; height: ' + options.maxHeight + 'px">';
    }

    function getFileExtension(path) {
        return path.substr(path.lastIndexOf('.') + 1).toLowerCase();
    }

    function isValidImageFile(file, callback) {
        // Check file size.
        if (file.size / 1024 > options.maxFileSizeKb)
        {
            callback(false, 'File is too large (max ' + options.maxFileSizeKb + 'kB).');
            return;
        }

        // Check image format by file extension.
        var fileExtension = getFileExtension(file.name);
        if ($.inArray(fileExtension, options.allowedFormats) > -1) {
            callback(true, 'Image file is valid.');
        }
        else {
            callback(false, 'File type is not allowed.');
        }
    }

    function resetFileTab($fileTab) {

        $fileTab.find('.alert').remove();

        $fileTab.find('input').val('');

        // check how many images there uploaded and if 0
        // disable suggest button
        var $images = $('#demo').find('img');
        var image_count = $images.length;

        if (image_count === 0 ) {
            var $suggestButton = $('#suggest_btn');
            $suggestButton.prop('disabled', true);
            $suggestButton.addClass('disabled');
        }
    }

    function submitImageFile($fileTab) {
        var $browseFileButton = $fileTab.find('.btn:eq(0)');
        var $removeFileButton = $fileTab.find('.btn:eq(1)');
        var $fileInput = $browseFileButton.find('input');
        
        $fileTab.find('.alert').remove();

        // Check if file was uploaded.
        if (!($fileInput[0].files && $fileInput[0].files[0])) {
            return;
        }

        
        var file = $fileInput[0].files[0];

        isValidImageFile(file, function(isValid, message) {
            if (isValid) {

                // Enable suggest buttong
                var $suggestButton = $('#suggest_btn');
                $suggestButton.prop('disabled', false);
                $suggestButton.removeClass('disabled');

                // Enable next 

                var fileReader = new FileReader();

                fileReader.onload = function(e) {
                    // Show thumbnail and remove button.

                    var img = $fileTab.find('.preview_img')[0];
                    var $img = $(img);
                    $img.attr('src', e.target.result)
                    $img.show()

                    var remove_btn = $fileTab.find('.remove_btn')[0]
                    $(remove_btn).show();

                };

                fileReader.onerror = function() {
                    $fileTab.prepend(getAlertHtml('Error loading image file.'));
                    $fileInput.val('');
                };

                fileReader.readAsDataURL(file);
            }
            else {
                $fileTab.prepend(getAlertHtml(message));
                $browseFileButton.find('span').text('Browse');
                $fileInput.val('');
            }

            $browseFileButton.prop('disabled', false);
        });
    }

}(jQuery));
