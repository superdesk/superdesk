module.exports = {
    test: {
        path: 'http://localhost:<%= connect.options.port %>'
    },
    mock: {
        path: 'http://localhost:<%= connect.mock.options.port %>'
    }
};
