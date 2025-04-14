import shutil
import psp
import os


cwd = os.getcwd()
main_savefile = os.path.join(cwd, "ULJM05800/MHP3RD.BIN")
savedata = psp.SavedataCipher(6)
pspsavedata = psp.PSPSavedataCipher(6)

def create_backup():
    shutil.copy(main_savefile, os.path.join(cwd, "MHP3RD.BIN.bak"))

def PSPDecrypt():
    try:
        create_backup()
        print("PSP decrypting...")
        pspsavedata.decrypt_file(pspsavedata_file=main_savefile, out_file=os.path.join(cwd, "pspsave.BIN"))
        os.remove(main_savefile)
        print("Done!")
        return True
    except Exception as e:
        print(f"Error in PSP Decrypt: {e}")
        return False

def Decrypt():
    try:
        print("Decrypting...")
        savedata.decrypt_file(savedata_file=os.path.join(cwd, "pspsave.BIN"), out_file=os.path.join(cwd, "save.BIN"))
        os.remove(os.path.join(cwd, "pspsave.BIN"))
        print("Done!")
        return True
    except Exception as e:
        print(f"Error in Decrypt: {e}")
        return False

def Encrypt():
    try:
        print("Encrypting...")
        savedata.encrypt_file(savedata_file=os.path.join(cwd, "save.BIN"), out_file=os.path.join(cwd, "pspsave.BIN"))
        os.remove(os.path.join(cwd, "save.BIN"))
        print("Done!")
        return True
    except Exception as e:
        print(f"Error in Encrypt: {e}")
        return False

def PSPEncrypt():
    try:
        print("PSP encrypting...")
        pspsavedata.encrypt_file(pspsavedata_file=os.path.join(cwd, "pspsave.BIN"), out_file=main_savefile)
        os.remove(os.path.join(cwd, "pspsave.BIN"))
        print("Done!")
        os.remove(os.path.join(cwd, "MHP3RD.BIN.bak"))
        return True
    except Exception as e:
        print(f"Error in PSP Encrypt: {e}")
        return False