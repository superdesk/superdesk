import {get, debounce} from 'lodash';

import './styles.scss';

RoutingWidgetController.$inject = ['desks', 'privileges', 'api', 'notify', 'gettext', '$scope'];
function RoutingWidgetController(desks, privileges, api, notify, gettext, $scope) {
    this.canManage = privileges.privileges.desk_routing;

    desks.initialize().then(() => {
        this.desk = desks.getCurrentDesk();
        if (!this.desk) { // only works in desk context
            return;
        }

        this.desks = desks.desks._items.filter((desk) => desk._id !== this.desk._id);
        this.destination = this.desk.closed_destination || null;
        this.destinationName = this.destination && this.desks.find((desk) => desk._id === this.destination).name;

        this.routedFrom = this.desks.filter((desk) => desk.closed_destination === this.desk._id);
    });

    const errorHandler = (reason) => {
        if (reason.status === 412) {
            notify.warning('Desk status is outdated, please refresh.');
        } else {
            console.error('unknown error', reason);
        }
    };

    const updateDesk = (updates) => {
        api.update('closed_desks', this.desk, updates)
            .then((updated) => {
                angular.extend(this.desk, {
                    _etag: updated._etag,
                    is_closed: updated.is_closed,
                    closed_destination: updated.closed_destination,
                });
            }, errorHandler);
    };

    this.toggle = () => {
        updateDesk({is_closed: !this.desk.is_closed});
    };

    this.updateDestination = () => {
        updateDesk({closed_destination: this.destination});
    };

    // update desk closed status
    $scope.$on('desks:closed', (event, extra) => {
        // update open/close status for routedFrom
        this.routedFrom.forEach((desk) => {
            desk._id === extra._id && angular.extend(desk, {is_closed: extra.is_closed});
        });

        // update open/close status for current desk
        if (extra._id === this.desk._id) {
            angular.extend(this.desk, extra);
        }

        // re-render
        $scope.$apply();
    });
}


TopMenuInfoDirective.$inject = ['desks', '$timeout'];
function TopMenuInfoDirective(desks, $timeout) {
    return {
        template: require('./views/top-menu-info.html'),
        link: (scope) => {
            const setup = debounce(() => {
                const desk = desks.getCurrentDesk();
                const selected = document.getElementById('selected-desk');

                selected && selected.classList.remove('desk--closed');
                scope.routingFrom = scope.routingTo = null;

                if (!desk) {
                    return;
                }

                scope.$applyAsync(() => { // using debounce, so it must trigger angular rendering
                    if (desk.is_closed) {
                        scope.routingTo = get(desks.deskLookup[desk.closed_destination], 'name', '');
                        selected && selected.classList.add('desk--closed');
                    } else {
                        scope.routingFrom = getRoutingFrom(desk);
                    }
                });

                // it can only run when dropdown is rendered
                $timeout(setDeskItemDropdownStatus, 500, false);
            }, 200);

            function getRoutingFrom(desk) {
                return desks.desks._items
                    .filter((d) => d.closed_destination === desk._id && d.is_closed)
                    .map((d) => d.name)
                    .join(', ');
            }

            function setDeskItemDropdownStatus() {
                desks.desks._items.forEach((d) => {
                    const btn = document.getElementById('desk-item-' + d._id);

                    if (!btn) { // user is not a member
                        return;
                    }

                    btn.classList.remove('desk-item--closed', 'desk-item--receiving');

                    if (d.is_closed) {
                        btn.classList.add('desk-item--closed');
                    } else if (getRoutingFrom(d)) {
                        btn.classList.add('desk-item--receiving');
                    }
                });
            }

            desks.initialize().then(() => {
                scope.$watch(desks.getCurrentDeskId.bind(desks), setup);

                scope.$on('desks:closed', (event, extra) => {
                    desks.fetchDeskById(extra._id).then((desk) => {
                        desks.desks._items = desks.desks._items
                            .map((d) => d._id === desk._id ? angular.extend(d, desk) : d);
                        desks.deskLookup[desk._id] = desk;
                        scope.$applyAsync(setup);
                    });
                });

                scope.$on('$routeChangeSuccess', setup);
            });
        },
    };
}

export default angular.module('ansa.closed', [])
    .controller('RoutingWidgetController', RoutingWidgetController)
    .directive('sdTopMenuInfoPlaceholder', TopMenuInfoDirective)
    .config(['dashboardWidgetsProvider', (dashboardWidgets) => {
        dashboardWidgets.addWidget('close-desk', {
            label: gettext('Desk Router'),
            icon: 'switches',
            max_sizex: 1,
            max_sizey: 2,
            sizex: 1,
            sizey: 1,
            template: 'close-desk-widget.html',
            description: 'Close desk widget',
        });
    }])
    .run(['$templateCache', ($templateCache) => {
        $templateCache.put(
            'close-desk-widget.html',
            require('./views/close-desk-widget.html')
        );
    }])
;
