/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

(function () {
    'use strict';

    angular
        .module('testapiApp')
        .factory('raiseAlert', raiseAlert);

    raiseAlert.$inject = ['$uibModal'];

    /**
     * This allows alert pop-ups to be raised. Just inject it as a dependency
     * in the calling controller.
     */
    function raiseAlert($uibModal) {
        return function(mode, title, text) {
            $uibModal.open({
                templateUrl: 'testapi-ui/shared/alerts/alertModal.html',
                controller: 'RaiseAlertModalController as alert',
                backdrop: true,
                keyboard: true,
                backdropClick: true,
                size: 'md',
                resolve: {
                    data: function () {
                        return {
                            mode: mode,
                            title: title,
                            text: text
                        };
                    }
                }
            });
        };
    }

    angular
        .module('testapiApp')
        .controller('RaiseAlertModalController', RaiseAlertModalController);

    RaiseAlertModalController.$inject = ['$uibModalInstance', 'data'];

    /**
     * This is the controller for the alert pop-up.
     */
    function RaiseAlertModalController($uibModalInstance, data) {
        var ctrl = this;

        ctrl.close = close;
        ctrl.data = data;

        /**
         * This method will close the alert modal. The modal will close
         * when the user clicks the close button or clicks outside of the
         * modal.
         */
        function close() {
            $uibModalInstance.close();
        }
    }
})();
