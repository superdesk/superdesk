var tests = Object.keys(window.__karma__.files).filter(function (file) {
      return /Spec\.js$/.test(file);
});

requirejs.config({
    baseUrl: '/app/',
    deps: tests,
    callback: window.__karma__.start
});
