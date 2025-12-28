import sys
import os

print("CWD:", os.getcwd())
try:
    from project_config import Config
    print("Config imported from:", Config.__module__)
    try:
        print("DB_PATH:", Config.DB_PATH)
    except AttributeError as e:
        print("AttributeError:", e)
        print("Dir(Config):", dir(Config))
except ImportError as e:
    print("ImportError:", e)
