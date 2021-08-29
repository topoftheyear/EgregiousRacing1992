@ECHO off
::Images have to be done specially
python -O -m PyInstaller -w --noconfirm --name "Egregious Racing 1992"^
    --icon=icon.ico^
    --path="./common"^
    --path="./utils"^
    --add-data="./img/*;img"^
    --add-data="./liblines.dll;."^
    --add-data="./settings.ini;."^
    --add-data="./leaderboard.json;."^
    --add-data="./visitor2.ttf;."^
    --add-data="./README.md;."^
    --clean main.py^
    main.py
pause
