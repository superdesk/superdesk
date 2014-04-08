
module.exports = {
    compile: {
        options: {
            baseUrl: '<%= appDir %>/scripts/',
            mainConfigFile: '<%= appDir %>/scripts/config.js',

            name: 'main',
            out: '<%= distDir %>/scripts/main.js',

            include: [
                'main',
                'superdesk/filters/all',
                'superdesk/services/all',
                'superdesk/directives/all',
                'superdesk/auth/auth',
                'superdesk/data/data',
                'superdesk/datetime/datetime',

                'superdesk-items/module',
                'superdesk-users/module',
                'superdesk-settings/module',
                'superdesk-dashboard/module',
                'superdesk-desks/module',
                'superdesk-archive/module',
                'superdesk-scratchpad/module',
                'superdesk-planning/module'
            ]
        }
    }
};
