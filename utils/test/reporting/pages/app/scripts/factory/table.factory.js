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
            },
            getProjectUrl: function() {
                return $resource(PROJECT_URL + '/projects-page/projects', {}, {
                    'get': {
                        method: 'GET'
                    }
                })
            },
            getProjectTestCases: function() {
                return $resource(PROJECT_URL + '/projects/:project/cases', { project: '@project' }, {
                    'get': {
                        method: 'GET'
                    }
                })
            },
            getProjectTestCaseDetail: function() {
                return $resource(PROJECT_URL + '/projects/:project/cases/:testcase', { project: '@project', testcase: '@testcase' }, {
                    'get': {

                        method: 'GET'
                    }
                })
            }
        };
    });