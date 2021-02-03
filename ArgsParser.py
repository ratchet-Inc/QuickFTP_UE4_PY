import sys
import os

def GetDefaultArgs()-> dict:
    data = {
        "host": "localhost",
        "username": "",
        "passw": "",
        "dbName": "",
        "listenPort": 8089,
        "listenHost": "127.0.0.1",
        "storageDir" :"C:/uploads/"
        }
    return data

def ParseArguments(defaults = GetDefaultArgs()):
    for i in range(len(sys.argv)):
        if "-host" == sys.argv[i].lower():
            defaults["host"] = sys.argv[i + 1]
            pass
        if "-uname" == sys.argv[i].lower():
            defaults["username"] = sys.argv[i + 1]
            pass
        if "-userpass" == sys.argv[i].lower():
            defaults["passw"] = sys.argv[i + 1]
            pass
        if "-dbname" == sys.argv[i].lower():
            defaults["dbName"] = sys.argv[i + 1]
            pass
        if "-lport" == sys.argv[i].lower():
            defaults["listenPort"] = sys.argv[i + 1]
            pass
        if "-lhost" == sys.argv[i].lower():
            defaults["listenHost"] = sys.argv[i + 1]
            pass
        if "-storageRoot".lower() == sys.argv[i].lower():
            defaults["storageDir"] = sys.argv[i + 1]
            pass
        pass
    return defaults
