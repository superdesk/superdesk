define([
    'angular',
    'require',
    './sdModal',
    './sdAutofocus',
    './sdDebounceThrottle',
    './sdPagination',
    './sdSort',
    './sdCheck',
    './sdWithParams',
    './sdSearch',
    './sdModal',
    './sdConfirm',
    './sdSelect',
    './sdPermissions',
    './sdUserAvatar',
    './sdDragDrop',
    './menu',
    './listView',
    './sdTypeahead',
    './sdNotifications'
], function(angular, require) {
    'use strict';

    return [
        require('./sdAutofocus').name,
        require('./sdDebounceThrottle').name,
        require('./sdModal').name,
        require('./sdPagination').name,
        require('./sdSort').name,
        require('./sdWithParams').name,
        require('./sdCheck').name,
        require('./sdSearch').name,
        require('./sdConfirm').name,
        require('./sdSelect').name,
        require('./sdPermissions').name,
        require('./sdUserAvatar').name,
        require('./sdDragDrop').name,
        require('./menu').name,
        require('./listView').name,
        require('./sdTypeahead').name,
        require('./sdNotifications').name
    ];
});
