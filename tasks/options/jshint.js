module.exports = {
    options: {
        jshintrc: '.jshintrc'
    },
    all: [
        'Gruntfile.js',
        '<%= appDir %>/scripts/main.js',
        '<%= appDir %>/scripts/superdesk/**/*.js',
        '<%= appDir %>/scripts/superdesk-*/**/*.js',
        'test/**/*.js',
        'spec/**/*.js',
        '*.js'
    ]
};
