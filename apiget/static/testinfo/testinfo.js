function openmenu(menunow){
    menunow.attr("class", "open");
    menunow.children("ul").show();
    menunow.siblings().attr("class", "");
    menunow.siblings().children("ul").hide();
}

function unfinish(unfinished) {
    alert('功能尚未完成');
}

function base_getupdate(){
    $("#loading").fadeIn();
    $.get("/api/update/",function (ret) {
        alert("更新"+ret+"条数据");
    }).done(function() {
        $("#loading").fadeOut();
        location.reload();
    });
}
function baseinit() {

    $("#load").click(function () {
        base_getupdate();
    });

    $('.unfinished').click(function () {
        unfinish($(this));
    });

    $('.detailclose').click(function () {
        $("#detail").fadeOut();
    });
}

function chartsinit() {
    Main.init();
    openmenu($('#holeinfo'));
    var date = new Date();
    var thisyear = date.getFullYear();
    while(thisyear>=2013){
        $("#charts-year").append('<option value="'+thisyear+'">'+thisyear+'</option>');
        thisyear--;
    }
    getcharts(2, 1,'最近两年安全部漏洞统计');
    $("#chart1-last-2-year").click(function () {
        getcharts(2, 1, '最近两年安全部漏洞统计');
    });
    $("#chart1-last-3-year").click(function () {
        getcharts(3, 1,'最近三年安全部漏洞统计');
    });
    $("#chart1-all-year").click(function () {
        getcharts('all', 1, '2013年至今安全部漏洞统计');
    });

    $("#chart2-last-2-year").click(function () {
        getcharts(2, 2, '最近两年安全部漏洞统计');
    });
    $("#chart2-last-3-year").click(function () {
        getcharts(3, 2,'最近三年安全部漏洞统计');
    });
    $("#chart2-all-year").click(function () {
        getcharts('all', 2, '2013年至今安全部漏洞统计');
    });
}

function feedbackinit() {
    Main.init();
    getfb(1);
    openmenu($('#testinfo'));
    openmenu($('#moretool'));
    $.getJSON('/api/feedback',
        {
            mode: 0
        }
        ,function (ret) {
            $('#summary').append('目前共计收到反馈'+(ret.donec+ret.ndonec)+'，已经处理'+ret.donec+'，未处理'+ret.ndonec+'。其中云笔记'+ret.groupc.YNOTE+'条，广告'+ret.groupc.EAD+'条，购物'+ret.groupc.ARMANI+'条，词典产品'+ret.groupc.LUNA+'条')
        }
    );

    $("#grade").click(function () {
        getfb(1);
    });
    $("#fbqcount").click(function () {
        getfb(2);
    });
    $("#undolist").click(function () {
        getfb(3);
    });
    $("#fbulist").click(function () {
        getfb(4);
    });
    $("#filedown").click(function () {
        window.open('/download')
    });
    $("#fbupload").click(function () {
        window.open('/fbupload')
    });
}
function filedowninit() {
    Main.init();
    openmenu($('#testinfo'));
    openmenu($('#moretool'));
    $.getJSON('/api/filename',
        function(ret){
            for (var k in ret.filelist){
                $('#filename').append('<option value="'+ret.filelist[k]+'">'+ret.filelist[k]+'</option>');
            }
        })
}
function fbuploadinit() {
    Main.init();
    openmenu($('#testinfo'));
    openmenu($('#moretool'));
}


function update_getentry() {
    var group = $('#group').val();
    var quarter = $('#quarter').val();
    $.getJSON('/api/getlastentry',
        {
            'group': group,
            'quarter': quarter
        },function (ret) {
            for (var k in ret){
                $('#'+ k).val(ret[k]);
            }
        }
    );
}

function updateinit() {
    Main.init();
    openmenu($('#testinfo'));
    openmenu($('#moretool'));
    $.getJSON('/api/getquarters',
        {
            need: 'new'
        },
        function (ret) {
            for (var ind in ret.quarters){
                $("#quarter").append('<option value="'+ret.quarters[ind]+'">'+ret.quarters[ind]+'</option>');
            }
            getpbugs();
        });
    $('#go').click(function(){
        update_getentry();
    });
}
function table_opendetail(thisone) {
    var id = thisone.attr('id');
    $.get('/api/detailbyid',
        {
            id: id
        },
        function (ret) {
            $("#detail .modal-dialog .modal-content .modal-body").html(ret);
            $("#detail").fadeIn();
        }
    )
}

