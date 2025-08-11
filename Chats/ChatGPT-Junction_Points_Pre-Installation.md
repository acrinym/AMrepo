# Junction Points Pre-Installation

#### You:
Can I create a junction point or something in win11 that acts as if it's on the main C Drive but is actually on D before it's ever even installed? 

#### ChatGPT:
Yes, you can use junction points (or symbolic links) in Windows 11 to have a folder appear as if it’s on the C: drive while its actual data resides on the D: drive. However, doing this *before* Windows is installed introduces some additional complexities. Here’s what you need to consider:

---

### Using Junction Points in Windows 11

- **What Are Junction Points?**\
  Junction points are a type of reparse point that lets you create a directory link. When you access the junction (e.g., on C:), Windows transparently redirects you to the target location (e.g., on D:).

- **The Command:**\
  Once in an elevated command prompt, the basic syntax is:
  ```cmd
  mklink /J "C:\Path\LinkFolder" "D:\Path\TargetFolder"
  ```
  This creates a junction point at `C:\Path\LinkFolder` that points to `D:\Path\TargetFolder`.

---

### Setting Up Before Windows Installation

- **Pre-Installation Environment:**\
  Since you’re aiming to have this configuration in place *before* Windows is installed, you’d need to work within a pre-installation environment such as **WinPE (Windows Preinstallation Environment)**. In WinPE, you can:
  - **Partition and Format** your drives as needed.
  - **Create the Junction Points:** Manually run the `mklink` command from an elevated command prompt within WinPE.
- **Considerations with Windows Setup:**
  - **Installer Behavior:** The Windows installer typically creates and formats partitions based on your selections. If you’ve already set up a partition with your junction points in WinPE, you need to ensure that Windows Setup doesn’t overwrite these changes or reassign drive letters unexpectedly.
  - **System Directories:** If your intent is to have essential system folders (or user profiles) reside on D: via junction points, be cautious. Windows expects certain directories (like `Windows`, `Program Files`, or `Users`) to be in standard locations, and redirecting them can complicate updates or system recovery.

---

### Alternative Approaches

- **Post-Installation Configuration:**\
  A more common approach is to install Windows normally and then move specific directories (like parts of the user profile, Program Files, etc.) to D: and create junction points on C: pointing to these new locations. This method gives you full control once Windows is running and can be less disruptive.

- **Mount Points Instead:**\
  Instead of a junction point, you can also consider using **mount points**. This method involves mounting the D: drive (or a partition of it) as a folder on C::
  - **Disk Management:** Use the Disk Management tool to assign a folder path on C: to the D: partition.
  - This approach is often more transparent to Windows and can reduce some of the risks associated with junctions.

---

### Final Thoughts

- **Plan Carefully:**\
  Manipulating system paths and drive assignments before installation can lead to unexpected behavior if not done correctly. If your goal is to manage space or separate system files from user data, weigh the pros and cons of pre-installation modifications versus post-installation adjustments.

- **Testing in WinPE:**\
  If you decide to proceed pre-installation, thoroughly test your setup in WinPE to confirm that:
  - The junction points behave as expected.
  - Windows Setup recognizes your intended configuration without conflict.

---

**In Summary:**\
Yes, it’s technically possible to create a junction point so that a folder on C: redirects to D:, even before Windows is fully installed—but it requires working in a pre-installation environment (like WinPE) and careful planning to ensure that Windows Setup doesn’t interfere with your configuration.

Feel free to ask if you need more details on any of these steps or further guidance on setting up your environment!


#### You:
Not before windows I'm trying to install Serum VST presets. And they take up a lot of space, so I want to create a folder on D that will have the presets installed *there* instead of on C where it thinks it is installing.

#### ChatGPT:
Yes, you can offload Serum VST presets to your D: drive while tricking the installer into thinking it's installing on C:. The idea is to create a directory junction (or symbolic link) so that when Serum writes presets to its expected location on C:, Windows transparently redirects those writes to a folder on D:.

Below are step-by-step instructions and some points to keep in mind:

---

## Step-by-Step Guide

