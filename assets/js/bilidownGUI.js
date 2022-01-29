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
    _backend_object.onDownloadClick($('#input-param').val(), $('#input-directory').val())
})

$('#btnSuspend').click(function () {

})

$('#btnResume').click(function () {

})