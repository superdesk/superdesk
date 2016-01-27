module.exports = {
    bowerCore: {
        src: [
            '<%= bowerDir %>/scripts/superdesk-core.js',
            '<%= bowerDir %>/scripts/templates-cache.js',
            '<%= bowerDir %>/scripts/superdesk.js'
        ],
        dest: '<%= bowerDir %>/scripts/superdesk-core.js'
    }
};
