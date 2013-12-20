module.exports = {
    build: {
        expand: true,
        cwd: '<%= appDir %>/scripts',
        dest: '<%= tmpDir %>/scripts',
        src: [
            'main.js',
            'superdesk/**/*.js',
            'superdesk-*/**/*.js'
        ]
    }
};
