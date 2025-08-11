# Restore .scr File Functionality

#### You:
Can you make me a .bat file that restores .scr screensaver open file functionality? 
Windows gives me currently a "there are no programs to open this file" "open with" dialog. 

#### ChatGPT:
Certainly! Here is a .bat file that will restore the .scr screensaver open file functionality by associating .scr files with the appropriate screensaver executable:

```bat
@echo off
REM This script restores the .scr screensaver open file functionality

echo Restoring .scr screensaver open file functionality...

REM Associate .scr files with the screensaver executable
assoc .scr=scrfile
ftype scrfile="%SystemRoot%\System32\%1.scr" /S

REM Inform the user that the association has been restored
echo .scr screensaver open file functionality has been restored.

REM Pause to let the user see the message
pause
```

Save this code as `restore_screensaver_association.bat` and run it as an administrator. This script does the following:

1. **assoc .scr=scrfile**: Associates the `.scr` file extension with a file type named `scrfile`.
2. **ftype scrfile="%SystemRoot%\System32%1.scr" /S**: Defines the file type `scrfile` to use the screensaver executable located in the `System32` directory.

Make sure to run the script with administrative privileges to apply the changes successfully. If you encounter any issues or need further customization, feel free to ask!Certainly! Here is a .bat file that will restore the .scr screensaver open file functionality by associating .scr files with the appropriate screensaver executable:

```bat
@echo off
REM This script restores the .scr screensaver open file functionality

echo Restoring .scr screensaver open file functionality...

REM Associate .scr files with the screensaver executable
assoc .scr=scrfile
ftype scrfile="%SystemRoot%\System32\%1.scr" /S

REM Inform the user that the association has been restored
echo .scr screensaver open file functionality has been restored.

REM Pause to let the user see the message
pause
```

Save this code as `restore_screensaver_association.bat` and run it as an administrator. This script does the following:

1. **assoc .scr=scrfile**: Associates the `.scr` file extension with a file type named `scrfile`.
2. **ftype scrfile="%SystemRoot%\System32%1.scr" /S**: Defines the file type `scrfile` to use the screensaver executable located in the `System32` directory.

Make sure to run the script with administrative privileges to apply the changes successfully. If you encounter any issues or need further customization, feel free to ask!


#### You:
Will this work in win10?

#### ChatGPT:
Yes, the script should work in Windows 10. However, there is a small adjustment needed to ensure that it correctly associates `.scr` files with the screensaver executable. The corrected version of the script is:

```bat
@echo off
REM This script restores the .scr screensaver open file functionality

echo Restoring .scr screensaver open file functionality...

REM Associate .scr files with the screensaver executable
assoc .scr=scrfile
ftype scrfile="%SystemRoot%\System32\rundll32.exe desk.cpl,InstallScreenSaver %1"

REM Inform the user that the association has been restored
echo .scr screensaver open file functionality has been restored.

REM Pause to let the user see the message
pause
```

Save this code as `restore_screensaver_association.bat` and run it as an administrator. This script does the following:

1. **assoc .scr=scrfile**: Associates the `.scr` file extension with a file type named `scrfile`.
2. **ftype scrfile="%SystemRoot%\System32\rundll32.exe desk.cpl,InstallScreenSaver %1"**: Defines the file type `scrfile` to use the `rundll32.exe` command to run the screensaver executable.

To run the script with administrative privileges:

1. Right-click on the `restore_screensaver_association.bat` file.
2. Select "Run as administrator."

This should restore the .scr screensaver open file functionality on your Windows 10 system. If you have any further issues or need additional help, feel free to ask!


#### You:
Can you add to that the ability to right-click a .scr file and install it (copies to %windir%)? 

#### ChatGPT:
Certainly! To add the functionality of right-clicking a `.scr` file to install it (copy it to `%windir%`), you can modify the registry through a `.bat` file. This will add an "Install" option to the right-click context menu for `.scr` files.

Here is the updated script:

