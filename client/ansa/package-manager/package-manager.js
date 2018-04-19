PackageManagerCtrl.$inject = ['$scope', 'api', 'search', 'packages', 'notify', 'gettext', 'authoring', 'lodash'];
function PackageManagerCtrl($scope, api, search, packages, notify, gettext, authoring, _) {
    let self = this;

    $scope.contentItems = [];
    $scope.packageModal = false;
    $scope.groupList = packages.groupList;

    function fetchPackages() {
        self.loading = true;

        var query = search.query();
        var linkedPackages = [];

        query.clear_filters();

        _.forEach($scope.item.linked_in_packages, (packageRef) => {
            linkedPackages.push(packageRef.package);
        });

        var filter = [
            {not: {term: {state: 'spiked'}}},
            {not: {terms: {guid: linkedPackages}}},
            {term: {type: 'composite'}},
            {range: {versioncreated: {gte: 'now-24h'}}},
        ];

        query.size(100).filter(filter);
        var criteria = query.getCriteria(true);

        let killed = {};

        criteria.repo = 'archive,published';
        api.query('search', criteria)
            .then((result) => {
                let items = result._items.sort((a, b) => {
                    if (a.versioncreated > b.versioncreated) {
                        return -1;
                    } else if (a.versioncreated < b.versioncreated) {
                        return 1;
                    }

                    return 0;
                });

                items.forEach((item) => {
                    if (item.state === 'killed') {
                        killed[item.guid] = true;
                    }
                });

                $scope.contentItems = items.filter((item) => {
                    if (!killed[item.guid]) {
                        killed[item.guid] = true;
                        return true;
                    }

                    return false;
                });
            })
            .finally(() => {
                self.loading = false;
            });
    }

    function updatePackageList(_package) {
        if ($scope.item.linked_in_packages) {
            $scope.item.linked_in_packages.push({package: _package._id});
        } else {
            $scope.item.linked_in_packages = [{package: _package._id}];
        }
        return fetchPackages();
    }

    this.addToPackage = function(pitem, group) {
        var onSuccess = function() {
            notify.success(gettext('Package Updated'));
            authoring.autosave(pitem);

            return updatePackageList(pitem);
        };

        var onError = function(error) {
            this.loading = false;
            if (angular.isDefined(error.data._message)) {
                notify.error(error.data._message);
            } else {
                notify.error(gettext('Error. The item was not added to the package.'));
            }
        };

        this.loading = true;

        if (pitem.state === 'published' || pitem.state === 'corrected') {
            return addToPublishedPackage(pitem, group, onSuccess, onError);
        }

        return addToUnpublishedPackage(pitem, group, onSuccess, onError);
    };

    function addToPublishedPackage(pitem, group, onSuccess, onError) {
        var query = {
            package_id: pitem._id,
            new_items: [{
                group: group,
                item_id: $scope.item._id,
            }],
        };

        api.save('published_package_items', query).then(onSuccess, onError);
    }

    function addToUnpublishedPackage(pitem, group, onSuccess, onError) {
        var orig = _.clone(pitem);

        packages.addItemsToPackage(pitem, group, [$scope.item]);
        api.save('archive', orig, _.pick(pitem, 'groups')).then(onSuccess, onError);
    }

    fetchPackages();
}

export default angular.module('ansa.package-manager', ['superdesk.apps.authoring.widgets'])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('packages', {
                icon: 'manage-package',
                label: gettext('Package Manager'),
                template: 'package-manager-widget.html',
                order: 6,
                side: 'right',
                display: {authoring: true, packages: false, killedItem: false, legalArchive: false, archived: false},
            });
    }])

    .run(['$templateCache', ($templateCache) => {
        $templateCache.put('package-manager-widget.html', require('./views/package-manager-widget.html'));
    }])

    .controller('PackageManagerWidgetCtrl', PackageManagerCtrl)
;