1. **Determine the Target Path**
   - Identify the folder where Serum expects to install its presets on the C: drive (e.g., something like `C:\Program Files\Xfer\Serum\Presets`).
   - Decide on the destination folder on your D: drive where you want the presets to actually reside (e.g., `D:\SerumPresets`).

2. **Prepare the Destination Folder**
   - Create the folder on D: (if it doesn’t already exist).\
     Example:
     ```cmd
     mkdir D:\SerumPresets
     ```

3. **Backup or Remove Existing Folder (If Necessary)**
   - If a folder already exists at the target location on C:, **move** or **rename** it so you can create the junction point without conflicts.
   - For example, rename:
     ```cmd
     ren "C:\Program Files\Xfer\Serum\Presets" "C:\Program Files\Xfer\Serum\Presets_backup"
     ```

4. **Create the Junction Point**
   - Open Command Prompt as an administrator.
   - Use the `mklink` command with the `/J` flag to create a junction point.\
     Example command:
     ```cmd
     mklink /J "C:\Program Files\Xfer\Serum\Presets" "D:\SerumPresets"
     ```
   - If the command is successful, you'll see a message indicating that the junction has been created.

5. **Verify the Setup**
   - Navigate to `C:\Program Files\Xfer\Serum\Presets` in File Explorer. It should look like a normal folder, but its contents are actually stored on D:.
   - You can also run the following command in Command Prompt to view the link:
     ```cmd
     dir "C:\Program Files\Xfer\Serum"
     ```

6. **Install Serum VST**
   - Proceed with installing Serum. When the installer writes the presets to its designated location on C:, the files will be stored on D: thanks to the junction.

---

## Additional Considerations

- **Permissions:**
  - Ensure you have administrative rights when creating the junction.

- **Installer Behavior:**
  - Most installers follow junction points transparently. However, if the installer performs additional checks (like verifying free space on C:), you might need to test this configuration.

- **Alternate Approach:**
  - **Symbolic Link (`/D`):**\
    If for any reason a junction point (`/J`) does not work as expected, you might try a directory symbolic link using:
    ```cmd
    mklink /D "C:\Program Files\Xfer\Serum\Presets" "D:\SerumPresets"
    ```
    Note that creating a symbolic link might require enabling Developer Mode in Windows 11 or running as an administrator.

- **Reversibility:**
  - If you ever need to reverse the process, simply delete the junction point (it appears as a folder) and restore the original folder if needed.

---

By following these steps, Serum will install its presets to what it perceives as the default folder on C:, but the actual data will reside on your D: drive, helping you manage disk space efficiently.

If you run into any issues or have more questions, feel free to ask!


#### You:
How do we find out where it is about to install with Process Hacker, etc? 

#### ChatGPT:
Determining where an installer is writing files can be really helpful before creating your junction or symlink. Here are a couple of methods you can use with Process Hacker and Process Monitor to track down the target installation path:

---

## Using Process Hacker

Process Hacker lets you inspect open handles, which can reveal what directories or files an installer is interacting with.

1. **Run Process Hacker as Administrator**
   - Right-click the Process Hacker shortcut and select “Run as administrator” to ensure you have full access to process details.

2. **Start the Installer**
   - Launch your Serum VST installer so that it begins its installation process.

3. **Locate the Installer Process**
   - In Process Hacker’s main window, find the installer process (it might be named something like `SerumSetup.exe` or similar).

4. **Inspect Open Handles**
   - Right-click the installer process and choose **Properties**.
   - Go to the **Handles** tab.
   - Use the search/filter box to look for keywords such as `Program Files`, `Serum`, or even the specific folder name you suspect (e.g., `Xfer` or `Presets`).
   - Reviewing the list of open handles may reveal the path where files are being created or modified.

> **Note:**\
> Sometimes an installer might not have opened the target directory immediately, so you might need to refresh or check again as the installation process advances.

---

## Using Process Monitor (ProcMon)

Process Monitor from Sysinternals offers a more dynamic view of file system activity and is often more straightforward for tracking file writes.

