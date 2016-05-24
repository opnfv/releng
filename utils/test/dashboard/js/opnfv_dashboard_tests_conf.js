var opnfv_dashboard_project = 'functest';
var opnfv_dashboard_installer = '';
var opnfv_dashboard_test = '';
var opnfv_dashboard_test_unit = '';
var opnfv_dashboard_pod = 'all';

var opnfv_dashboard_installers = ['apex', 'compass', 'fuel', 'joid'];

var opnfv_dashboard_installers_scenarios = {};
opnfv_dashboard_installers_scenarios['apex'] =
    ['os-nosdn-nofeature-ha',
    'os-odl_l2-nofeature-ha',
    'os-onos-nofeature-ha',
    'os-odl_l3-nofeature-ha',
    'os-odl_l2-sfc-ha'];

opnfv_dashboard_installers_scenarios['compass']=
    ['os-nosdn-nofeature-ha',
    'os-odl_l2-nofeature-ha',
    'os-onos-nofeature-ha',
    'os-ocl-nofeature-ha'];

opnfv_dashboard_installers_scenarios['fuel']=
    ['os-nosdn-nofeature-ha','os-odl_l2-nofeature-ha','os-onos-nofeature-ha','os-odl_l3-nofeature-ha','os-odl_l2-bgpvpn-ha','os-nosdn-ovs-ha','os-nosdn-kvm-ha','os-nosdn-ovs_kvm-ha'];

opnfv_dashboard_installers_scenarios['joid']=
    ['os-nosdn-nofeature-ha',
    'os-odl_l2-nofeature-ha',
    'os-onos-nofeature-ha',
    'os-ocl-nofeature-ha'];

var opnfv_dashboard_testcases = {
    'VIM': {
        'Tempest': ['Tempest duration',
                'Tempest nb tests/nb failures'],
        'vPing': ['vPing duration'],
        'vPing_userdata': ['vPing_userdata duration'],
        'Rally': ['rally duration']
    },
    'Controller': {
        'ODL': ['ODL nb tests/nb failures'],
        'ONOS': ['ONOS FUNCvirNet duration ',
                'ONOS FUNCvirNet nb tests/nb failures',
                'ONOS FUNCvirNetL3 duration',
                'ONOS FUNCvirNetL3 nb tests/nb failures']
    },
    'Features': {
        'vIMS': ['vIMS nb tests passed/failed/skipped',
                'vIMS orchestrator/VNF/test duration'],
        'promise': ['Promise duration ',
                'Promise nb tests/nb failures'],
		'doctor': ['doctor-notification duration ']
    }
};

var opnfv_dashboard_installers_pods = {};
opnfv_dashboard_installers_pods['apex'] = ['all','intel-pod7','opnfv-jump-1'];
opnfv_dashboard_installers_pods['compass'] = ['all','huawei-us-deploy-bare-1','huawei-us-deploy-vm-1','huawei-us-deploy-vm2','intel-pod8'];
opnfv_dashboard_installers_pods['fuel'] = ['all','ericsson-pod2','opnfv-jump-2','arm-pod1','zte-pod1'];
opnfv_dashboard_installers_pods['joid'] = ['all','intel-pod5','intel-pod6','orange-fr-pod2'];

var opnfv_dashboard_installers_pods_print = {};
opnfv_dashboard_installers_pods_print['apex'] = ['all','intelpod7','opnfvjump1'];
opnfv_dashboard_installers_pods_print['compass'] = ['all','hwusbare1','hwusvm1','hwusvm2','intelpod8'];
opnfv_dashboard_installers_pods_print['fuel'] = ['all','ericssonpod2','opnfvjump2','armpod1','ztepod1'];
opnfv_dashboard_installers_pods_print['joid'] = ['all','intelpod5','intelpod6','orangefrpod2'];

var opnfv_dashboard_file_directory = 'res-test';
var opnfv_dashboard_file_prefix = 'res_';
var opnfv_dashboard_file_suffix = '.json';

var opnfv_dashboard_ys = ['y', 'y1', 'y2', 'y3', 'y4', 'y5'];
var opnfv_dashboard_y_labels = ['ylabel',
        'y1label',
        'y2label',
        'y3label',
        'y4label',
        'y5label'];

var opnfv_dashboard_graph_color_ok = "#00ADBB";
var opnfv_dashboard_graph_color_nok = "#3c7b70";
var opnfv_dashboard_graph_color_other = "#313330";

var opnfv_dashboard_graph_legend = 'always'; // legend print
var opnfv_dashboard_graph_title_height = 30; // height for the graph title
var opnfv_dashboard_graph_stroke_width = 5; // line stroke when mouse over
var opnfv_dashboard_graph_axis_label_color = '#2E2925';
var opnfv_dashboard_graph_text_align = 'right';
var opnfv_dashboard_graph_background_color = 'transparent';
