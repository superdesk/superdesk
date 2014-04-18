define([
    'angular',
    'require',
    './data',
    './translate',
    './storage',
    './permissionsService',
    './keyboardManager',
    './entity',
    './server',
    './superdesk',
    './dragDropService',
    './modalService',
    './beta'
], function(angular, require) {
    'use strict';

    return [
        require('./data').name,
        require('./superdesk').name,
        require('./beta').name,
        require('./modalService').name,
        require('./dragDropService').name,
        require('./server').name,
        require('./entity').name,
        require('./keyboardManager').name,
        require('./permissionsService').name,
        require('./storage').name,
        require('./translate').name
    ];
});