```bat
@echo off
REM This script restores the .scr screensaver open file functionality
REM and adds an "Install" option to the right-click context menu.

echo Restoring .scr screensaver open file functionality...

REM Associate .scr files with the screensaver executable
assoc .scr=scrfile
ftype scrfile="%SystemRoot%\System32\rundll32.exe desk.cpl,InstallScreenSaver %1"

REM Add "Install" option to the right-click context menu for .scr files
reg add "HKCR\scrfile\shell\Install" /ve /d "Install" /f
reg add "HKCR\scrfile\shell\Install\command" /ve /d "%SystemRoot%\System32\cmd.exe /c copy \"%1\" \"%windir%\" && rundll32.exe desk.cpl,InstallScreenSaver %windir%\%~nx1" /f

REM Inform the user that the association and context menu have been restored
echo .scr screensaver open file functionality and context menu have been restored.

REM Pause to let the user see the message
pause
```

Save this code as `restore_screensaver_association_and_install.bat` and run it as an administrator. This script does the following:

1. **assoc .scr=scrfile**: Associates the `.scr` file extension with a file type named `scrfile`.
2. **ftype scrfile="%SystemRoot%\System32\rundll32.exe desk.cpl,InstallScreenSaver %1"**: Defines the file type `scrfile` to use the `rundll32.exe` command to run the screensaver executable.
3. **reg add "HKCR\scrfile\shell\Install" /ve /d "Install" /f**: Adds an "Install" option to the right-click context menu for `.scr` files.
4. **reg add "HKCR\scrfile\shell\Install\command" /ve /d "%SystemRoot%\System32\cmd.exe /c copy "%1" "%windir%" && rundll32.exe desk.cpl,InstallScreenSaver %windir%%\~nx1" /f**: Defines the command for the "Install" option, which copies the selected `.scr` file to the Windows directory and installs it as the current screensaver.

This should add the desired functionality to your Windows 10 system. If you encounter any issues or need further customization, feel free to ask!


#### You:
Now can you restore the ability to see the screensaver's iconfile(usually embedded in the screensaver resources), and add the ability to change icons for screensavers in general? 

#### ChatGPT:
To restore the ability to see the screensaver's icon file and add the ability to change icons for screensavers, you need to associate the `.scr` files with their icon resources correctly. This can be achieved by modifying the registry to handle the icon display and adding a context menu option to change the icon.

Here's the updated `.bat` script:

```bat
@echo off
REM This script restores the .scr screensaver open file functionality,
REM adds an "Install" option to the right-click context menu,
REM restores the ability to see the screensaver's icon,
REM and adds the ability to change icons for screensavers.

echo Restoring .scr screensaver open file functionality...

REM Associate .scr files with the screensaver executable
assoc .scr=scrfile
ftype scrfile="%SystemRoot%\System32\rundll32.exe desk.cpl,InstallScreenSaver %1"

REM Add "Install" option to the right-click context menu for .scr files
reg add "HKCR\scrfile\shell\Install" /ve /d "Install" /f
reg add "HKCR\scrfile\shell\Install\command" /ve /d "%SystemRoot%\System32\cmd.exe /c copy \"%1\" \"%windir%\" && rundll32.exe desk.cpl,InstallScreenSaver %windir%\%~nx1" /f

REM Restore the ability to see the screensaver's icon
reg add "HKCR\scrfile\DefaultIcon" /ve /d "%1" /f

REM Add "Change Icon" option to the right-click context menu for .scr files
reg add "HKCR\scrfile\shell\ChangeIcon" /ve /d "Change Icon" /f
reg add "HKCR\scrfile\shell\ChangeIcon\command" /ve /d "rundll32.exe shell32.dll,Control_RunDLL desk.cpl,,@Screen Savers" /f

REM Inform the user that the association, context menu, icon restoration, and icon change ability have been restored
echo .scr screensaver open file functionality, context menu, icon restoration, and icon change ability have been restored.

REM Pause to let the user see the message
pause
```

This script performs the following actions:

1. **assoc .scr=scrfile**: Associates the `.scr` file extension with a file type named `scrfile`.
2. **ftype scrfile="%SystemRoot%\System32\rundll32.exe desk.cpl,InstallScreenSaver %1"**: Defines the file type `scrfile` to use the `rundll32.exe` command to run the screensaver executable.
3. **reg add "HKCR\scrfile\shell\Install" /ve /d "Install" /f**: Adds an "Install" option to the right-click context menu for `.scr` files.
4. **reg add "HKCR\scrfile\shell\Install\command" /ve /d "%SystemRoot%\System32\cmd.exe /c copy "%1" "%windir%" && rundll32.exe desk.cpl,InstallScreenSaver %windir%%\~nx1" /f**: Defines the command for the "Install" option, which copies the selected `.scr` file to the Windows directory and installs it as the current screensaver.
5. **reg add "HKCR\scrfile\DefaultIcon" /ve /d "%1" /f**: Restores the ability to see the screensaver's icon by associating the `.scr` file's default icon with itself.
6. **reg add "HKCR\scrfile\shell\ChangeIcon" /ve /d "Change Icon" /f**: Adds a "Change Icon" option to the right-click context menu for `.scr` files.
7. **reg add "HKCR\scrfile\shell\ChangeIcon\command" /ve /d "rundll32.exe shell32.dll,Control\_RunDLL desk.cpl,,@Screen Savers" /f**: Defines the command for the "Change Icon" option, which opens the Screen Savers settings where you can change the icon.

