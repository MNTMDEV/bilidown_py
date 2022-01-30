var _backend_object = null;
var _channel = null;

var convertBase64Url = function (jsonData) {
    JSON.stringify(jsonData);
}

var initEvent = function () {
    //initial parameter
    _backend_object.onGetParam(function (param) {
        $('#input-param').val(param);
    });
    // initial directory
    _backend_object.onGetRootDirectory(function (directory) {
        $('#input-directory').val(directory);
    });
    _backend_object.sigUI.connect(function(jsonData){
        processUIEvent(jsonData);
    })
}



var processUIEvent = function(jsonData){
    var type = jsonData.type;
    var data = jsonData.data;
    switch(type){
        case 'progress':
            $('#progress').css('width',data+"%");
            $('#progress').text(data+"%");
            break;
        case 'info':
            $('#info').attr('class', data.style);
            $('#info').text(data.info);
            if((data.type==1)||(data.type==3)){
                $('#btnDownload').attr('disabled',false);
            }
            break;
    }
}

$(function () {
    _channel = new QWebChannel(qt.webChannelTransport, function (channel) {
        _backend_object = channel.objects.BilidownGUI;
        initEvent();
    });
})

$('#btnQuit').click(function () {
    _backend_object.onQuitClick();
});

$('#iconQuit').click(function () {
    _backend_object.onQuitClick();
});

$('#iconMin').click(function () {
    _backend_object.onMinimizeClick();
});

$('.browse-file').click(function () {
    _backend_object.onBrowseDirectoryClick(function (directory) {
        if (directory != "") {
            $('#input-directory').val(directory);
        }
    });
})

$('#btnDownload').click(function () {
    $('#btnDownload').attr('disabled',true);
    _backend_object.onDownloadClick($('#input-param').val(), $('#input-directory').val())
})

$('#btnSuspend').click(function () {

})

$('#btnResume').click(function () {

})