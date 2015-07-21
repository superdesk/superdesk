
module.exports = {
    app: {
        src: [
            '<%= appDir %>/scripts/**/*.js',
            '!<%= appDir %>/scripts/bower_components/**/*',
            '!<%= appDir %>/scripts/translations.js',
            '!**/*spec.js'
        ],
        envs: ['browser', 'amd']
    },
    specs: {
        src: ['<%= specDir %>', '<%= appDir %>/**/*spec.js'],
        envs: ['node', 'jasmine']
    },
    tasks: {
        src: '<%= tasksDir %>',
        envs: ['node']
    },
    root: {
        src: '*.js',
        envs: ['node']
    }
};
