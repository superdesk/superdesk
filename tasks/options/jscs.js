module.exports = {
    options: {
        config: '.jscs.json'
    },
    all: [
        'Gruntfile.js',
        '<%= appDir %>/scripts/main.js',
        '<%= appDir %>/scripts/superdesk/**/*.js',
        '<%= appDir %>/scripts/superdesk-*/**/*.js',
        'test/**/*.js',
        'spec/**/*.js'
    ]
};
