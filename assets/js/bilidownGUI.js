var _backend_object = null;
var _channel= null;

$(function () {
    _channel = new QWebChannel(qt.webChannelTransport, function (channel) {
        _backend_object = channel.objects.BilidownGUI;
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