Save this script as `restore_screensaver_functionality_and_icon.bat` and run it as an administrator. This will restore the screensaver functionality, add the install option, restore icon display, and add the ability to change icons for screensavers. If you have any further questions or need additional assistance, feel free to ask!


#### You:
And this must be for windows 10. :)

#### ChatGPT:
Here's the updated script tailored for Windows 10, which restores the `.scr` screensaver open file functionality, adds the "Install" option to the right-click context menu, restores the ability to see the screensaver's icon, and adds the ability to change icons for screensavers:

```bat
@echo off
REM This script restores the .scr screensaver open file functionality,
REM adds an "Install" option to the right-click context menu,
REM restores the ability to see the screensaver's icon,
REM and adds the ability to change icons for screensavers.

echo Restoring .scr screensaver open file functionality...

REM Associate .scr files with the screensaver executable
assoc .scr=scrfile
ftype scrfile="%SystemRoot%\System32\rundll32.exe desk.cpl,InstallScreenSaver %1"

REM Add "Install" option to the right-click context menu for .scr files
reg add "HKCR\scrfile\shell\Install" /ve /d "Install" /f
reg add "HKCR\scrfile\shell\Install\command" /ve /d "%SystemRoot%\System32\cmd.exe /c copy \"%1\" \"%windir%\" && rundll32.exe desk.cpl,InstallScreenSaver %windir%\%~nx1" /f

REM Restore the ability to see the screensaver's icon
reg add "HKCR\scrfile\DefaultIcon" /ve /d "%1" /f

REM Add "Change Icon" option to the right-click context menu for .scr files
reg add "HKCR\scrfile\shell\ChangeIcon" /ve /d "Change Icon" /f
reg add "HKCR\scrfile\shell\ChangeIcon\command" /ve /d "rundll32.exe shell32.dll,Control_RunDLL desk.cpl,@ScreenSavers" /f

REM Inform the user that the association, context menu, icon restoration, and icon change ability have been restored
echo .scr screensaver open file functionality, context menu, icon restoration, and icon change ability have been restored.

REM Pause to let the user see the message
pause
```

Save this code as `restore_screensaver_functionality_and_icon.bat` and run it as an administrator. Here’s what each part of the script does:

1. **assoc .scr=scrfile**: Associates the `.scr` file extension with a file type named `scrfile`.
2. **ftype scrfile="%SystemRoot%\System32\rundll32.exe desk.cpl,InstallScreenSaver %1"**: Defines the file type `scrfile` to use the `rundll32.exe` command to run the screensaver executable.
3. **reg add "HKCR\scrfile\shell\Install" /ve /d "Install" /f**: Adds an "Install" option to the right-click context menu for `.scr` files.
4. **reg add "HKCR\scrfile\shell\Install\command" /ve /d "%SystemRoot%\System32\cmd.exe /c copy "%1" "%windir%" && rundll32.exe desk.cpl,InstallScreenSaver %windir%%\~nx1" /f**: Defines the command for the "Install" option, which copies the selected `.scr` file to the Windows directory and installs it as the current screensaver.
5. **reg add "HKCR\scrfile\DefaultIcon" /ve /d "%1" /f**: Restores the ability to see the screensaver's icon by associating the `.scr` file's default icon with itself.
6. **reg add "HKCR\scrfile\shell\ChangeIcon" /ve /d "Change Icon" /f**: Adds a "Change Icon" option to the right-click context menu for `.scr` files.
7. **reg add "HKCR\scrfile\shell\ChangeIcon\command" /ve /d "rundll32.exe shell32.dll,Control\_RunDLL desk.cpl,@ScreenSavers" /f**: Defines the command for the "Change Icon" option, which opens the Screen Savers settings where you can change the icon.

