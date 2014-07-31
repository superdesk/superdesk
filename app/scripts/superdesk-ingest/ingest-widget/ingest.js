define([
    'angular',
    'require'
], function(angular, require) {
    'use strict';

    var INGEST_EVENT = 'changes in media_archive';

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
        .controller('IngestController', ['$location', '$scope', 'superdesk', 'api', 'es',
        function ($location, $scope, superdesk, api, es) {
            var config;
            var refresh = _.debounce(_refresh, 1000);

            $scope.$on(INGEST_EVENT, refresh);

            $scope.$watchGroup({
                provider: 'widget.configuration.provider',
                size: 'widget.configuration.maxItems',
                q: 'widget.configuration.search',
                item: 'item.headline'
            }, function(vals) {
                config = $scope.widget.configuration || {};
                refresh();
            });

            function _refresh() {
                var params = {
                    q: config.search || undefined,
                    size: config.maxItems || 10
                };

                var filters = [];
                if (config.provider && config.provider !== 'all') {
                    filters.push({term: {provider: config.provider}});
                }

                if ($scope.item) {
                    var itemFilters = moreLikeThis($scope.item);
                    if (itemFilters.length) {
                        filters.push({or: moreLikeThis($scope.item)});
                    }
                }

                var criteria = es(params, filters);
                criteria.sort = [{firstcreated: 'desc'}];
                api.ingest.query({source: criteria}).then(function(items) {
                    $scope.items = items;
                });
            }

            function moreLikeThis(item) {
                var filters = [];

                if (item.slugline) {
                    filters.push({term: {slugline: item.slugline}});
                }

                if (item.subject && item.subject.length) {
                    filters.push({terms: {'subject.code': _.pluck(item.subject, 'code')}});
                }

                if (item.headline) {
                    filters.push({query: {query_string: {query: item.headline}}});
                }

                return filters;
            }

            $scope.view = function(item) {
                //superdesk.intent(superdesk.ACTION_VIEW, 'ingest', item);
                $location.path('/ingest');
                $location.search('_id', item._id);
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
