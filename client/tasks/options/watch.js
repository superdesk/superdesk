module.exports = {
    options: {
        livereload: '<%= livereloadPort %>'
    },
    less: {
        tasks: ['style'],
        files: [
            '<%= appDir %>/styles/{,*/}*.less',
            '<%= appDir %>/scripts/superdesk*/**/*.less'
        ]
    },
    code: {
        options: {livereload: true},
        tasks: ['hint'],
        files: [
            '<%= appDir %>/scripts/*.js',
            '<%= appDir %>/scripts/superdesk*/**/*.js'
        ]
    },
    assets: {
        options: {livereload: true},
        files: [
            '<%= appDir %>/styles/**/*.css',
            '<%= appDir %>/scripts/superdesk*/**/*.html',
            '<%= appDir %>/docs/**/*.html'
        ]
    },
    index: {
        options: {livereload: true},
        tasks: ['template'],
        files: ['<%= appDir %>/index.html']
    },
    less_docs: {
        options: {livereload: true},
        tasks: ['less:docs', 'cssmin'],
        files: [
            '<%= appDir %>/docs/**/*.less'
        ]
    },
    code_docs: {
        options: {livereload: true},
        tasks: ['hint:docs'],
        files: ['<%= appDir %>/docs/**/*.js']
    },
    html_docs: {
        options: {livereload: true},
        tasks: ['template:docs'],
        files: ['<%= appDir %>/docs.html']
    }
};
