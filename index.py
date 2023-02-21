import os
import subprocess
import sys
import shutil
import json
import dialog
import pickle
import base64
from colorama import Fore, Back, Style
d = dialog.Dialog("dialog")

class Kernel():
    def log(self, msg):
        print("[LOG] "+msg)
    def _mem_check(self):
        pass

    def panic(self, msg):
        print("=== PANIC PANIC PANIC ===")
        print("KERNEL_PANIC: "+msg)
    def _disk_space_check(self):
        disk = shutil.disk_usage(".")
        free = round(disk.free / (1024*1024))
        if free < self._r_storage:
            return False
        else:
            return True

    def read_settings(self):
        try:
            with open("kernel_libs/settings.json") as f:
                settings = json.load(f)

            if settings["req_storage"] < 1024:
                self.panic("Invalid value of \"req_storage\" while reading user-settings: Minimum of the value is 1024!")

            if settings["alloc_mem"] < 512:
                self.panic("Invalid value of \"alloc_mem\" while reading user-settings: Minimum of the value is 512!")

            self._memallocsz = settings["alloc_mem"]
            self._fofspp = settings["enable_fofspp"]
            try:
                self._r_storage = int(settings["req_storage"])
            except Exception:
                self.panic("Invalid value of \"req_storage\" while reading user-settings: Unknown error")
            self._g_settings = settings
            
        except FileNotFoundError:
            self.panic("Cannot read user-settings file!: file not found")
    def save_settings(self,n_settings):
        try:
            with open("kernel_libs/settings.json", "w") as f:
                json.dump(n_settings, f)
        except FileNotFoundError:
            self.panic("Cannot save new settings!: file not found!")
    def k_settings(self):
        menu = d.menu("Chooss to set", 30, 45, 28, (("User", "User options"), ("System", "System options"), ("Perfomance", "Adjust Perfomance")))
        if menu[0] == "ok":
            mdn = menu[1]
            if mdn == "User":
                self.k_user_settings()
    def k_user_settings(self):
        while True:
            enable_fofspp = True
            check_updts = False
            clist = d.checklist("Check the options!", 35, 50, 30, [("FOFSPP", "Enable FOFSPP", "on"), ("Check Updts", "Check updates everyuser logged in", "off")])
            if clist[0] == "ok":
                if len(clist[1]) == 2:
                    for i in clist[1]:
                        if i == "FOFSPP": enable_fofspp = True
                        elif  i == "Check Updts": check_updts = True

                elif len(clist[1]) == 1:
                    if i == "FOFSPP": enable_fofspp = True
                    elif  i == "Check Updts": check_updts = True

                if len(clist[1]) == 0:
                    enable_fofspp = False
                    check_updts = False
                bsettings = {"req_storage": self._r_storage, "alloc_mem": self._memallocsz, "enable_fofspp": enable_fofspp, "check_updates": check_updts}
                self.save_settings(bsettings)
                d.msgbox("Settings has been updated !", 20, 35)
                break
    def k_perfom_settings(self):
        while True:
            k = d.mixedform("Please fill", [("Req. Storage", 1, 1, str(self._r_storage), 1, 20, 14, 5, 0x0), ("Alloc. Mem", 2, 1, str(self._memallocsz), 2, 20, 14, 5, 0x0)], width=45)
            if k[0] == "ok":
                rst = int(k[1][0])
                memalloc = int(k[1][1])
                if rst < 1024:
                    d.msgbox("Invalid value of \"req_storage\" while reading user-settings: Minimum of the value is 1024!", 20, 15)
                    continue
                if memalloc < 512:
                    d.msgbox("Invalid value of \"alloc_mem\" while r    eading user-settings: Minimum of the value is 512!")
                    continue

                if memalloc > 1024 and rst > 3052:
                    if d.yesno("Are you sure to continue?, Setting     mem_alloc and req storage over their maximum recommended values (may causing a problem to your real system)", 20, 26):
                        pass
                    else:
                        continue
                if rst > 3052 :
                    if d.yesno("Are you sure to continue?, Setting req_storage over 2048 MiB are not recommended (may causing a problem to your real system)", 20, 26):
                        pass
                    else:
                        continue
                elif memalloc > 1024:
                    if d.yesno("Are you sure to continue?, Settiing mem_alloc over 1024 MiB are not recommended (may causing a problem to your real system)", 20, 26):
                        pass
                    else:
                        continue
                elif memalloc > 1024 and rst > 3052:
                    if d.yesno("Are you sure to continue?, Setting mem_alloc and req storage over their maximum recommended values (may causing a problem to your real system", 20, 26):
                        pass
                    else:
                        continue
                bjson = {}

                bjson["req_storage"] = rst
                bjson["alloc_mem"] = memalloc
                self.save_settings(bjson)
                d.msgbox("Settings updated!")
                break
            else:
                return False
        
    def __init__(self):
        self.log("Initiating kernel...")
        try:
            self.read_settings()
            if self._disk_space_check():
                pass
            else:
                self.panic("Free storage is lower than required")
        except Exception as e:
            print("Failed initiating OS, exiting..\nError:"+str(e))
            exit(2)

        self.log("Successfully Initiate Kernel!")

