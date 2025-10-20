import shutil, time, ctypes, threading
from pathlib import Path

IMG="rat.jpg"
PD=Path(r"C:\Users\Public\Downloads")
ZW="\u200B"
STOP=threading.Event()
MOD_ALT=0x0001;MOD_CTRL=0x0002;WM_HOTKEY=0x0312;HK=1

def r_desktop(): 
    d=Path.home()/ "Desktop"
    return d if d.exists() else Path(r"C:\Users\Public\Desktop") if Path(r"C:\Users\Public\Desktop").exists() else Path.home()

def ensure_src():
    f=PD/IMG
    if not f.exists(): PD.mkdir(parents=True,exist_ok=True); f.write_bytes(b"\x89PNG\r\n\x1a\nRAT_PLACEHOLDER")
    return f

def copy_rat(c):
    s=ensure_src()
    n=ZW*c+IMG
    try: shutil.copy2(s,r_desktop()/n); return n
    except: return ""

def list_files(): return {f.name for f in r_desktop().iterdir() if f.is_file()}

def rm_zw(): 
    for f in r_desktop().iterdir(): 
        if f.is_file() and f.name.startswith(ZW) and f.name.endswith(IMG): 
            f.unlink()
    ctypes.windll.shell32.SHChangeNotify(0x8000000,0x1000,None,None)

def worker():
    t=[];c=1
    n=copy_rat(c)
    if n: t.append(n);c+=1
    while not STOP.is_set():
        d=[f for f in t if f not in list_files()]
        if d:
            time.sleep(0.2);d=[f for f in d if f not in list_files()];new=[]
            for _ in d:
                for _ in range(2):
                    if STOP.is_set(): break
                    n=copy_rat(c)
                    if n:new.append(n);c+=1
                if STOP.is_set(): break
            t=[f for f in t if f not in d]+new
            if new: ctypes.windll.shell32.SHChangeNotify(0x8000000,0x1000,None,None)
        time.sleep(0.5)

def hotkey():
    u=ctypes.windll.user32
    if not u.RegisterHotKey(None,HK,MOD_CTRL|MOD_ALT,ord('X')): return
    msg=ctypes.wintypes.MSG()
    while not STOP.is_set():
        got=u.GetMessageW(ctypes.byref(msg),None,0,0)
        if got==0: break
        if msg.message==WM_HOTKEY and msg.wParam==HK:
            STOP.set(); rm_zw(); break
        u.TranslateMessage(ctypes.byref(msg)); u.DispatchMessageW(ctypes.byref(msg))
    u.UnregisterHotKey(None,HK)

t=threading.Thread(target=worker,daemon=True)
t.start()
try: hotkey()
except KeyboardInterrupt: STOP.set(); rm_zw()
t.join(5)
