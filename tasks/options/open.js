module.exports = {
    test: {
        path: 'http://<%= connect.options.hostname %>:<%= connect.options.port %>'
    },
    mock: {
        path: 'http://<%= connect.options.hostname %>:<%= connect.mock.options.port %>'
    }
};
