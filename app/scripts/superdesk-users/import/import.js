(function() {
'use strict';

UserImportService.$inject = ['api', '$q'];
function UserImportService(api, $q) {

    function reject(key, message){
        var error = {};
        error[key] = 1;
        error.message = message;
        return $q.reject(error);
    }

    this.importUser = function importUser(importUserData) {
        return api.save('import_profile', importUserData)
        .then(null, function handleErrorResponse(response) {
            var data = response.data;
            if (response.status === 404) {
                return reject('profile_to_import', data._message);
            } else if (response.status === 400) {
                return reject(data._issues.profile_to_import ? 'profile_to_import': 'credentials', data._message);
            } else {
                return reject('credentials', data._message);
            }
        });
    };
}

UserImportController.$inject = ['$scope', 'userImport'];
function UserImportController($scope, userImport) {

    $scope.model = {};
    $scope.error = null;

    $scope.importUser = function importUser(user) {
        $scope.error = null;
        userImport.importUser(user)
            .then(function finishImport(user) {
                $scope.resolve(user);
            }, function renderErrors(error) {
                $scope.error = error;
            });
    };
}

angular.module('superdesk.users.import', ['superdesk.activity', 'superdesk.api'])
    .service('userImport', UserImportService)
    .config(['superdeskProvider', function(superdeskProvider) {
        superdeskProvider
            .activity('import.user', {
                label: gettext('Import user'),
                modal: true,
                controller: UserImportController,
                templateUrl: 'scripts/superdesk-users/import/views/import-user.html',
                filters: [{action: 'create', type: 'user'}],
                features: {import_profile: 1}
            });
    }]);

})();
