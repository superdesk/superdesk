define([
    'angular',
    'require'
], function(angular, require) {
    'use strict';

    var INGEST_EVENT = 'ingest:update';

    angular.module('superdesk.widgets.ingest', ['superdesk.authoring.widgets'])
        .config(['widgetsProvider', function(widgets) {
            widgets.widget('ingest', {
                label: 'Ingest',
                multiple: true,
                icon: 'ingest',
                max_sizex: 2,
                max_sizey: 2,
                sizex: 1,
                sizey: 2,
                thumbnail: require.toUrl('./thumbnail.png'),
                template: require.toUrl('./widget-ingest.html'),
                configurationTemplate: require.toUrl('./configuration.html'),
                configuration: {maxItems: 10, provider: 'all', search: '', updateInterval: 5},
                description: 'Ingest widget'
            });
        }])
        .config(['authoringWidgetsProvider', function(authoringWidgets) {
            authoringWidgets.widget('ingest', {
                label: gettext('Ingest'),
                icon: 'ingest',
                template: require.toUrl('./widget-ingest.html')
            });
        }])
        .factory('IngestWidgetSearchCriteria', ['es', function(es) {

            /**
             * Get filter to match items similar to given item
             */
            function moreLikeThis(item) {
                var filters = [];

                if (item.slugline) {
                    filters.push({term: {slugline: item.slugline}});
                }

                if (item.subject && item.subject.length) {
                    filters.push({terms: {'subject.code': _.pluck(item.subject, 'code')}});
                }

                return filters;
            }

            return function(config) {
                var params = {
                    q: config.search || null,
                    size: config.size || 10
                };

                var filters = [];
                if (config.provider && config.provider !== 'all') {
                    filters.push({term: {provider: config.provider}});
                }

                if (config.item && !config.search) {
                    var itemFilters = moreLikeThis(config.item);
                    if (itemFilters.length) {
                        filters.push({or: itemFilters});
                    } else {
                        params.q = config.item.headline || null;
                    }
                }

                angular.extend(this, es(params, filters));
                this.sort = [{firstcreated: 'desc'}];
            };
        }])
        .controller('IngestController', ['$location', '$scope', 'superdesk', 'api', 'IngestWidgetSearchCriteria', 'storage',
        function ($location, $scope, superdesk, api, SearchCriteria, storage) {
            var config;
            var refresh = _.debounce(_refresh, 1000);
            var pinnedList = {};

            $scope.selected = null;
            $scope.pinnedItems = storage.getItem('ingestWidget:pinned') || [];
            _.each($scope.pinnedItems, function(item) {
                pinnedList[item._id] = true;
            });
            $scope.processedItems = null;

            $scope.$on(INGEST_EVENT, function() {
                refresh();
                $scope.$digest();
            });

            $scope.$watchGroup({
                provider: 'widget.configuration.provider',
                size: 'widget.configuration.maxItems',
                search: 'query || widget.configuration.search',
                item: 'item',
                headline: 'headline'
            }, function(vals) {
                config = vals || {};
                refresh();
            });

            function processItems() {
                $scope.processedItems = $scope.pinnedItems.concat($scope.items._items);
            }

            function _refresh() {
                var criteria = new SearchCriteria(config);
                api.ingest.query({source: criteria}).then(function(items) {
                    $scope.items = items;
                    processItems();
                });
            }

            $scope.view = function(item) {
                $scope.selected = item;
            };

            $scope.go = function(item) {
                $location.path('/workspace/ingest');
                $location.search('_id', item._id);
            };

            $scope.pin = function(item) {
                var newItem = _.cloneDeep(item);
                newItem.pinnedInstance = true;
                $scope.pinnedItems.push(newItem);
                $scope.pinnedItems = _.uniq($scope.pinnedItems, '_id');
                pinnedList[item._id] = true;
                storage.setItem('ingestWidget:pinned', $scope.pinnedItems);
                processItems();
            };

            $scope.unpin = function(item) {
                _.remove($scope.pinnedItems, {_id: item._id});
                pinnedList[item._id] = false;
                storage.setItem('ingestWidget:pinned', $scope.pinnedItems);
                processItems();
            };

            $scope.isPinned = function(item) {
                return !!pinnedList[item._id];
            };
        }])
        .controller('IngestConfigController', ['$scope', 'superdesk', 'api',
        function ($scope, superdesk, api) {
            api.ingest.query({source: {size: 0}}).then(function(items) {
                $scope.availableProviders = ['all'].concat(_.pluck(items._facets.provider.terms, 'term'));
            });

            $scope.notIn = function(haystack) {
                return function(needle) {
                    return haystack.indexOf(needle) === -1;
                };
            };
        }]);
});
