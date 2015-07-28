define([
    'require',
    './sdAutofocus',
    './sdDebounceThrottle',
    './sdSort',
    './sdCheck',
    './sdWithParams',
    './sdConfirm',
    './sdSelect',
    './sdPermissions',
    './sdUserAvatar',
    './sdDragDrop',
    './sdTypeahead',
    './sdSlider',
    './sdSearchList'
], function(require) {
    'use strict';

    return [
        require('./sdAutofocus').name,
        require('./sdDebounceThrottle').name,
        require('./sdSort').name,
        require('./sdWithParams').name,
        require('./sdCheck').name,
        require('./sdConfirm').name,
        require('./sdSelect').name,
        require('./sdPermissions').name,
        require('./sdUserAvatar').name,
        require('./sdDragDrop').name,
        require('./sdTypeahead').name,
        require('./sdSlider').name,
        require('./sdSearchList').name
    ];
});
