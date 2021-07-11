@ECHO off
CALL cbuild.bat
::Images have to be done specially
python -O -m PyInstaller -w --noconfirm --name voxel^
    --path="./common"^
    --path="./csource"^
    --path="./utils"^
    --add-data="./img/1C.png;img"^
    --add-data="./img/1H.png;img"^
    --add-data="./liblines.dll;."^
    --add-data="./settings.ini;."^
    main.py
