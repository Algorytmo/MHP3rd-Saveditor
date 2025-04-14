import crypto_func
import time
import os


def main():
    try:
        if crypto_func.PSPDecrypt() and crypto_func.Decrypt():
            print("\nWaiting for file editing")
            import gui
            gui.main()
            while not os.path.exists(os.path.join(os.getcwd(), "modifications_done.flag")): # Check notification flag
                time.sleep(1)
            print("\nDone! Starting encrypting")
            if crypto_func.Encrypt() and crypto_func.PSPEncrypt():
                os.remove(os.path.join(os.getcwd(), "modifications_done.flag"))
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()