1. **Download and Run ProcMon**
   - Download Process Monitor from [Microsoft Sysinternals](https://docs.microsoft.com/en-us/sysinternals/downloads/procmon).
   - Run it as an administrator.

2. **Set Up Filters**
   - Click on the **Filter** icon (or press **Ctrl+L**).
   - Add a filter for the installer process by setting:
     - **Condition:** `Process Name`
     - **Operator:** `is`
     - **Value:** the installer executable name (e.g., `SerumSetup.exe`).
   - Optionally, you can add a filter for operations like `CreateFile` to zero in on file access events.
   - Click **Add** then **OK** to apply the filter.

3. **Monitor the File Activity**
   - Start the installer if it isn’t already running.
   - ProcMon will log all file system activity for the installer. Look for file operations that include directory paths.
   - Pay attention to events where files are being written or directories are being accessed; these will reveal the intended installation folder.

4. **Analyze the Logs**
   - Once you see a file being written to (for example, something like `C:\Program Files\Xfer\Serum\Presets`), you’ll have a good indication of the target folder.
   - You can pause or stop logging once you’ve captured enough information.

---

## Summary

- **Process Hacker** can help you inspect what directories the installer has open by checking its handles.
- **Process Monitor** provides real-time tracking of file system operations, making it easier to spot the exact paths being accessed during installation.

By using these tools, you can confidently determine where Serum is about to install its presets, allowing you to set up your junction or symlink on C: pointing to D: with confidence.

Feel free to ask if you need more details on any of these steps or run into any issues along the way!


#### You:
Can I use system informer to determine paths that would be installed to, then create junctions before installing? 

#### ChatGPT:
Yes, you can use a tool like System Informer to help determine which paths an installer is planning to use—**if** it provides the necessary insights into file and registry activity. However, there are some considerations and alternatives to keep in mind:

---

### What to Expect from System Informer

- **Capabilities Vary:**
  - Some system information tools can show you details about active processes, registry entries, or even logs from previous installations, but they might not be as effective at real-time file system monitoring as dedicated tools.
  - If System Informer is configured to monitor file or registry activity related to the installer, you might see which directories it’s targeting.

- **Pre-Installation Insights:**
  - You may be able to spot the intended install paths by watching for activity or by reviewing any installer logs or configuration files that System Informer picks up.
  - This is especially useful if the installer uses pre-set defaults (like installing presets to a specific folder in `C:\Program Files\Xfer\Serum\`).

---

### Creating Junctions Based on the Identified Paths

If you confirm the target directory (e.g., where Serum installs its presets), you can create a junction point **before** starting the installation:

1. **Confirm the Target Path:**
   - Use System Informer (or another tool) to identify the intended directory.
   - Double-check by reviewing installer options or any configuration files if available.

2. **Prepare the Destination on D:**
   - Create the folder on D: where you want the presets to reside (e.g., `D:\SerumPresets`).

3. **Backup or Remove Any Existing Folder:**
   - If a folder already exists at the target location on C:, move or rename it to avoid conflicts.

4. **Create the Junction Point:**
   - Open an elevated Command Prompt and run:
     ```cmd
     mklink /J "C:\Program Files\Xfer\Serum\Presets" "D:\SerumPresets"
     ```
   - This way, when the installer writes to the presets folder on C:, Windows will redirect those writes to D:.

---

### Alternatives and Recommendations

- **Process Monitor (ProcMon):**
  - For real-time tracking of file system events, ProcMon is often more reliable. It allows you to filter by process name and monitor file operations like `CreateFile` or `WriteFile` to reveal exactly where files are being written.

- **Installer Documentation:**
  - Sometimes the easiest route is checking the documentation or installer settings. Many installers offer a custom install path option.

- **Test in a Controlled Environment:**
  - Before applying the junction in your main setup, consider testing the process to ensure that the installer doesn’t encounter unexpected issues.

---

### In Summary

- **Yes**, if System Informer provides the necessary insight into the intended installation paths, you can use it to determine where Serum is planning to install its presets.
- Once you know the path, you can safely create a junction point from that location on C: to your desired folder on D: **before** running the installer.
- Just be mindful that tools like Process Monitor might offer a more detailed and real-time picture of what’s happening during the installation.

If you have any more questions or need further guidance, feel free to ask!
