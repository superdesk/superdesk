(function() {
    'use strict';

    /**
     * Populate audio/video sources using given renditions dict
     */
    function SourcesDirective() {
        var typeMap = {
            'video/mpeg': 'video/mp4'
        };

        return {
            scope: {
                renditions: '='
            },
            link: function(scope, elem, attrs) {

                function pause() {
                    elem[0].pause();
                }

                function load() {
                    elem[0].load();
                }

                function createSource(rendition) {
                    angular.element('<source>')
                        .attr('src', rendition.href)
                        .attr('type', typeMap[rendition.mimetype] || rendition.mimetype)
                        .appendTo(elem);
                }

                scope.$watch('renditions', function(renditions) {
                    pause();
                    elem.empty();
                    angular.forEach(renditions, createSource);
                    load();
                });

                scope.$on('$destroy', pause);
            }
        };
    }

    function FileValidatorDirective() {

        function isAcceptedFileType(file, accept) {
            return file.type.indexOf(accept.replace('*', '')) === 0;
        }

        return {
            require: 'ngModel',
            link: function(scope, elem, attrs, ngModel) {
                ngModel.$validators.fileType = function(modelValue, viewValue) {
                    var value = modelValue || viewValue;
                    return !value || !attrs.accept || isAcceptedFileType(value, attrs.accept);
                };
            }
        };
    }

   angular.module('superdesk.upload', ['angularFileUpload', 'superdesk.imageFactory'])
   .directive('sdSources', SourcesDirective)
   .directive('sdFileTypeValidator', FileValidatorDirective);

})();
