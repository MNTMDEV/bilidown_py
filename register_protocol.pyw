import ctypes
import os
import sys
import tkinter
import tkinter.messagebox
import winreg


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_variables():
    py_exec_path = sys.executable
    script_path = "%s\\bypassGUI.pyw" % (os.getcwd())
    return (py_exec_path, script_path)


def show_variables():
    vars = get_variables()
    exec_path = "PY_EXEC_PATH = %s" % (vars[0])
    sc_path = "SCRIPT_PATH = %s" % (vars[1])
    print(exec_path)
    print(sc_path)


def register_protocol():
    vars = get_variables()
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
    # close handler
    winreg.CloseKey(default_icon_key)
    winreg.CloseKey(command_key)
    winreg.CloseKey(bilidown_key)


def main():
    root = tkinter.Tk()
    root.withdraw()
    show_variables()
    choice = tkinter.messagebox.askokcancel(
        'bilidown协议注册', '是否注册bilidown协议?', parent=root)
    if(choice):
        try:
            register_protocol()
            tkinter.messagebox.showinfo(
                'bilidown协议注册', 'bilidown协议注册成功！', parent=root)
        except:
            tkinter.messagebox.showerror(
                'bilidown协议注册', 'bilidown协议注册失败！', parent=root)


if __name__ == '__main__':
    if is_admin():
        main()
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1)
