(function() {

'use strict';

MetadataCtrl.$inject = [
    '$scope', 'desks', 'metadata', '$filter', 'privileges', 'datetimeHelper',
    'preferencesService', 'archiveService'
];
function MetadataCtrl(
    $scope, desks, metadata, $filter,
    privileges, datetimeHelper, preferencesService, archiveService) {

    desks.initialize()
    .then(function() {
        $scope.deskLookup = desks.deskLookup;
        $scope.userLookup = desks.userLookup;
    });

    metadata.initialize().then(function() {
        $scope.metadata = metadata.values;
        return preferencesService.get();
    })
    .then(setAvailableCategories);

    $scope.processGenre = function() {
        $scope.item.genre = _.map($scope.item.genre, function(g) {
            return _.pick(g, 'name');
        });
    };

    $scope.disableAddingTargetedFor = function() {
        return !$scope.item._editable || angular.isUndefined($scope.item.targeted_for_value) || $scope.item.targeted_for_value === '';
    };

    $scope.addTargeted = function() {
        if (angular.isUndefined($scope.item.targeted_for)) {
            $scope.item.targeted_for = [];
        }

        if (!angular.isUndefined($scope.item.targeted_for_value) && $scope.item.targeted_for_value !== '') {
            var targeted_for = {'name': $scope.item.targeted_for_value};

            if (angular.isUndefined(_.find($scope.item.targeted_for, targeted_for))) {
                targeted_for.allow = angular.isUndefined($scope.item.negation) ? true : !$scope.item.negation;
                $scope.item.targeted_for.push(targeted_for);
                $scope.autosave($scope.item);
            }
        }

    };

    $scope.removeTargeted = function(to_remove) {
        if (angular.isDefined(_.find($scope.item.targeted_for, to_remove))) {
            $scope.item.targeted_for = _.without($scope.item.targeted_for, to_remove);
            $scope.autosave($scope.item);
        }
    };

    /**
    * Builds a list of categories available for selection in scope. Used by
    * the "category" menu in the Authoring metadata section.
    *
    * @function setAvailableCategories
    * @param {Object} prefs - user preferences setting, including the
    *   preferred categories settings, among other things
    */
    function setAvailableCategories(prefs) {
        var all,        // all available categories
            assigned = {},   // category codes already assigned to the article
            filtered,
            itemCategories,  // existing categories assigned to the article

            // user's category preference settings , i.e. a map
            // object (<category_code> --> true/false)
            userPrefs;

        all = metadata.values.categories || [];
        userPrefs = prefs['categories:preferred'].selected || {};

        // gather article's existing category codes
        itemCategories = $scope.item.anpa_category || [];

        itemCategories.forEach(function (cat) {
            assigned[cat.qcode] = true;
        });

        filtered = _.filter(all, function (cat) {
            return userPrefs[cat.qcode] || assigned[cat.qcode];
        });

        $scope.availableCategories = filtered;
    }

    $scope.$watch('item.publish_schedule_date', function(newValue, oldValue) {
        setPublishScheduleDate(newValue, oldValue);
    });

    $scope.$watch('item.publish_schedule_time', function(newValue, oldValue) {
        setPublishScheduleDate(newValue, oldValue);
    });

    function setPublishScheduleDate(newValue, oldValue) {
        if (newValue !== oldValue) {
            if ($scope.item.publish_schedule_date && $scope.item.publish_schedule_time) {
                $scope.item.publish_schedule = datetimeHelper.mergeDateTime($scope.item.publish_schedule_date,
                    $scope.item.publish_schedule_time).format();
            } else {
                $scope.item.publish_schedule = null;
            }

            $scope.autosave($scope.item);
        }
    }

    $scope.$watch('item.embargo_date', function(newValue, oldValue) {
        setEmbargoTS(newValue, oldValue);
    });

    $scope.$watch('item.embargo_time', function(newValue, oldValue) {
        setEmbargoTS(newValue, oldValue);
    });

    /**
     * Listener method which gets invoked when either Embargo Date or Embargo Time has changed. This function takes
     * values of both Embargo Date and Embargo Time to form Timestamp.
     */
    function setEmbargoTS(newValue, oldValue) {
        if (newValue !== oldValue) {
            if ($scope.item.embargo_date && $scope.item.embargo_time) {
                $scope.item.embargo = datetimeHelper.mergeDateTime(
                    $scope.item.embargo_date, $scope.item.embargo_time).format();
            } else {
                $scope.item.embargo = null;
            }

            $scope.autosave($scope.item);
        }
    }

    /**
     * Publish Schedule and Embargo are saved as Timestamps in DB but each field has date and time as two different
     * inputs in UI. This function breaks the timestamp fetched from API to Date and Time and assigns those values to
     * the appropriate field.
     */
    function resolvePublishScheduleAndEmbargoTS() {
        if ($scope.item.embargo) {
            var embargoTS = new Date(Date.parse($scope.item.embargo));
            $scope.item.embargo_date = $filter('formatDateTimeString')(embargoTS, 'MM/DD/YYYY');
            $scope.item.embargo_time = $filter('formatDateTimeString')(embargoTS, 'HH:mm:ss');
        }

        if ($scope.item.publish_schedule) {
            var publishSchedule = new Date(Date.parse($scope.item.publish_schedule));
            $scope.item.publish_schedule_date = $filter('formatDateTimeString')(publishSchedule, 'MM/DD/YYYY');
            $scope.item.publish_schedule_time = $filter('formatDateTimeString')(publishSchedule, 'HH:mm:ss');
        }
    }

    $scope.unique_name_editable = Boolean(privileges.privileges.metadata_uniquename);
    resolvePublishScheduleAndEmbargoTS();
}

MetadataDropdownDirective.$inject = ['$timeout'];
function MetadataDropdownDirective($timeout) {
    return {
        scope: {
            list: '=',
            disabled: '=ngDisabled',
            item: '=',
            field: '@',
            icon: '@',
            label: '@',
            change: '&'
        },
        templateUrl: 'scripts/superdesk-authoring/metadata/views/metadata-dropdown.html',
        link: function(scope) {
            scope.select = function(item) {
                var o = {};

                if (angular.isDefined(item)) {
                    o[scope.field] = (scope.field === 'place' || scope.field === 'genre') ? [item] : item.value;
                } else {
                    o[scope.field] = null;
                }

                _.extend(scope.item, o);
                scope.change({item: scope.item});
            };

            $timeout(function() {
                if (scope.list && scope.field === 'place') {
                    scope.places = _.groupBy(scope.list, 'group');
                }
            });
        }
    };
}

MetadataWordsListEditingDirective.$inject = ['$timeout'];
function MetadataWordsListEditingDirective($timeout) {
    return {
        scope: {
            item: '=',
            field: '@',
            disabled: '=',
            list: '=',
            change: '&',
            header: '@'
        },
        templateUrl: 'scripts/superdesk-authoring/metadata/views/metadata-words-list.html',
        link: function(scope, element) {
            scope.words = [];
            scope.selectedTerm = '';

            $timeout(function() {
                element.find('input, select').addClass('line-input');

                if (scope.list) {
                    scope.words = scope.list;
                }
            });

            /**
             * sdTypeahead directive invokes this method and is responsible for searching word(s) where the word.name
             * matches word_to_find.
             *
             * @return {Array} list of word(s)
             */
            scope.search = function(word_to_find) {
                if (!word_to_find) {
                    scope.words = scope.list;
                } else {
                    scope.words = _.filter(scope.list, function (t) {
                        return ((t.name.toLowerCase().indexOf(word_to_find.toLowerCase()) !== -1));
                    });
                }

                scope.selectedTerm = word_to_find;
                return scope.words;
            };

            /**
             * sdTypeahead directive invokes this method and is responsible for updating the item with user selected
             * word.
             *
             * @param {Object} item selected word object
             */
            scope.select = function(item) {
                var keyword = item ? item.value : scope.selectedTerm;
                var t = _.clone(scope.item[scope.field]) || [];
                var index = _.findIndex(t, function (word) {
                    return word.toLowerCase() === keyword.toLowerCase();
                });

                if (index < 0) {
                    t.push(keyword);

                    var o = {};
                    o[scope.field] = t;
                    _.extend(scope.item, o);
                    scope.change({item: scope.item});
                }

                scope.selectedTerm = '';
            };

            /**
             * Removes the term from the user selected terms
             */
            scope.removeTerm = function(term) {
                var temp = _.without(scope.item[scope.field], term);

                //build object
                var o = {};
                o[scope.field] = temp;

                _.extend(scope.item, o);

                scope.change({item: scope.item});
            };
        }
    };
}

/**
 * Wraping  'sd-typeahead' directive for editing of metadata list attributes
 *
 * @param {Object} item - specify the content item itself
 * @param {String} field - specify the (metadata) filed under the item which will be edited
 * @param {Boolean} disabled - whether component should be disabled for editing or not
 * @param {Array} list - list of available values that can be added
 * @param {String} unique - specify the name of the field, in list item which is unique (qcode, value...)
 *
 */
MetadataListEditingDirective.$inject = ['metadata'];
function MetadataListEditingDirective(metadata) {
    return {
        scope: {
            item: '=',
            field: '@',
            disabled: '=ngDisabled',
            list: '=',
            unique: '@',
            postprocessing: '&',
            change: '&',
            header: '@'
        },
        templateUrl: 'scripts/superdesk-authoring/metadata/views/metadata-terms.html',
        link: function(scope) {
            metadata.subjectScope = scope;

            scope.$watch('list', function(items) {
                if (
                    !items || items.length === 0
                ) {
                    return;
                }

                var tree = {};
                angular.forEach(items, function(item) {
                    if (!tree.hasOwnProperty(item.parent)) {
                        tree[item.parent] = [item];
                    } else {
                        tree[item.parent].push(item);
                    }
                });

                scope.terms = items;
                scope.tree = tree;
                scope.activeTree = tree[null];
            });

            scope.$on('$destroy', function() {
                metadata.subjectScope = null;
            });

            scope.openParent = function(term, $event) {
                var parent = _.find(scope.list, {qcode: term.parent});
                scope.openTree(parent, $event);
            };

            scope.openTree = function(term, $event) {
                scope.activeTerm = term;
                scope.activeTree = scope.tree[term ? term.qcode : null];
                $event.stopPropagation();
            };

            scope.activeList = false;
            scope.selectedTerm = '';
            var uniqueField = scope.unique || 'qcode';

            scope.searchTerms = function(term) {
                if (!term) {
                    scope.terms = scope.list;
                    scope.activeList = false;
                } else {
                    scope.terms = _.filter(scope.list, function(t) {
                        var searchObj = {};
                        searchObj[uniqueField] = t[uniqueField];
                        scope.activeList = true;
                        return ((t.name.toLowerCase().indexOf(term.toLowerCase()) !== -1) &&
                            !_.find(scope.item[scope.field], searchObj));
                    });
                }
                return scope.terms;
            };

            scope.selectTerm = function(term) {
                if (term) {

                    //instead of simple push, extend the item[field] in order to trigger dirty $watch
                    var t = _.clone(scope.item[scope.field]) || [];
                    t.push(term);

                    //build object
                    var o = {};
                    o[scope.field] = t;
                    _.extend(scope.item, o);

                    scope.selectedTerm = '';

                    scope.postprocessing();
                    scope.change({item: scope.item});
                }
            };

            scope.removeTerm = function(term) {
                var tempItem = {},
                    subjectCodesArray = scope.item[scope.field],
                    filteredArray = _.without(subjectCodesArray, term);

                if (subjectCodesArray && filteredArray.length === subjectCodesArray.length) {
                    _.remove(filteredArray, {name: term});
                }

                tempItem[scope.field] = filteredArray;
                _.extend(scope.item, tempItem);
                scope.change({item: scope.item});
            };
        }
    };
}

MetadataLocatorsDirective.$inject = ['$timeout'];
function MetadataLocatorsDirective($timeout) {
    return {
        scope: {
            item: '=',
            fieldprefix: '@',
            field: '@',
            disabled: '=ngDisabled',
            list: '=',
            change: '&',
            postprocessing: '&',
            header: '@'
        },

        templateUrl: 'scripts/superdesk-authoring/metadata/views/metadata-locators.html',
        link: function(scope, element) {
            scope.selectedTerm = '';

            $timeout(function() {
                if (scope.item) {
                    if (scope.fieldprefix && scope.item[scope.fieldprefix][scope.field]) {
                        scope.selectedTerm = scope.item[scope.fieldprefix][scope.field].city;
                    } else if (scope.item[scope.field]) {
                        scope.selectedTerm = scope.item[scope.field].city;
                    }
                }

                if (scope.list) {
                    scope.locators = scope.list;
                }
            });

            /**
             * sdTypeahead directive invokes this method and is responsible for searching located object(s) where the
             * city name matches locator_to_find.
             *
             * @return {Array} list of located object(s)
             */
            scope.searchLocator = function(locator_to_find) {
                if (!locator_to_find) {
                    scope.locators = scope.list;
                } else {
                    scope.locators = _.filter(scope.list, function(t) {
                        return ((t.city.toLowerCase().indexOf(locator_to_find.toLowerCase()) !== -1));
                    });
                }

                scope.selectedTerm = locator_to_find;
                return scope.locators;
            };

            /**
             * sdTypeahead directive invokes this method and is responsible for updating the item with user selected
             * located object.
             *
             * @param {Object} locator user selected located object
             */
            scope.selectLocator = function(locator) {
                var updates = {};

                if (!locator && scope.selectedTerm) {
                    var previousLocator = scope.fieldprefix ? scope.item[scope.fieldprefix][scope.field] :
                                            scope.item[scope.field];

                    if (scope.selectedTerm === previousLocator.city) {
                        locator = previousLocator;
                    } else {
                        locator = {'city': scope.selectedTerm, 'city_code': scope.selectedTerm, 'tz': 'UTC',
                            'dateline': 'city', 'country': '', 'country_code': '', 'state_code': '', 'state': ''};
                    }
                }

                if (locator) {
                    if (angular.isDefined(scope.fieldprefix)) {
                        updates[scope.fieldprefix] = scope.item[scope.fieldprefix];
                        updates[scope.fieldprefix][scope.field] = locator;
                    } else {
                        updates[scope.field] = locator;
                    }

                    scope.selectedTerm = locator.city;
                    _.extend(scope.item, updates);
                }

                var selectedLocator = {item: scope.item, city: scope.selectedTerm};

                scope.postprocessing(selectedLocator);
                scope.change(selectedLocator);
            };
        }
    };
}

MetadataService.$inject = ['api', '$q'];
function MetadataService(api, $q) {

    var service = {
        values: {},
        subjectScope: null,
        loaded: null,
        fetchMetadataValues: function() {
            var self = this;

            return api('vocabularies').query().then(function(result) {
                _.each(result._items, function(vocabulary) {
                    self.values[vocabulary._id] = vocabulary.items;
                });

                self.values.targeted_for = _.union(self.values.geographical_restrictions, self.values.subscriber_types);
            });
        },
        fetchSubjectcodes: function(code) {
            var self = this;
            return api.get('/subjectcodes').then(function(result) {
                self.values.subjectcodes = result._items;
            });
        },
        removeSubjectTerm: function(term) {
            var self = this,
                tempItem = {},
                subjectCodesArray = self.subjectScope.item[self.subjectScope.field],
                filteredArray = _.without(subjectCodesArray, term);

            if (filteredArray.length === subjectCodesArray.length) {
                _.remove(filteredArray, {name: term});
            }

            tempItem[self.subjectScope.field] = filteredArray;

            _.extend(self.subjectScope.item, tempItem);

            self.subjectScope.change({item: self.subjectScope.item});
        },
        fetchCities: function() {
            var self = this;
            return api.get('/cities').then(function(result) {
                self.values.cities = result._items;
            });
        },
        initialize: function() {
            if (!this.loaded) {
                this.loaded = this.fetchMetadataValues()
                    .then(angular.bind(this, this.fetchSubjectcodes))
                    .then(angular.bind(this, this.fetchCities));
            }

            return this.loaded;
        }
    };

    return service;
}

angular.module('superdesk.authoring.metadata', ['superdesk.authoring.widgets'])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('metadata', {
                icon: 'info',
                label: gettext('Info'),
                removeHeader: true,
                template: 'scripts/superdesk-authoring/metadata/views/metadata-widget.html',
                order: 1,
                side: 'right',
                display: {authoring: true, packages: true, legalArchive: true}
            });
    }])

    .controller('MetadataWidgetCtrl', MetadataCtrl)
    .service('metadata', MetadataService)
    .directive('sdMetaTerms', MetadataListEditingDirective)
    .directive('sdMetaDropdown', MetadataDropdownDirective)
    .directive('sdMetaWordsList', MetadataWordsListEditingDirective)
    .directive('sdMetaLocators', MetadataLocatorsDirective);
})();
