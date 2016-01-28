module.exports = {
    options: {
        livereload: '<%= livereloadPort %>'
    },
    less: {
        tasks: ['style'],
        files: [
            '<%= coreDir %>/assets/styles/{,*/}*.less',
            '<%= coreDir %>/apps/**/*.less',
            '<%= appDir %>/**/*.less'
        ]
    },
    code: {
        options: {livereload: true},
        tasks: [],
        files: [
            '<%= coreDir %>/apps/superdesk*/**/*.js',
            '<%= appDir %>/**/*.js'
        ]
    },
    ngtemplates: {
        options: {livereload: true},
        tasks: [],
        files: [
            '<%= coreDir %>/apps/superdesk*/views/*.html',
            '<%= appDir %>/templates/**/*.html'
        ]
    },
    assets: {
        options: {livereload: true},
        tasks: [],
        files: [
            '<%= distDir %>/*.css',
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
