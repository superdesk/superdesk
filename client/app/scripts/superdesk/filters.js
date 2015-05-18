define([
    'angular',
    'lodash'
], function(angular, _) {
    'use strict';

    return angular.module('superdesk.filters', []).
        filter('any', function() {
            return function(data, key) {
                return _.any(data, key);
            };
        }).
        filter('body', function() {
            return function(content) {
                var lines = $(content);
                var texts = [];
                for (var i = 0; i < lines.length; i++) {
                    var el = $(lines[i]);
                    if (el.is('p')) {
                        texts.push(el[0].outerHTML);
                    }
                }

                return texts.join('\n');
            };
        }).
        filter('mergeWords', function() {
            return function(array, propertyName) {
                var subjectMerged = [];
                _.forEach(array, function(item) {
                    var value = (propertyName == null?item:item[propertyName]);
                    if (value) {
                        subjectMerged.push(value);
                    }
                });

                return subjectMerged.join(', ');
            };
        }).
        filter('splitWords', function() {
            return function(word) {
                var split = [];
                _.forEach(word.split(','), function(w) {
                    var trim = w.replace(/^\s+|\s+$/g, '');
                    split.push({'name': trim});
                });
                return split;
            };
        }).
        filter('trusted', ['$sce', function($sce) {
            return function(value) {
                return $sce.trustAsResourceUrl(value);
            };
        }]).
        filter('filterObject', ['$filter', function($filter) {
            return function(items, fields) {
                var filtered = [];
                angular.forEach(items, function(item) {
                    filtered.push(item);
                });
                return $filter('filter')(filtered, fields);
            };
        }])
        .filter('menuGroup', function() {
            return function(input) {

                if (!input || !input.category) {
                    return '#/';
                }
                return '#' + input.href;
            };
        })
        .filter('truncateString', function() {
            return function(inputString, limit, postfix) {
                return _.trunc(inputString, {'length': limit, 'omission': postfix || '...'});
            };
        })
        .filter('dateString', ['$filter', function($filter) {
            return function(input) {
                if (input !== null) {
                    return $filter('date')(input, 'dd.MM.yyyy');
                }
            };
        }])
        .filter('dateTimeString', ['$filter', function($filter) {
            return function(input) {
                if (input !== null) {
                    return $filter('date')(input, 'dd.MM.yyyy HH:mm');
                }
            };
        }])
        .filter('dateTimeStringWithSecs', ['$filter', function($filter) {
            return function(input) {
                if (input !== null) {
                    return $filter('date')(input, 'dd.MM.yyyy HH:mm:ss');
                }
            };
        }])
        .filter('queueStatus', ['$filter', function($filter)  {
            return function(input) {
                if (input === 'pending') {
                    return 'warning';
                } else if (input === 'success') {
                    return 'success';
                } else if (input === 'error') {
                    return 'danger';
                }
            };
        }]);
});
