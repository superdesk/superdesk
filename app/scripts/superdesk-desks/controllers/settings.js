define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$scope', 'em', 'gettext', 'notify',
        function($scope,em, gettext, notify) {

			var _desk = null;
			$scope.editDesk = null;

			em.getRepository('desks').matching().then(function(desks){
				$scope.desks = desks;
			});

			$scope.edit = function(desk) {
				$scope.editDesk = _.extend({}, desk);
				_desk = desk;
			};

			$scope.cancel = function() {
				$scope.editDesk = null;
			};

			$scope.save = function(desk) {
				if (!_desk) {
					em.save('desks', desk).then(function(result) {
						_.extend(desk, result);
						notify.success(gettext('New Desk created.'), 3000);
						$scope.desks._items.unshift(desk);
						$scope.cancel();
	                });
				} else {
					em.update(desk).then(function(result) {
						_.extend(_desk, result);
						notify.success(gettext('Desk settings updated.'), 3000);
						$scope.cancel();
	                });
				}
			};

			$scope.remove = function(desk) {
                em.remove(desk).then(function() {
                    _.remove($scope.desks._items, desk);
                    notify.success(gettext('Desk deleted.'), 3000);
                });
            };
		}];
});