function table_select() {
    var group = $("#group").val();
    var productName = $("#productName").val();
    var targetType = $("#targetType").val();
    var bgdate = $("#bgdate").val();
    var eddate = $("#eddate").val();
    var level = $("#level").val();
    var status = $("#status").val();
    var quarter = $("#quarter").val();
    var year = $("#year").val();
    var st = $('form').serialize();
    if ($("#tablerow")){
        $("#tablerow").remove();
    }
    $(".main-container .main-content .container").append('<div class="row" id="tablerow"><div class="col-md-12"><div class="panel panel-default"></div></div></div>');
    $("#tablerow div div").append('<div class="panel-heading"><i class="fa clip-grid-6"></i>漏洞信息数据表<div class="panel-tools"><a class="btn btn-xs btn-link panel-close" href="#"> <i class="fa fa-times"></i> </a></div></div>').append('<div class="panel-body"><table class="table table-striped table-bordered table-hover table-full-width" id="sample_1"></table></div>');
    $("table").append('<thead><tr><th>id</th><th class="hidden-xs">产品名</th><th>漏洞状态</th><th class="hidden-xs">目标类型</th><th class="hidden-xs">漏洞等级</th><th>目标</th><th class="hidden-xs">创建时间</th><th class="hidden-xs">描述</th></tr></thead>');
    $("table").append('<tbody></tbody>');
    $.getJSON("/api/search",
        {
            "group": group,
            "productName": productName,
            "targetType":targetType,
            "bgdate":bgdate,
            "eddate":eddate,
            "level":level,
            "status":status,
            "quarter":quarter,
            "year":year
        }
        , function (ret) {
            $.each(ret, function (idx, item) {
                $("table tbody").append('<tr><td>' + item.id + "</td><td>" + item.productName + "</td><td>" + item.status +
                    "</td><td>" + item.targetType + "</td><td>" + item.level +
                    "</td><td>" + item.targets + "</td><td>" + item.createTime + '</td><td><button class="opendetail btn btn-info btn-block" id='+item.id+'>详情</button></td></tr>');
            });
            $('.opendetail').click(function(){
                table_opendetail($(this));
            });
            TableData.init();
        });
}

function table_time_quarter(date) {
    $("#bgdate").val("");
    $("#eddate").val("");
}

function table_time_date(date) {
    $("#year").val("");
    $("#quarter").val("");
    if (date.getDate() < 10){
        $("#eddate").val(date.getFullYear()+"-"+(date.getMonth()+1)+"-0"+(date.getDate()));
    }
    else {
        $("#eddate").val(date.getFullYear()+"-"+(date.getMonth()+1)+"-"+(date.getDate()));
    }
}

function tableinit() {
    Main.init();

    openmenu($('#holeinfo'));
    var date = new Date();
    var thisyear = date.getFullYear();
    while(thisyear>=2013){
        $("#year").append('<option value="'+thisyear+'">'+thisyear+'</option>');
        thisyear--;
    }
    $("#time_quarter").click(function (){
        table_time_quarter(date);
    });

    $("#time_date").click(function (){
        table_time_date(date);
    });
    getgitem();
    $("#group").change(function(){
        getgitem();
    });
    $("#select").click(function () {
        table_select();
    });
}


function getgitem() {
    var gn = $('#group').val();
    $("#productName").children().next().remove();
    $.getJSON("/api/productnamelist",
        {
            'group':gn
        }
        , function (ret) {
            $.each(ret.name, function (idx, item) {
                $("#productName").append('<option value="'+item+'">'+item+'</option>');
            });
        });
}

