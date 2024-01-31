(function() {
    "use strict";

    microCloud.controller('CPElasticController', ['$scope', 'ControlPanelService', 'MicroCloudFactory',
        function($scope, ControlPanelService, MicroCloudFactory){

            $scope.controlPanel.hideNav = false;

            $scope.elastic = {};
            $scope.elastic.idList = [];
            $scope.elastic.selectedIdList = [];

            $scope.init = function () {
                $scope.elastic.elasticList = ControlPanelService.elasticList;

                for (let index = 0; index < 50; index ++) {
                    let a = angular.copy(ControlPanelService.elasticList[2]);
                    a._id = a._id + index;
                    $scope.elastic.elasticList.push(a);
                }

                $scope.elastic.businessGroup = ControlPanelService.businessGroupList[0];
                $scope.elastic.businessGroupList = ControlPanelService.businessGroupList;
                $scope.elastic.routeList = ControlPanelService.routeList;
                $scope.elastic.sliderConfig = ControlPanelService.elasticIpSliderConfig;

                $scope.elastic.pagination = {
                    paginalNumberList: ControlPanelService.paginalNumberList,
                    paginalNumber: ControlPanelService.paginalNumberList[0],
                    totalItem: ControlPanelService.pagination.totalItem,
                    currentPage: ControlPanelService.pagination.currentPage
                };

                $scope.getIdList();
                MicroCloudFactory.initPopover();
            };

            $scope.updateBusinessGroup = function (newBusinessGroup) {
                $scope.elastic.businessGroup = newBusinessGroup;
            };

            $scope.showAllIp = function (ipList) {
                let ipListForHtml = '';
                if (ipList[0]) {
                    angular.forEach(ipList, function (ip, index){
                        if (index < 10) {
                            ipListForHtml += index !== ipList.length - 1 ? ip + "<br>" : ip;
                        }else {
                            ipListForHtml += '...';
                            return false;
                        }
                    });
                }
                return ipListForHtml;
            };

            $scope.getIdList = function () {
                angular.forEach($scope.elastic.elasticList, function (elastic) {
                    if (elastic._id && $.inArray(elastic._id, $scope.elastic.idList) === -1) {
                        $scope.elastic.idList.push(elastic._id)
                    }
                })
            };

            $scope.init();

            $scope.updateIdSelectStatus = function (id) {
                if (id && MicroCloudFactory.getType(id) === 'String') {
                    $.inArray(id, $scope.elastic.selectedIdList) === -1 ? $scope.elastic.selectedIdList.push(id) :
                        $scope.elastic.selectedIdList.splice($.inArray(id, $scope.elastic.selectedIdList), 1);
                }
            };

            $scope.checked = function (id) {
                if (id && MicroCloudFactory.getType(id) === 'String') {
                    return $.inArray(id, $scope.elastic.selectedIdList) >= 0;
                }
            };

            $scope.selectAllOrDeselectAll = function () {
                $scope.selectAllCheckedOrNot() ? $scope.elastic.selectedIdList = [] :
                    $scope.elastic.selectedIdList = angular.copy($scope.elastic.idList);
            };

            $scope.selectAllCheckedOrNot = function () {
                let Checked = false;
                if ($scope.elastic.idList[0] && $scope.elastic.selectedIdList[0]) {
                    Checked = true;
                    angular.forEach($scope.elastic.idList, function (id) {
                        if ($.inArray(id, $scope.elastic.selectedIdList) === -1) {
                            Checked = false;
                            return false;
                        }
                    })
                }
                return Checked;
            };

            $scope.fixToolbar = function () {
                if ($('#page-content').scrollTop() >= 135) {
                    $('#elastic-tool-bar').addClass('fix-tool-bar');
                }else {
                    $('#elastic-tool-bar').removeClass('fix-tool-bar');
                }
            };

            $scope.initModal = function () {
                $scope.elastic.newIp = {
                    route: {
                        id: $scope.elastic.routeList[0]._id,
                        name: $scope.elastic.routeList[0].name,
                        description: $scope.elastic.routeList[0].description
                    },
                    bandwidth: 1,
                    ipNumber: 1
                };
            };

            $scope.updateRoute = function (route) {
                $scope.elastic.newIp = {
                    route: {
                        id: route._id,
                        name: route.name,
                        description: route.description
                    }
                };
            };

            $scope.reduceIpNumber = function () {
                if ($scope.elastic.newIp.ipNumber > 1) {
                    $scope.elastic.newIp.ipNumber -= 1;
                }
            };

            $scope.increaseIpNumber = function () {
                if ($scope.elastic.newIp.ipNumber < 200) {
                    $scope.elastic.newIp.ipNumber += 1;
                }
            };

        }]);
})();