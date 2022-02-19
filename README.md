# bilidown_py

b站源视频下载轻量级python版，这将是第一个README比程序更有用、展示思想而非代码的项目。(orz)

你还在苦恼b站视频素材下不了吗？你还在抱怨bilibilijj不好使吗？

项目包括bilidown480.py(无Cookie低画质)、bilidown.py(需要提取资源链接)、bilidownGUI.pyw(B雷图形化多线程下载器)。

## 本项目优势

- 由于耦合度小，bilibili的URL格式或者参数格式发生变化，您仍然可以正常使用并且不用做代码改动。
- 本项目只引入了requests，直接pip装上依赖就能使了，集成的太多装依赖也费时间。
- 控制台、GUI，各种类型应有尽有。
- 坠重要的~~~需要登录或者大会员的资源也能下(只要你当前的bilibili账号有权限访问，毕竟它灵活嘛)。

## bilidownGUI
- 运行register_protocol，注册bilidown://协议。
- 打开chrome浏览器，打开bilibili视频页，使用bilibili默认的H5播放器，选择好要下载的画质
- 使用[bilidown_lite](https://github.com/MNTMDEV/bilidown_lite)提取资源URL。
- 点击使用bilidownGUI下载，转到GUI客户端操作。

## bilidown

- 需要有chrome浏览器、python运行环境、[ffmpeg](http://ffmpeg.org/download.html)，要安装requests(一行pip install requests的事)
- 打开chrome浏览器，打开bilibili视频页，使用bilibili默认的H5播放器，选择好要下载的画质
- 使用[bilidown_lite](https://github.com/MNTMDEV/bilidown_lite)提取资源URL。
- 运行bilidown。
- 分别复制[bilidown_lite](https://github.com/MNTMDEV/bilidown_lite)提取的视频&网页地址和音频&网页地址，运行2次后获得视频和音频。
- 两次它都会生成xxx.m4s的文件，都改成.mp4格式的，然后视频音频自然你就能区分出来了，然后上ffmpeg，把视频音频全打到一个文件里

## bilidown480

为什么说是bilidown480呢，这个可是确实已经达到了完全自动化的目标，但是你是知道的，游客所能看到的bili视频最高画质就是480，你没有登录的Cookies，bilibili自然不会叫你看高画质的视频，当然更别提下载它的源文件了。就不多说了，好处自然是输入https://www.bilibili.com/video/av(bv)xxxxxxxx 就能全自动下载，缺点你懂的，高画质别想了，如果还要让程序输入Cookies，那还不如直接使用上面那个最简版的用抓包来做呢。当然，不要忽略一点，这个家伙还是支持下载同一个av/bv号不同页的视频哦。

## 注意事项

控制台输出如果有Warning警告尝试次数超限，很有可能已经触发了风控或网络状态极差，出现此类Warning下载的文件是不完整的，建议重新下载或者更换网络环境重新下载。

## TODO

null