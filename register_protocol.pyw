import ctypes
import os
import sys
import tkinter
import tkinter.messagebox
import winreg

# bilidown:// URL Protocol Register Program


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_variables():
    py_exec_path = sys.executable
    script_path = "%s\\bilidownGUI.pyw" % (os.getcwd())
    return (py_exec_path, script_path)


def show_variables():
    vars = get_variables()
    exec_path = "PY_EXEC_PATH = %s" % (vars[0])
    sc_path = "SCRIPT_PATH = %s" % (vars[1])
    print(exec_path)
    print(sc_path)


def release_register_handler(h):
    if h != None:
        winreg.CloseKey(h)


def is_registered():
    ret = False
    bilidown_key = None
    try:
        bilidown_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, 'bilidown')
        ret = True
    except:
        ret = False
    finally:
        release_register_handler(bilidown_key)
    return ret


def register_protocol():
    ret = False
    vars = get_variables()
    bilidown_key = None
    default_icon_key = None
    command_key = None
    try:
        # get registry key
        bilidown_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 'bilidown')
        default_icon_key = winreg.CreateKey(bilidown_key, 'DefaultIcon')
        command_key = winreg.CreateKey(bilidown_key, 'shell\\open\\command')
        # put key-value pair
        winreg.SetValue(bilidown_key, "", winreg.REG_SZ, "BilidownProtocol")
        winreg.SetValueEx(bilidown_key, "URL Protocol", 0, winreg.REG_SZ, "")
        winreg.SetValue(default_icon_key, "", winreg.REG_SZ, vars[0])
        command_value = '%s "%s" "%%1"' % (vars[0], vars[1])
        winreg.SetValue(command_key, "", winreg.REG_SZ, command_value)
        ret = True
    except:
        ret = False
    finally:
        release_register_handler(default_icon_key)
        release_register_handler(command_key)
        release_register_handler(bilidown_key)
    return ret


def recursive_delete_key(key):
    try:
        while True:
            keyname = winreg.EnumKey(key, 0)
            subkey = winreg.OpenKey(key, keyname, 0, winreg.KEY_ALL_ACCESS)
            result = recursive_delete_key(subkey)
            release_register_handler(subkey)
            if(result == False):
                return False
    except:
        pass
    try:
        winreg.DeleteKey(key, "")
        return True
    except:
        return False


def unregister_protocol():
    bilidown_key = None
    result = False
    try:
        bilidown_key = winreg.OpenKey(
            winreg.HKEY_CLASSES_ROOT, 'bilidown', 0, winreg.KEY_ALL_ACCESS)
        result = recursive_delete_key(bilidown_key)
    except:
        pass
    finally:
        release_register_handler(bilidown_key)
    return result


def register_and_notify(root):
    if register_protocol():
        tkinter.messagebox.showinfo(
            'bilidown协议注册', 'bilidown协议注册成功！', parent=root)
    else:
        tkinter.messagebox.showerror(
            'bilidown协议注册', 'bilidown协议注册失败！', parent=root)


def register_proc(root):
    choice = tkinter.messagebox.askyesno(
        'bilidown协议注册', '是否注册bilidown协议?', parent=root)
    if(choice):
        register_and_notify(root)


def unregister_proc(root):
    choice = tkinter.messagebox.askyesnocancel(
        'bilidown协议注册', 'bilidown协议已注册,即将执行bilidown协议卸载操作。\r\n是否重新安装bilidown协议?', parent=root)
    if(choice != None):
        if(unregister_protocol()):
            tkinter.messagebox.showinfo(
                'bilidown协议注册', 'bilidown协议卸载成功！', parent=root)
        else:
            tkinter.messagebox.showerror(
                'bilidown协议注册', 'bilidown协议卸载失败！', parent=root)
    if(choice):
        register_and_notify(root)


def main():
    root = tkinter.Tk()
    root.withdraw()
    show_variables()
    if is_registered():
        unregister_proc(root)
    else:
        register_proc(root)


if __name__ == '__main__':
    if is_admin():
        main()
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1)
