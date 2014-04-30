define([
    'jquery',
    'angular',
    'jquery-ui'
], function($, angular) {
    'use strict';

    return angular.module('superdesk.dragdrop.directives', [])
        /**
         * sdSortable creates a container in which contained items can be sortable by drag/drop.
         *
         * Usage:
         * <div sd-sortable data-update="update" data-placeholder="placeholder"></div>
         *
         * Params:
         * @scope {function} update - function to call when sort is updated.
         * This function should accept an array of item indexes.
         *
         * @scope {string} placeholder - css class name for placeholder box
         * displayed during sorting.
         */
        .directive('sdSortable', [function() {
            return {
                scope: {update: '=', placeholder: '='},
                link: function(scope, element, attrs) {
                    element.sortable({
                        tolerance: 'intersect',
                        placeholder: scope.placeholder,
                        start: function(event, ui) {
                            $(event.target).data('ui-sortable').floating = true;
                        },
                        update: function(event, ui) {
                            scope.update();
                        }
                    });
                    element.disableSelection();
                }
            };
        }])
        /**
         * sdDraggable creates a draggable item. Works with sdDroppable.
         *
         * Usage:
         * <div sd-draggable data-item="item" data-container="'.container'"></div>
         *
         * Params:
         * @scope {object} item - data to be carried.
         *
         * @scope {string} container - css selector to attach dragged item to.
         */
        .directive('sdDraggable', ['dragDropService', function(dragDropService) {
            return {
                scope: {item: '=', container: '='},
                link: function(scope, element, attrs) {
                    element.draggable({
                        helper: 'clone',
                        appendTo: scope.container,
                        start: function(event, ui) {
                            dragDropService.item = scope.item;
                        }
                    });
                }
            };
        }])
        /**
         * sdDroppable marks a drop area for sdDraggable items.
         *
         * Usage:
         * <div sd-droppable data-update="update"></div>
         *
         * Params:
         * @scope {function} update - function to be called when an item is dropped.
         */
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
