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
        files: [
            '<%= appDir %>/styles/**/*.css',
            '<%= appDir %>/scripts/**/*.html'
        ]
    },
    index: {
        options: {livereload: true},
        tasks: ['template'],
        files: ['<%= appDir %>/index.html', '<%= appDir %>/docs.html']
    },
    less_docs: {
        options: {livereload: true},
        tasks: ['less:docs'],
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
        tasks: [],
        files: ['<%= appDir %>/docs/**/*.html']
    }
};
