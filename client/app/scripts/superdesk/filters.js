define([
    'angular',
    'lodash',
    'moment',
    'moment-timezone'
], function(angular, _, moment) {
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
        .filter('formatDateTimeString', [function() {
            return function(input, format_string) {
                var moment_timestamp = angular.isDefined(input)? moment(input).utc() : moment.utc();
                return angular.isDefined(format_string) ? moment_timestamp.format(format_string) : moment_timestamp.format();
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
        }])
        .filter('mergeTargets', function() {
            return function(array) {
                var merged = [];
                _.forEach(array, function(item) {
                    merged.push(item.allow === false ? 'Not ' + item.name : item.name);
                });

                return merged.join(', ');
            };
        })
        .filter('previewDateline', ['$filter', function($filter) {
            return function(located, source, datelineDate) {
                if (_.isObject(located) && angular.isDefined(located.city)) {
                    var momentizedTimestamp = angular.isDefined(datelineDate) ? moment.utc(datelineDate) : moment.utc();
                    var _month = '';

                    if (angular.isDefined(located) && located.tz !== 'UTC') {
                        momentizedTimestamp = momentizedTimestamp.tz(located.tz);
                    }

                    var currentMonth = momentizedTimestamp.month() + 1;

                    if (currentMonth === 9) {
                        _month = 'Sept ';
                    } else if (currentMonth >= 3 && currentMonth <= 7) {
                        _month = momentizedTimestamp.format('MMMM');
                    } else {
                        _month = momentizedTimestamp.format('MMM');
                    }

                    return $filter('formatDatelineToLocMMMDDSrc')(located, _month, momentizedTimestamp.format('DD'), source);
                } else {
                    return '';
                }
            };
        }])
        .filter('daysInAMonth', function() {
            return function (month) {
                var _timeStamp = month ? moment((month + 1), 'MM') : moment();
                var daysInCurrMonth = [];

                for (var i = _timeStamp.startOf('month').date(); i <= _timeStamp.endOf('month').date(); i++) {
                    daysInCurrMonth.push(i < 10 ? ('0' + i) : i.toString());
                }

                return daysInCurrMonth;
            };
        })
        .filter('formatDatelineToMMDD', function() {
            return function (date_to_format, located) {
                var momentizedTimestamp = moment.utc(date_to_format);

                if (angular.isDefined(located) && located.tz !== 'UTC') {
                    momentizedTimestamp = momentizedTimestamp.tz(located.tz);
                }

                return {'month': momentizedTimestamp.month().toString(), 'day': momentizedTimestamp.format('DD')};
            };
        })
        .filter('formatDatelineToLocMMMDDSrc', function() {
            return function(located, month, date, source) {
                if (!source) {
                    source = '';
                }

                var dateline = located.city_code;
                var datelineFields = located.dateline.split(',');

                if (_.indexOf(datelineFields, 'state')) {
                    dateline.concat(', ', located.state_code);
                }

                if (_.indexOf(datelineFields, 'country')) {
                    dateline.concat(', ', located.country_code);
                }

                return dateline.toUpperCase().concat(', ', month, ' ', date, ' ', source, ' -');
            };
        })
        .filter('relativeUTCTimestamp', function() {
            return function (located, month, date) {
                var currentTSInLocated = located.tz === 'UTC' ? moment.utc() : moment().tz(located.tz);
                currentTSInLocated.month(month).date(date);

                return currentTSInLocated.toISOString();
            };
        })
        .filter('sortByName', function() {
            return function (_collection, propertyName) {
                if (!propertyName) {
                    propertyName = 'name';
                }

                _collection = _.sortBy(_collection, function (_entry) {
                    return _entry[propertyName].toLowerCase();
                });

                return _collection;
            };
        });
});
