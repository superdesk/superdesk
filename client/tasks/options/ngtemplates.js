'use strict';

module.exports = {
    app: {
        cwd: 'app',
        src: 'scripts/superdesk*/**/*.html',
        dest: '<%= distDir %>/scripts/templates-cache.js',
        options: {
            htmlmin: {
                collapseWhitespace: true,
                collapseBooleanAttributes: true
            },
            bootstrap: function(module, script) {
                return '"use strict";' +
                    'angular.module(\'superdesk.templates-cache\')' +
                    '.run([\'$templateCache\', function($templateCache) {' +
                    script + ' }]);';
            }
        }
    }
};