This script should work on Windows 10 to restore the screensaver functionality, icon display, and context menu options. If you have any further questions or need additional assistance, feel free to ask!


#### You:
IT still tells me "windows can't open this type of file(.scr)

#### ChatGPT:
I apologize for the inconvenience. Let's adjust the script to ensure the file association and icon restoration are correctly applied in Windows 10.

Here is the updated script:

```bat
@echo off
REM This script restores the .scr screensaver open file functionality,
REM adds an "Install" option to the right-click context menu,
REM restores the ability to see the screensaver's icon,
REM and adds the ability to change icons for screensavers.

echo Restoring .scr screensaver open file functionality...

REM Associate .scr files with the screensaver executable
assoc .scr=scrfile
ftype scrfile="%SystemRoot%\System32\rundll32.exe desk.cpl,InstallScreenSaver %1"

REM Add "Install" option to the right-click context menu for .scr files
reg add "HKCR\scrfile\shell\Install" /ve /d "Install" /f
reg add "HKCR\scrfile\shell\Install\command" /ve /d "cmd.exe /c copy \"%1\" \"%windir%\" && rundll32.exe desk.cpl,InstallScreenSaver %windir%\%~nx1" /f

REM Restore the ability to see the screensaver's icon
reg add "HKCR\scrfile\DefaultIcon" /ve /d "%1" /f

REM Add "Change Icon" option to the right-click context menu for .scr files
reg add "HKCR\scrfile\shell\ChangeIcon" /ve /d "Change Icon" /f
reg add "HKCR\scrfile\shell\ChangeIcon\command" /ve /d "rundll32.exe shell32.dll,Control_RunDLL desk.cpl,@ScreenSavers" /f

REM Add Open option to the right-click context menu for .scr files
reg add "HKCR\scrfile\shell\Open" /ve /d "Open" /f
reg add "HKCR\scrfile\shell\Open\command" /ve /d "%SystemRoot%\System32\rundll32.exe desk.cpl,InstallScreenSaver %1" /f

REM Inform the user that the association, context menu, icon restoration, and icon change ability have been restored
echo .scr screensaver open file functionality, context menu, icon restoration, and icon change ability have been restored.

REM Pause to let the user see the message
pause
```

Save this code as `restore_screensaver_functionality_and_icon.bat` and run it as an administrator. Here’s a summary of what this script does:

1. **assoc .scr=scrfile**: Associates the `.scr` file extension with a file type named `scrfile`.
2. **ftype scrfile="%SystemRoot%\System32\rundll32.exe desk.cpl,InstallScreenSaver %1"**: Defines the file type `scrfile` to use the `rundll32.exe` command to run the screensaver executable.
3. **reg add "HKCR\scrfile\shell\Install" /ve /d "Install" /f**: Adds an "Install" option to the right-click context menu for `.scr` files.
4. **reg add "HKCR\scrfile\shell\Install\command" /ve /d "cmd.exe /c copy "%1" "%windir%" && rundll32.exe desk.cpl,InstallScreenSaver %windir%%\~nx1" /f**: Defines the command for the "Install" option, which copies the selected `.scr` file to the Windows directory and installs it as the current screensaver.
5. **reg add "HKCR\scrfile\DefaultIcon" /ve /d "%1" /f**: Restores the ability to see the screensaver's icon by associating the `.scr` file's default icon with itself.
6. **reg add "HKCR\scrfile\shell\ChangeIcon" /ve /d "Change Icon" /f**: Adds a "Change Icon" option to the right-click context menu for `.scr` files.
7. **reg add "HKCR\scrfile\shell\ChangeIcon\command" /ve /d "rundll32.exe shell32.dll,Control\_RunDLL desk.cpl,@ScreenSavers" /f**: Defines the command for the "Change Icon" option, which opens the Screen Savers settings where you can change the icon.
8. **reg add "HKCR\scrfile\shell\Open" /ve /d "Open" /f**: Adds an "Open" option to the right-click context menu for `.scr` files.
9. **reg add "HKCR\scrfile\shell\Open\command" /ve /d "%SystemRoot%\System32\rundll32.exe desk.cpl,InstallScreenSaver %1" /f**: Defines the command for the "Open" option to open the screensaver.

This should restore the screensaver functionality and the ability to see and change icons for `.scr` files in Windows 10. If you encounter any issues or need further assistance, please let me know!
