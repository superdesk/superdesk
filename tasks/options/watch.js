module.exports = {
    options: {
        livereload: '<%= livereloadPort %>',
    },
    css: {
        files: [
            '<%= appDir %>/{,*/}*.html',
            '{<%= tmpDir %>,<%= appDir %>}/styles/css/custom.css',
            '{<%= tmpDir %>,<%= appDir %>}/styles/{,*/}*.less',
            '{<%= tmpDir %>,<%= appDir %>}/{,*/}*.js',
            '<%= appDir %>/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}'
        ],
        tasks: ['less']
    }
};
