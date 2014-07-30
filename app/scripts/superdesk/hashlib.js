define(['bower_components/jsSHA/src/sha512'], function(SHA) {
    'use strict';

    var HASH_TYPE = 'ASCII',
        HASH_ALGO = 'SHA-512',
        HASH_OUT = 'HEX';

    /**
     * Get hmac for given input using given secret key
     *
     * @param {string} input
     * @param {string} key
     * @returns {string}
     */
    function hmac(input, key) {
        return sha(input).getHMAC(key, HASH_TYPE, HASH_ALGO, HASH_OUT);
    }

    /**
     * Get sha object for given string input
     *
     * @param {string} input
     * @returns {object}
     */
    function sha(input) {
        return new SHA(input, HASH_TYPE);
    }

    /**
     * Get hash of given input
     *
     * @param {string} input
     * @returns {string}
     */
    function hash(input) {
        return sha(input).getHash(HASH_ALGO, HASH_OUT);
    }

    return {
        hmac: hmac,
        hash: hash
    };
});
