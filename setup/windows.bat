@echo off
@REM [BETA] v
@REM This script will build the Windows version of the application. 
@REM Created by: auroraisluna - For bugs or issues please open an issue on GitHub!

@REM We want to check if the script is being run from the correct directory.
@REM If it isn't we will exit the script.
if not exist src\main.py (
    echo !!!!!
    echo This script must be run from the root directory of the project.
    echo Please run the script from the root directory of the project.
    echo Use 'cd ..' to move up one directory and then run the script again with 'setup\buildWindows.bat'
    echo !!!!!
    exit /b 1
)


@REM First we need to make sure that the dist & build directory exists and is empty.
CALL :LABEL
echo Creating dist directory...
if exist dist rmdir /s /q dist
if not exist dist mkdir dist
echo Creating build directory...
if exist build rmdir /s /q build
if not exist build mkdir build

CALL :LABEL
echo Building application...
echo. 

@REM Now we need to build the application with pipenv 
python -m pipenv run pyinstaller -F --icon=src/assets/poro.ico src/main.py --collect-all charset_normalizer -n CapsuleFarmerEvolved

@REM Now we need to copy all the required files to the build directory
CALL :LABEL
echo Copying application files...
xcopy /v /y dist\ build\
xcopy /v /y config\ build\

@REM Prompt the user to confirm that they want to create the zip file
CALL :LABEL
echo Would you like to create a zip file of the application? (Requires 7zip on PATH) [Y/N]
echo.

set /p createZipFile=

set zipFileAnswer=no
if %createZipFile%==Y set zipFileAnswer=yes
if %createZipFile%==y set zipFileAnswer=yes

if %zipFileAnswer%==yes (

    CALL :LABEL
    echo Creating zip file...

    cd build

    @REM Delete the zip file if it already exists
    if exist CapsuleFarmerEvolved.zip del CapsuleFarmerEvolved.zip

    @REM Delete 'CapsuleFarmerEvolved' directory
    if exist CapsuleFarmerEvolved rmdir /s /q CapsuleFarmerEvolved

    @REM Create the zip file
    7z a -tzip CapsuleFarmerEvolved.zip *

    cd ..

) 

@REM Clean up the dist directory
CALL :LABEL

echo Would you like to delete the dist directory? [Y/N]
echo.

set deleteDistAnswer=no
set /p deleteDist=
if %deleteDist%==Y set deleteDistAnswer=yes
if %deleteDist%==y set deleteDistAnswer=yes
if %deleteDistAnswer%=="yes" (

    CALL :LABEL
    echo Deleting dist directory...
    rmdir /s /q dist

)

CALL :LABEL
echo [OK] Application build complete. You can find the application in the build directory.
echo.
pause
exit /b 0



:LABEL
cls
echo ========================================
echo.
echo CapsuleFarmerEvolved Windows Build Script
echo.
echo ========================================
echo.
goto :EOF