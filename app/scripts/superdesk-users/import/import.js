(function() {
'use strict';

function UserImportService(api, $q) {

    function reject(key) {
        var errors = {};
        errors[key] = 1;
        return $q.reject(errors);
    }

    this.importUser = function importUser(importUserData) {
        return api.save('import_profile', importUserData)
        .then(null, function handleErrorResponse(response) {
            if (response.status === 404) {
                return reject('profile_to_import');
            } else {
                return reject('credentials');
            }
        });
    };
}

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
