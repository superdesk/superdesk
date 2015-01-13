
'use strict';

angular.module('superdesk.editor', [])
    .directive('sdTextEditor', function() {

        var TEXT_TYPE = 3;

        var config = {
            buttons: ['bold', 'italic', 'underline', 'quote', 'anchor'],
            anchorInputPlaceholder: gettext('Paste or type a full link')
        };

        /**
         * Get number of lines for all p nodes before given node withing same parent.
         */
        function getLinesBeforeNode(node) {
            var lines = 0;
            var p = node.previousSibling;
            while (p) {
                if (p.childNodes.length && p.childNodes[0].nodeType === TEXT_TYPE) {
                    lines += p.childNodes[0].wholeText.split('\n').length;
                } else if (p.childNodes.length) {
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
            scope: {type: '='},
            require: 'ngModel',
            templateUrl: 'scripts/superdesk/editor/views/editor.html',
            link: function(scope, elem, attrs, ngModel) {

                var editorElem;

                function updateModel() {
                    scope.$apply(function editorModelUpdate() {
                        ngModel.$setViewValue(editorElem.html());
                    });
                }

                ngModel.$render = function() {
                    editorElem = elem.find(scope.type === 'preformatted' ?  '.editor-type-text' : '.editor-type-html');
                    editorElem.empty();
                    editorElem.html(ngModel.$viewValue || '<p></p>');
                    this.editor = new window.MediumEditor(editorElem, config);

                    editorElem.on('input', updateModel);
                    editorElem.on('blur', updateModel);

                    if (scope.type === 'preformatted') {
                        editorElem.on('keydown keyup click', function() {
                            scope.$apply(function() {
                                angular.extend(scope.cursor, getLineColumn());
                            });
                        });
                    }

                    scope.$on('$destroy', function() {
                        editorElem.off();
                    });

                    scope.cursor = {};
                };
            }
        };
    });
