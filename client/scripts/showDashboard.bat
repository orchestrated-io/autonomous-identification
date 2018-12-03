@echo off
echo starting
@taskkill /f /im MicrosoftEdge.exe /t
cd "%AUTO_ID_PATH%\client"
echo npm install
call npm update @%NPM_SCOPE%/%NPM_PACKAGE%
copy /Y node_modules\@%NPM_SCOPE%\%NPM_PACKAGE%\build\* .
echo get url
python assumeRoleSigninUrl.py > dashboard_url.txt
echo start dashboard
for /f %%x in (dashboard_url.txt) do start "" "%%x"