module.exports = {
    options: {
        livereload: '<%= livereloadPort %>'
    },
    less: {
        tasks: ['style'],
        files: [
            '<%= appDir %>/styles/{,*/}*.less',
            '<%= appDir %>/scripts/superdesk/**/*.less',
            '<%= appDir %>/scripts/superdesk-*/**/*.less'
        ]
    },
    code: {
        options: {livereload: true},
        tasks: ['hint'],
        files: ['<%= appDir %>/scripts/**/*.js']
    },
    assets: {
        options: {livereload: true},
        tasks: ['copy:assets'],
        files: [
            '<%= appDir %>/styles/**/*.css',
            '<%= appDir %>/scripts/**/*.html'
        ]
    },
    index: {
        options: {livereload: true},
        tasks: ['template'],
        files: ['<%= appDir %>/index.html']
    }
};
