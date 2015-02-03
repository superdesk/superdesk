define(['angular'], function(angular) {
    'use strict';

    return angular.module('superdesk.select.directives', ['superdesk.asset'])

    .factory('optionParser', ['$parse', function ($parse) {

        var TYPEAHEAD_REGEXP = /^\s*(.*?)(?:\s+as\s+(.*?))?\s+for\s+(?:([\$\w][\$\w\d]*))\s+in\s+(.*)$/;

        return {
            parse: function (input) {

                var match = input.match(TYPEAHEAD_REGEXP);
                if (!match) {
                    throw new Error(
                    'Expected typeahead specification in form of _modelValue_ (as _label_)? for _item_ in _collection_' +
                      ' but got ' + input + '.');
                }

                return {
                    itemName: match[3],
                    source: $parse(match[4]),
                    viewMapper: $parse(match[2] || match[1]),
                    modelMapper: $parse(match[1])
                };
            }
        };
    }])

    /**
     * sdSelect renders custom inpu type select with ability to select multiple items
     *
     * Usage:
     * <sd-select multiple="true" ng-model="model" options="c.name for c in collection" change="action()"></sd-multiselect>
     */
    .directive('sdSelect', ['$parse', '$document', '$compile', 'optionParser',

    function ($parse, $document, $compile, optionParser) {
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function (originalScope, element, attrs, modelCtrl) {

                var exp = attrs.options,
                parsedResult = optionParser.parse(exp),
                isMultiple = attrs.multiple ? true : false,
                required = false,
                scope = originalScope.$new(),
                changeHandler = attrs.change || angular.noop;

                scope.items = [];
                scope.header = 'Select';
                scope.multiple = isMultiple;
                scope.disabled = false;
                scope.showfilter = attrs.showfilter ? true : false;

                originalScope.$on('$destroy', function () {
                    scope.$destroy();
                });

                var popUpEl = angular.element('<div sd-select-popup></div>');

                //required validator
                if (attrs.required || attrs.ngRequired) {
                    required = true;
                }
                attrs.$observe('required', function(newVal) {
                    required = newVal;
                });

                //watch disabled state
                scope.$watch(function () {
                    return $parse(attrs.disabled)(originalScope);
                }, function (newVal) {
                    scope.disabled = newVal;
                });

                //watch single/multiple state for dynamically change single to multiple
                scope.$watch(function () {
                    return $parse(attrs.multiple)(originalScope);
                }, function (newVal) {
                    isMultiple = newVal || false;
                });

                //watch option changes for options that are populated dynamically
                scope.$watch(function () {
                    return parsedResult.source(originalScope);
                }, function (newVal) {
                    if (angular.isDefined(newVal)) {
                        parseModel();
                    }
                }, true);

                //watch model change
                scope.$watch(function () {
                    return modelCtrl.$modelValue;
                }, function (newVal, oldVal) {
                    //when directive initialize, newVal usually undefined. Also, if model value already set in the controller
                    //for preselected list then we need to mark checked in our scope item. But we don't want to do this every time
                    //model changes. We need to do this only if it is done outside directive scope, from controller, for example.
                    if (angular.isDefined(newVal)) {
                        markChecked(newVal);
                        scope.$eval(changeHandler);
                    }
                    getHeaderText();
                    modelCtrl.$setValidity('required', scope.valid());
                }, true);

                function parseModel() {
                    scope.items.length = 0;
                    var model = parsedResult.source(originalScope);
                    if (!angular.isDefined(model)) { return; }
                    for (var i = 0; i < model.length; i++) {
                        var local = {};
                        local[parsedResult.itemName] = model[i];
                        scope.items.push({
                            label: parsedResult.viewMapper(local),
                            model: parsedResult.modelMapper(local),
                            checked: false
                        });
                    }
                }

                parseModel();

                element.append($compile(popUpEl)(scope));

                function getHeaderText() {
                    if (is_empty(modelCtrl.$modelValue)) {
                        scope.header = 'Select';
                        return scope.header;
                    }

                    if (isMultiple) {
                        scope.header = modelCtrl.$modelValue.length + ' ' + 'selected';
                    } else {
                        var local = {};
                        local[parsedResult.itemName] = modelCtrl.$modelValue;
                        scope.header = parsedResult.viewMapper(local);
                    }
                }

                function is_empty(obj) {
                    if (!obj) { return true; }
                    if (obj.length && obj.length > 0) { return false; }
                    for (var prop in obj) {
                        if (obj[prop]) { return false; }
                    }
                    return true;
                }

                scope.valid = function validModel() {
                    if (!required) { return true; }
                    var value = modelCtrl.$modelValue;
                    return (angular.isArray(value) && value.length > 0) || (!angular.isArray(value) && value !== null);
                };

                function selectSingle(item) {
                    if (item.checked) {
                        scope.uncheckAll();
                    } else {
                        scope.uncheckAll();
                        item.checked = !item.checked;
                    }
                    setModelValue(false);
                }

                function selectMultiple(item) {
                    item.checked = !item.checked;
                    setModelValue(true);
                }

                function setModelValue(isMultiple) {
                    var value;

                    if (isMultiple) {
                        value = [];
                        angular.forEach(scope.items, function (item) {
                            if (item.checked) { value.push(item.model); }
                        });
                    } else {
                        angular.forEach(scope.items, function (item) {
                            if (item.checked) {
                                value = item.model;
                                return false;
                            }
                        });
                    }
                    modelCtrl.$setViewValue(value);
                }

                function markChecked(newVal) {
                    if (!angular.isArray(newVal)) {
                        angular.forEach(scope.items, function (item) {
                            if (angular.equals(item.model, newVal)) {
                                item.checked = true;
                                return false;
                            }
                        });
                    } else {
                        angular.forEach(newVal, function (i) {
                            angular.forEach(scope.items, function (item) {
                                if (angular.equals(item.model, i)) {
                                    item.checked = true;
                                }
                            });
                        });
                    }
                }

                scope.checkAll = function () {
                    if (!isMultiple) { return; }
                    angular.forEach(scope.items, function (item) {
                        item.checked = true;
                    });
                    setModelValue(true);
                };

                scope.uncheckAll = function () {
                    angular.forEach(scope.items, function (item) {
                        item.checked = false;
                    });
                    setModelValue(true);
                };

                scope.select = function (item) {
                    if (isMultiple === false) {
                        selectSingle(item);
                        scope.toggleSelect();
                    } else {
                        selectMultiple(item);
                    }
                };
            }
        };
    }])

    .directive('sdSelectPopup', ['$document', 'asset', function ($document, asset) {
        return {
            restrict: 'A',
            scope: false,
            replace: true,
            templateUrl: asset.templateUrl('superdesk/views/sdselect.html'),
            link: function (scope, element, attrs) {

                scope.open = false;

                scope.toggleSelect = function () {
                    scope.open = !scope.open;
                    if (scope.open) {
                        scope.focus();
                    }
                };

                scope.focus = function focus() {
                    var searchBox = element.find('input')[0];
                    searchBox.focus();
                };
            }
        };
    }]);
});
