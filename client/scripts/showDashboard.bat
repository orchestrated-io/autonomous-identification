@echo off
echo starting
cd "%AUTO_ID_PATH%\client"
echo npm install
call npm update @%NPM_SCOPE%/auto-id-keys
copy /Y node_modules\@%NPM_SCOPE%\auto-id-keys\build\* .
echo get url
python assumeRoleSigninUrl.py > dashboard_url.txt
echo start dashboard
for /f %%x in (dashboard_url.txt) do start "" "%%x"