class App:
    DEFAULT_APPDATA_PATH = "apps/*apps/apps.info"
    def __init__(self, os_instance, kernel_instance):
        print("App (Loader) v 1.0 by HecmaTrynzz")
        self.app_path = "apps/"
        self.min_app_apiv = 1
        self.osin = os_instance
        self.kerin = kernel_instance
        self.apps = {}
        self.apps_total = 0
        self._appdata_reader()
    def _appdata_reader(self):
        try:
            r_apps = os.listdir(self.app_path)
            if len(r_apps) == 0:
                self.osin.throw("No app has been found.")
            self.apps_total = len(r_apps)
            # Validate json file
            for i in r_apps:
                try:
                    app_info = json.load(open("apps/"+i+"/apps.json"))
                    self.apps[app_info["name"]] = app_info
                except (json.JSONDecodeError, ValueError):
                    continue
            # example:
            # apps = { "calculator": { "version": 1, "exec_path": "apps/calculator/calculator.py" } }

        except FileNotFoundError:
            print("excec")

    def load_apps(self, appname):
        print("K1: "+appname+"\nK2: "+str(self.apps.keys())+"\nKRES: "+str(appname in self.apps.keys()))
        try:
            if appname in self.apps.keys():
                p = appname
                argue = ["test"]
                # Process required arguments
                spliter = ":::"
                r_args = self.apps[p]["required_arguments"]
                print(r_args)
                r_args = r_args[0].replace(" ", "")
                r_args = r_args.split("|")
                print("L: "+str(r_args)+"\nLENGTH: "+str(len(r_args)))
                if len(r_args) == 0:
                    pass
                elif len(r_args) > 1:
                    print("E_TEST1 : PASS")
                    for i in r_args:
                        if spliter in i:
                            tmp = i.split(spliter)
                            cmd_ = None
                            sub_ = None
                            if tmp[0] == tmp[-1]:
                                self.kerin.panic("DAHEL")
                            else:
                                cmd_ = tmp[0]
                                sub_ = tmp[-1]
                                print("E_TEST2 : PASS\nCMD: "+cmd_+"\nSB: "+sub_)
                                if cmd_.upper() == "INSTANCE":
                                    if sub_.lower() == "os":
                                        argue.append(base64.b64encode(bytes(repr(self.osin), "utf-8")).decode("utf-8"))
                                elif sub_.lower() == "kernel":
                                        argue.append(base64.b64encode(bytes(repr(self.kerin), "utf-8")).decode("utf-8"))
                                    
                
                execp = self.apps[p]["exec_path"]
                # Run the Python script as a subprocess and capture the output
                print("RUNNING EXEC")
                #result = subprocess.run(['python3', execp, *argue], shell=True)
                os.system("python3 "+execp+" "+" ".join(argue))
                print("RUNED")
        except subprocess.CalledProcessError as error:
            # Handle any errors that occur during the execution of the subprocess
            print(f"Error: {error}")

        except ValueError as e:
            print("Unknown error\nDEVS_INFO: "+str(e))       
 

        

class OS:
    def __init__(self):
        self.daemon_stat = True
        self.apiv = 1
        self.osver = "1.0"
        self.kernel = Kernel()
        self.appl = App(self, self.kernel)
        self._userwork_directory = "(+)user/anonymous/"
        self._userwork_directory = self._userwork_directory.replace("(+)", os.getcwd())
        print(self._userwork_directory)
        self._workdir = self._userwork_directory
        

    def init(self):
        print("\n\nLogged in as \"Anonymous\"\nFakeOS version 1.0     Kernel: EcroDarg")
        self.shell()
    def shell(self):
        while True:
            try:
                ic = input("> ").split(" ")
                cmd = ic[0]
                args = None
                if len(ic) > 1:
                    ic.pop(0)
                    args = ic
                if cmd == "cd":
                    if args == None:
                        self._workdir = self._userwork_directory
                        continue
                    else:
                        try:
                            path = args[0]
                            _cdir = os.getcwd()
                            os.chdir(path)
                            if not self._userwork_directory in os.getcwd():
                                os.chdir(_cdir)
                                continue
                            self._workdir = os.getcwd()
                        except IndexError:
                            self._workdir = self._userwork_directory
                            continue
                elif cmd == "ls":
                    flist = os.listdir(os.getcwd())
                    f = []
                    d = []
                    hidden = []
                    for i in flist:
                        if args != None:
                            if i.split("/")[-1].startswith("."):
                                hidden.append(i)
                        if os.path.isfile(os.getcwd()+"/"+i):
                            if args != None:
                                if i.split("/")[-1].startswith("."):
                                    continue 
                            f.append(i)
                        if os.path.isdir(os.getcwd()+"/"+i):
                            if args != None:
                                if i.split("/")[-1].startswith("."):
                                    continue 
                            d.append(i)
                    for h in hidden: print(Fore.YELLOW + h + Style.RESET_ALL, end=" ")
                    for dir in d: print(Fore.BLUE + dir + Style.RESET_ALL, end=" " )
                    for file in f: print(Fore.GREEN + file + Style.RESET_ALL, end=" ")
                    print("")

                elif ic == "ksettings":
                    self.kernel.k_settings()
                elif ic == "exit":
                    exit(2)
                elif ic == "cd":
                    pass
                elif ic == "calc": self.appl.load_apps("FCalculator")
            except (IndexError, ValueError, KeyError) as e:
                print("[IGNORE] An Error has been occured, this error not affecting your os, just ignore it\n\nDEV_INFO: "+str(e))
                continue
            except (KeyboardInterrupt, EOFError):
                print("Instead of using CTRL+D/CTRL+C, better if you use \"exit\" commands!")
                continue
class OSApi(OS):
    def __init__(self):
        super(OSApi, self).__init__()
    def getOSAPIVersion (self): return self.apiv
    def getOSVersion (self): return self.osver
    

class KernelApi(Kernel):
    def __init__(self):
        super(KernelApi, self).__init__()
if __name__== "__main__":
    OS().init()

