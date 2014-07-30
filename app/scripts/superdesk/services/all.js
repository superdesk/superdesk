define([
    'require',
    './data',
    './translate',
    './storage',
    './permissionsService',
    './keyboardManager',
    './entity',
    './server',
    './dragDropService',
    './modalService'
], function(require) {
    'use strict';

    return [
        require('./data').name,
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