function getfb(Mode){
    $('#tb').children().remove();
    $('#namelist').children().remove();
    var myChart = echarts.init(document.getElementById('main'));
    var option = {
        title: {
            text: "BUG总数",
            x: 'center',
            align: 'right'
        },
        color: [
            "#4cb0f9",
            "#003472",
            "#9ed048",
            "#ffa631"
        ],
        tooltip : {
            trigger: 'axis',
            axisPointer : {            // 坐标轴指示器，坐标轴触发有效
                type : 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
            }
        },
        toolbox: {
            feature: {
                saveAsImage: {}
            },
            top: '10%',
            right: '5%'
        },
        legend: {
            data:[],
            x: 'left',
            left:20,
            top:'10%'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: '20%',
            containLabel: true
        },
        xAxis : [
            {
                type : 'category',
                data : []
            }
        ],
        yAxis : [],
        series : []
    };

    if (Mode == 1){
        option.yAxis[0] = {type : 'value',min : 10,max : 8.5};
    }
    else {
        option.yAxis[0] = {type : 'value'};
    }
    var ldlist = [];
    var series = [];
    $.getJSON("/api/feedback",
        {
            "mode": Mode
        }
        , function (ret) {

            if (Mode <=2){

                option.xAxis[0].data = ret.xAxis;
                option.title.text = ret.title;

                sortk = [];
                for (var k in ret.data){
                    sortk.push(k);
                }
                sortk.sort();
                for (var i = 0;i<sortk.length; i++){
                    ldlist.push(sortk[i]);
                    if (ret.type == 'line'){
                        series.push({name: sortk[i], type: ret.type, data: ret.data[sortk[i]],
                            smooth:true, areaStyle: { normal: { }}});
                    }
                    else{
                        series.push({name: sortk[i], type: ret.type, data: ret.data[sortk[i]],
                            smooth:true, label: { normal: {show: true, position: 'top', textStyle: {fontSize: 16}}} });
                    }
                }
                option.legend.data = ldlist;
                option.series = series;
                myChart.setOption(option);
            }
            else if(Mode == 3){
                if (ret.list.length == 0){
                    $('#tb').append('<tr><td>所有问题都已解决</td></tr>');
                }
                else {
                    for (var li in ret.list){
                        $('tbody').append('<tr><td>'+li.name+'</td><td>'+li.content+'</td></tr>')
                    }
                }
            }
            else if(Mode == 4){
                var lis = [];
                for (var k in ret){
                    var l = [];
                    l.push(k);
                    l.push(ret[k]);
                    lis.push(l);

                }
                lis.sort(function (x,y) {
                    if (x[1]>y[1]){
                        return -1;
                    }
                    if (x[1]<y[1]){
                        return 1;
                    }
                    else {
                        return 0;
                    }
                });
                for (var k in lis){
                    $('#namelist').append('<span>'+lis[k][0]+":"+lis[k][1]+' | </span>')
                }
            }
        });
}

function getcharts(years, smode, title){
    var myChart = echarts.init(document.getElementById('main'));
    var option = {
        title : {
            text : '',
            x: 'center',
            align: 'right'
        },
        tooltip : {
            trigger: 'axis',
            axisPointer : {            // 坐标轴指示器，坐标轴触发有效
                type : 'line'        // 默认为直线，可选为：'line' | 'shadow'
            },
            enterable: true
        },
        toolbox: {
            feature: {
                saveAsImage: {},
                dataView: {}
            },
            top: '10%',
            right: '5%'
        },
        legend: {
            data:[],
            x: 'left',
            left:20,
            top:'10%'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: '20%',
            containLabel: true
        },
        xAxis : [
            {
                type : 'category',
                data : []
            }
        ],
        yAxis : [
            {
                type : 'value'
            }
        ],
        series : []
    };
    var formelement = {
        "years": years,
        "smode": smode
    };
    if (smode == '2'){
        var group =  $('#group').val();
        formelement['groupname'] = group;
    }
    $.getJSON("/api/statistics",
        formelement
        , function (ret) {
            var ldate = [];
            var smaplist = [];
            var allvalue = [];
            for( var i = 0; i < ret.xAxis.length; i++){
                allvalue.push(0);
            }
            $.each(ret.data, function (idx, item) {
                ldate.push(item.name);
                smaplist.push({name: item.name, type: 'line', smooth: true, data: item.value, label: { normal: {show: false, position: 'top', textStyle: {fontSize: 16}}}});
                for (var v in item.value){
                    allvalue[v] += item.value[v];
                }
            });
            ldate.push('全部');
            smaplist.push({name: '全部', type: 'line', smooth: true, data: allvalue, label: { normal: {show: false, position: 'top', textStyle: {fontSize: 16}}}});
            option.xAxis[0].data = ret.xAxis;
            option.legend.data = ldate;
            option.series = smaplist;
            if (smode == '1'){
                option.title.text = title;
            }
            else if(smode == '2'){
                option.title.text = group+title;
            }
            myChart.setOption(option);
        });
}