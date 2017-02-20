'use strict';

/**
 * get data factory
 */
angular.module('opnfvApp')
    .factory('TableFactory', function($resource, $rootScope) {

        return {
            getFilter: function() {
                return $resource(BASE_URL + '/filters', {}, {
                    'get': {
                        method: 'GET',

                    }
                });
            },
            getScenario: function() {
                return $resource(BASE_URL + '/scenarios', {}, {
                    'post': {
                        method: 'POST',
                    }
                })
            }
        };
    });