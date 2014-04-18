define([], function() {
    'use strict';
    return ['notify', 'gettext', function(notify, gettext) {
        var IS_IMG_REGEXP = /^image\//;
        return {
            scope: {
                file: '=',
                sdImagePreview: '=',
                progressWidth: '='
            },
            link: function(scope, elem) {

                function setProgress(val) {
                    if (scope.progressWidth !== undefined) {
                        scope.progressWidth = val;
                    }
                }

                function updatePreview(e) {
                    scope.$apply(function() {
                        scope.sdImagePreview = e.target.result;
                        setProgress(50);
                    });
                }

                scope.$watch('file', function(file) {
                    if (file && IS_IMG_REGEXP.test(file.type)) {
                        var fileReader = new FileReader();
                        fileReader.onload = updatePreview;
                        fileReader.readAsDataURL(file);
                        setProgress(30);
                    } else if (file) {
                        notify.pop();
                        notify.error(gettext('Sorry, but given file type is not supported.'));
                    }
                });
            }
        };
    }];
});
