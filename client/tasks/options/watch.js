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
        tasks: [],
        files: [
            '<%= appDir %>/scripts/*.js',
            '<%= appDir %>/scripts/superdesk*/**/*.js'
        ]
    },
    ngtemplates: {
        options: {livereload: true},
        tasks: [],
        files: [
            '<%= appDir %>/scripts/superdesk*/views/*.html'
        ]
    },
    assets: {
        options: {livereload: true},
        tasks: [],
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
