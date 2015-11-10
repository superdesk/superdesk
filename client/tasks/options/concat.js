module.exports = {
    bowerCore: {
        src: [
            '<%= bowerDir %>/scripts/superdesk-core.js',
            '<%= bowerDir %>/scripts/templates-cache.js',
            '<%= bowerDir %>/scripts/superdesk.js'
        ],
        dest: '<%= bowerDir %>/scripts/superdesk-core.js',
    },
    bowerApps: {
        src: [
            '<%= bowerDir %>/scripts/superdesk-apps.js',
            '<%= bowerDir %>/scripts/superdesk-settings.js',
            '<%= bowerDir %>/scripts/superdesk-dashboard.js',
            '<%= bowerDir %>/scripts/superdesk-archive.js',
            '<%= bowerDir %>/scripts/superdesk-ingest.js'
        ],
        dest: '<%= bowerDir %>/scripts/superdesk-apps.js',
    }
};
