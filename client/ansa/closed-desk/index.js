import './styles.scss';

RoutingWidgetController.$inject = ['desks', 'privileges', 'api', 'notify', 'gettext', '$scope'];
function RoutingWidgetController(desks, privileges, api, notify, gettext, $scope) {
    this.canManage = privileges.privileges.desks;

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

    this.toggle = () => {
        api.update('closed_desks', this.desk, {is_closed: !this.desk.is_closed})
            .then((updated) => {
                angular.extend(this.desk, {
                    _etag: updated._etag,
                    is_closed: updated.is_closed,
                });
            }, errorHandler);
    };

    this.updateDestination = () => {
        const updates = {closed_destination: this.destination};

        desks.save(this.desk, updates)
            .then((updated) => {
                angular.extend(this.desk, updated);
            }, errorHandler);
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

export default angular.module('ansa.closed', [])
    .controller('RoutingWidgetController', RoutingWidgetController)
    .config(['dashboardWidgetsProvider', (dashboardWidgets) => {
        dashboardWidgets.addWidget('close-desk', {
            label: gettext('Desk Router'),
            icon: 'switches',
            max_sizex: 1,
            max_sizey: 1,
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