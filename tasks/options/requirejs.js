module.exports = {
    compile: {
        options: {
            baseUrl: '<%= appDir %>/scripts',
            mainConfigFile: '<%= appDir %>/scripts/main.js',
            out: '<%= distDir %>/scripts/main.js',
            name: 'main',
            optimize: 'uglify2',
            include: [
                'superdesk/filters/all',
                'superdesk/services/all',
                'superdesk/directives/all',
                'main',
                'superdesk-auth/module',
                'superdesk-menu/module',
                'superdesk-items/module',
                'superdesk-users/module',
                'superdesk-settings/module',
                'superdesk-dashboard/module',
                'superdesk-desks/module'
            ]
        }
    }
};
