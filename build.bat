@ECHO OFF
CLS
COLOR 0A

::Begin
:: Set script name based on current directory
FOR /F "Delims=" %%D IN ('ECHO %CD%') DO SET ScriptName=%%~nD

:: Set window title
TITLE %ScriptName% Build Script

::Set build directory
SET BuildDir=..\%ScriptName%.build\

::Set exclude file name
SET ExcludeFile=%BuildDir%exclude.txt

::Erase the build directory
IF EXIST %BuildDir% (
	RMDIR %BuildDir% /S /Q
)
MD %BuildDir%

::Create the exclude file
ECHO .ini>>%ExcludeFile%
ECHO .pyc>>%ExcludeFile%
ECHO .pyo>>%ExcludeFile%
ECHO .svn>>%ExcludeFile%
ECHO build.bat>>%ExcludeFile%
ECHO build.sh>>%ExcludeFile%
ECHO thumbs.db>>%ExcludeFile%
ECHO resources\cache>>%ExcludeFile%
ECHO resources\config\settings.user.xml>>%ExcludeFile%

::Actually copy the files
XCOPY * %BuildDir% /S /I /EXCLUDE:%ExcludeFile%

::Remove the exclude file
DEL %ExcludeFile%

PAUSE