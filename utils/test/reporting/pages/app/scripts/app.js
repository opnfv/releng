'use strict';

/**
 * @ngdoc overview
 * @name opnfvApp
 * @description
 * # opnfvApp
 *
 * Main module of the application.
 */
angular
    .module('opnfvApp', [
        'ngAnimate',
        'ui.router',
        'oc.lazyLoad',
        'ui.bootstrap',
        'ngResource',
        'selectize',
        '720kb.tooltips',
        'ngDialog',
        'angularUtils.directives.dirPagination',
        'darthwade.dwLoading'

    ]);