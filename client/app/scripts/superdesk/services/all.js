define([
    'require',
    './data',
    './translate',
    './storage',
    './preferencesService',
    './permissionsService',
    './keyboardManager',
    './entity',
    './server',
    './dragDropService',
    './modalService',
    './workflowService'
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
        require('./preferencesService').name,
        require('./translate').name,
        require('./workflowService').name
    ];
});
