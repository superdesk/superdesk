
'use strict';

angular.module('superdesk.editor', [])
    .directive('sdTextEditor', function() {

        var TEXT_TYPE = 3;

        var config = {
            buttons: ['bold', 'italic', 'underline', 'quote', 'anchor']
        };

        /**
         * Get number of lines for all p nodes before given node withing same parent.
         */
        function getLinesBeforeNode(node) {
            var lines = 0;
            var p = node.previousSibling;
            while (p) {
                if (p.childNodes[0].nodeType === TEXT_TYPE) {
                    lines += p.childNodes[0].wholeText.split('\n').length;
                } else {
                    lines += 1; // empty paragraph
                }
                p = p.previousSibling;
            }

            return lines;
        }

        /**
         * Get line/column coordinates for given cursor position.
         */
        function getLineColumn() {
            var text, lines, linesBefore;
            var selection = window.getSelection();
            if (selection.anchorNode.nodeType === TEXT_TYPE) {
                text = selection.anchorNode.wholeText.substring(0, selection.anchorOffset);
                lines = text.split('\n');
                linesBefore = getLinesBeforeNode(selection.anchorNode.parentNode);
            } else {
                text = '';
                lines = [text];
                linesBefore = getLinesBeforeNode(selection.anchorNode);
            }
            return {
                line: lines.length + linesBefore,
                column: lines[lines.length - 1].length + 1
            };
        }

        return {
            scope: {cursor: '='},
            require: 'ngModel',
            link: function(scope, elem, attrs, ngModel) {
                function updateModel() {
                    scope.$apply(function editorModelUpdate() {
                        ngModel.$setViewValue(elem.html());
                    });
                }

                ngModel.$render = function() {
                    elem.empty();
                    elem.html(ngModel.$viewValue || '<p></p>'); // this p can use some css min-height
                    this.editor = new window.MediumEditor(elem, config);
                };

                elem.on('input', updateModel);
                elem.on('blur', updateModel);
                elem.on('keydown keyup click', function() {
                    scope.$apply(function() {
                        angular.extend(scope.cursor, getLineColumn());
                    });
                });

                scope.$on('$destroy', function() {
                    elem.off();
                });
            }
        };
    });
