module.exports = {
    compile: {
        options: {
            baseUrl: '<%= appDir %>/scripts',
            mainConfigFile: '<%= appDir %>/scripts/main.js',
            out: '<%= distDir %>/scripts/main.js',
            name: 'main',
            optimize: 'uglify2',
            include: [
                'main',
                'superdesk/filters/all',
                'superdesk/services/all',
                'superdesk/directives/all',
                'superdesk/auth/auth',
                'superdesk-items/module',
                'superdesk-users/module',
                'superdesk-settings/module',
                'superdesk-dashboard/module',
                'superdesk-desks/module',
                'superdesk-archive/module',
                'superdesk-scratchpad/module'
            ]
        }
    }
};
