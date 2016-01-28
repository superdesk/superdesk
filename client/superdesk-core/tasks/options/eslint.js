
module.exports = {
    app: {
        src: [
            '<%= appDir %>/*.js',
            '<%= coreDir %>/apps/**/*.js'
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
