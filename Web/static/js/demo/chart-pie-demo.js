import * as echarts from 'echarts';
var chartDom = document.getElementById('cityjob');
var myChart = echarts.init(chartDom);
var option;
window.onresize = function() {
    myChart.resize();
  };
option = {
  title: {
    text: '城市岗位需求'
  },
  tooltip: {
    trigger: 'item'
  },
  legend: {
    top: '5%',
    left: 'center'
  },
  series: [
    {
      name: 'Access From',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '40',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: {{data|tojson}}
    }
  ]
};

option && myChart.setOption(option);
