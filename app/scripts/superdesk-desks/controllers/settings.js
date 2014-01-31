define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$scope', 'em', 'gettext', 'notify',
        function($scope, em, gettext, notify) {

			var _desk = null;
			$scope.editDesk = null;
			$scope.memberPopup = null;
            $scope.selectedMembers = [];
            $scope.membersToSelect = [];
            $scope.desk = null;
            $scope.memberScreen2 = false;

			em.getRepository('desks').matching().then(function(desks) {
				$scope.desks = desks;
			});

			em.getRepository('users').matching().then(function(users) {
				$scope.users = users._items;
			});

			$scope.getMembers = function(desk) {
				var members = [];
				if ($scope.desks !== undefined && $scope.users !== undefined) {
                    angular.forEach(desk.members, function(value) {
                        members.push(_.find($scope.users, {_id: value}));
                    });
                }
                return members;
			};

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
                _desk = null;
            };

            $scope.openMembers = function(desk) {
                $scope.desk = desk;
                $scope.memberPopup = {};
                angular.forEach(desk.members, function(value) {
                    $scope.selectedMembers.push(_.find($scope.users, {_id: value}));
                });
                $scope.membersToSelect = _.without($scope.users, $scope.selectedMembers);
            };

            $scope.cancelMember = function(desk) {
                $scope.selectedMembers = [];
                $scope.memberPopup = null;
                $scope.memberScreen2 = false;
            };

            $scope.addMember = function(member) {
                $scope.selectedMembers.push(member);
            };

            $scope.removeMember = function(member) {
                $scope.selectedMembers = _.without($scope.selectedMembers, member);
            };

            $scope.saveMembers = function() {
                $scope.desk.members = _.map($scope.selectedMembers, function(obj) { return obj._id; });
                em.update($scope.desk).then(function(result) {
					_.extend($scope.desk, result);
					notify.success(gettext('Desk members updated.'), 3000);
					$scope.cancelMember();
                });
            };

            $scope.notIn = function(array) {
                return function(item) {
                    return array.indexOf(item) === -1;
                };
            };
		}];
});
