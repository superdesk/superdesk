define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.directives')
        .directive('sdSortable', [function() {
            return {
                scope: {update: '=', placeholder: '='},
                link: function(scope, element, attrs) {
                    element.sortable({
                        tolerance: 'intersect',
                        placeholder: scope.placeholder,
                        start: function(event, ui) {
                            $(event.target).data("ui-sortable").floating = true;
                        },
                        update: function(event, ui) {
                            scope.update();
                        }
                    });
                    element.disableSelection();
                }
            };
        }])
        .directive('sdDraggable', ['dragDropService', function(dragDropService) {
            return {
                scope: {item: '=', container: '='},
                link: function(scope, element, attrs) {
                    element.draggable({
                        helper: 'clone',
                        appendTo: scope.container,
                        start: function(event, ui) {
                            dragDropService.item = scope.item;
                        },
                    });
                }
            };
        }])
        .directive('sdDroppable', ['dragDropService', function(dragDropService) {
            return {
                scope: {update: '='},
                link: function(scope, element, attrs) {
                    element.droppable({
                        accept: ':not(.ui-sortable-helper)',
                        drop: function(event, ui) {
                            scope.update(dragDropService.item);
                            dragDropService.item = null;
                        }
                    });
                }
            };
        }]);
});