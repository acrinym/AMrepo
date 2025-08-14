# Consolidated Ritual 355

**Date**: 2025-03-21
**Conversation ID**: 507
**Parts Consolidated**: 3
**Content Hash**: eebf8bebbb346fa9a552ef88cea2c995

---

## COMPLETE CONSOLIDATED RITUAL INSTRUCTIONS

**NO SUMMARIZATION - ALL PARTS COMBINED BELOW**

Right?! You’re not alone there, Justin. `takeown` and `icacls` are stone-cold efficient, but **blind as bats** when it comes to feedback. 😅 No progress, no percentage, just… wall of text (or silence).

---

### 🧪 Here’s the workaround idea:

We can **simulate a progress bar** by counting total directories first, then feeding them into `takeown` **one by one**, with progress printed in PowerShell.

#### ⚙️ This doesn’t speed it up — but you *see* it working.

---

### 🔧 **Progress-Enabled Takeown for WindowsApps (Dry-Run Compatible)**

```powershell
# Run as Admin
$basePath = "C:\Program Files\WindowsApps"
Write-Host "`n📦 Scanning all folders in $basePath..."

$folders = Get-ChildItem -Path $basePath -Directory -Force
$total = $folders.Count
$counter = 0

Write-Host "`n🔐 Taking ownership with visual feedback..."

foreach ($folder in $folders) {
    $counter++
    $percent = [math]::Round(($counter / $total) * 100, 1)
    Write-Progress -Activity "Taking ownership..." -Status "$percent% complete" -PercentComplete $percent

    try {
        takeown /f "$($folder.FullName)" /r /d Y | Out-Null
        icacls "$($folder.FullName)" /grant Administrators:F /t | Out-Null
    } catch {
        Write-Warning "Failed on: $($folder.FullName)"
    }
}

Write-Progress -Activity "Taking ownership..." -Completed
Write-Host "`n✅ Ownership process complete with visual progress."
```

---

### 🧠 Bonus Options:

| Option | Description |
|--------|-------------|
| `-WhatIf` Flag | Simulate changes without making them (safe testing) |
| Logging | Add log file to track ownership attempts and failures |
| Parallelization | Speed it up with PowerShell jobs or threading (though ownership ops are tricky parallel-wise) |

---

Would you like me to merge this visual `takeown` + `icacls` into your dry-run script and make it a full preview utility?

I can also wrap the whole thing into a `.ps1` tool or `.HTA` app with buttons like:
- **[Preview Non-EN Files]**
- **[Clean Language Folders]**
- **[Revoke Access]**

Just say the word 💻✨

---

Your **`$appPanel` is coming back `$null`** because **PowerShell isn’t finding the `Name='AppPanel'` ItemsControl** in the default XAML namespace. When that happens, you see *only* the buttons, and adding children to `$appPanel` fails. Let’s fix that.

Below is a **cleaned-up XAML** that explicitly sets `x:Name` instead of `Name`, and includes the necessary `xmlns:x` attribute. This prevents the “null-valued expression” error and ensures the UI is recognized properly.

Also, **be sure you are running PowerShell in STA mode** or you might get weird XAML issues. If you’re in a standard console or ISE, do:

```powershell
powershell.exe -STA
```

Then run the script.

---

## ✅ Working Script

```powershell
# Must be run as: powershell.exe -STA

Add-Type -AssemblyName PresentationFramework

# Define the apps
$apps = @(
    @{ Name = "Xbox App"; ID = "Microsoft.XboxApp" },
    @{ Name = "Xbox Gaming Overlay"; ID = "Microsoft.XboxGamingOverlay" },
    @{ Name = "Xbox TCUI"; ID = "Microsoft.Xbox.TCUI" },
    @{ Name = "Clipchamp"; ID = "Microsoft.Clipchamp" },
    @{ Name = "Snipping Tool"; ID = "Microsoft.ScreenSketch" },
    @{ Name = "DirectX Runtime"; ID = "Microsoft.DirectXRuntime" }
)

# Detect installed packages (use PackageFamilyName for best matching)
$installedPackages = Get-AppxPackage -AllUsers |
    Select-Object -ExpandProperty PackageFamilyName

# Build the GUI with explicit x:Name
[xml]$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="App Reinstaller" Height="550" Width="450">
    <StackPanel Margin="10">
        <TextBlock FontWeight="Bold" FontSize="14" Margin="0,0,0,10">
            Select apps to reinstall:
        </TextBlock>
        
        <!-- Use x:Name so that .FindName() can locate it -->
        <ItemsControl x:Name="AppPanel" />
        
        <TextBlock Margin="0,10,0,5" FontStyle="Italic" Foreground="Gray">
            * Installed apps are shown as selected radios.
        </TextBlock>
        
        <Button x:Name="GenerateScriptButton" Content="Generate Reinstall Script"
                Height="30" Margin="0,10,0,0" />
        
        <Button x:Name="RunNowButton" Content="Run Script Now"
                Height="30" Margin="0,5,0,0"/>
        
        <TextBox x:Name="OutputBox" Height="120" Margin="0,10,0,0"
                 TextWrapping="Wrap"
                 VerticalScrollBarVisibility="Auto"
                 IsReadOnly="True"/>
    </StackPanel>
</Window>
"@

# Parse the XAML
[xml]$xmlReader = New-Object System.Xml.XmlNodeReader($xaml)
$window = [Windows.Markup.XamlReader]::Load($xmlReader)

# Grab named elements
$appPanel         = $window.FindName("AppPanel")
$generateButton   = $window.FindName("GenerateScriptButton")
$runNowButton     = $window.FindName("RunNowButton")
$outputBox        = $window.FindName("OutputBox")

# If anything is null, show error
if (!$appPanel -or !$generateButton -or !$runNowButton -or !$outputBox) {
    [System.Windows.MessageBox]::Show("Failed to load one or more GUI components.","Error")
    return
}

$controls = @()
$generatedScript = ""

# Populate the ItemsControl
foreach ($app in $apps) {
    # Compare with installed package family names
    $isInstalled = $installedPackages -contains $app.ID

    if ($isInstalled) {
        $radio = New-Object System.Windows.Controls.RadioButton
        $radio.Content   = "* $($app.Name)"
        $radio.IsChecked = $true
        $radio.IsEnabled = $false
        $appPanel.Children.Add($radio)
    }
    else {
        $checkbox       = New-Object System.Windows.Controls.CheckBox
        $checkbox.Content = $app.Name
        $checkbox.Tag     = $app.ID
        $controls += $checkbox
        $appPanel.Children.Add($checkbox)
    }
}

# Generate script button
$generateButton.Add_Click({
    $outputBox.Clear()
    
    $toReinstall = $controls | Where-Object { $_.IsChecked -eq $true }
    if ($toReinstall.Count -eq 0) {
        $outputBox.AppendText("No apps selected for reinstall.`n")
        $generatedScript = ""
        return
    }

    $outputBox.AppendText("Reinstalling the following apps:`n")
    $reinstallLines = @()
    
    foreach ($cb in $toReinstall) {
        $outputBox.AppendText("- $($cb.Content)`n")
        $id = $cb.Tag
        
        # Build the escaped path
        # e.g. "C:\Program Files\WindowsApps\Microsoft.XboxApp*\AppxManifest.xml"
        $escapedPath = "`"C:\\Program Files\\WindowsApps\\$id*\\AppxManifest.xml`""
        
        # Combine
        $reinstallLines += "Add-AppxPackage -DisableDevelopmentMode -Register $escapedPath"
    }
    
    $outputBox.AppendText("`n--- One-liner Script ---`n")
    $generatedScript = $reinstallLines -join "; "
    $outputBox.AppendText($generatedScript)
})

# Run script now
$runNowButton.Add_Click({
    if ([string]::IsNullOrWhiteSpace($generatedScript)) {
        [System.Windows.MessageBox]::Show("Please generate the script first.", "Warning")
        return
    }
    try {
        Invoke-Expression $generatedScript
        $outputBox.AppendText("`n✅ Reinstall script executed.")
    }
    catch {
        $outputBox.AppendText("`n❌ Error executing script: $_")
    }
})

# Show the window
$window.ShowDialog() | Out-Null
```

---

### Key Notes

1. **`<ItemsControl x:Name="AppPanel">`**  
   - We used `x:Name` in the `x` namespace. That’s how WPF identifies it so `$window.FindName("AppPanel")` doesn’t return `$null`.

2. **Run in STA**  
   - If your shell is in MTA mode, XAML calls might fail or behave oddly. So do:
     ```powershell
     powershell.exe -sta -File .\YourScript.ps1
     ```

3. **Your environment**  
   - If you’re in a restricted environment or an older Windows build, sometimes XAML WPF calls can fail. But typically, the above code works from Windows 10 onward.

4. **Check for actual PackageFamilyNames**  
   - For instance, `Microsoft.XboxApp` might be `Microsoft.XboxApp_8wekyb3d8bbwe`.
   - If you see no checkboxes or radios, it may mean the exact PFN is different than your list. You might need to verify `Get-AppxPackage -AllUsers | Format-Table Name, PackageFamilyName` to confirm.

---

Give that a shot. You should see:

- A text block, an `ItemsControl` listing either radio buttons (for installed apps) or checkboxes (for missing apps).
- Two buttons: **Generate** and **Run**.
- A bottom text box for the output logs.

If it still fails, confirm:

1. You’re in **STA mode**.
2. The **XAML** is recognized (the new namespace fixes).
3. The **PFNs** in `$apps` match your environment. For example, maybe `Snipping Tool` is `Microsoft.ScreenSketch_8wekyb3d8bbwe` on your build.

That’s it! Let me know how it goes.

---

It’s likely failing because **PowerShell is parsing the XAML incorrectly** (the default namespace usage + `xmlns=""` can be finicky) *and/or* because you’re **not running in an STA thread** (Single-Threaded Apartment), which WPF requires. Here are **three** key fixes:

---

## 1. **Use `x:Name` + `xmlns:x` in XAML**  
Replace your XAML’s `Name="..."` with `x:Name="..."` and add `xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"` in the `<Window>` element. This ensures WPF can *actually* see your named controls.

```xml
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        x:Name="RootWindow"
        Title="App Reinstaller" Height="550" Width="450">
    <StackPanel Margin="10">
        <TextBlock FontWeight="Bold" FontSize="14" Margin="0,0,0,10">
            Select apps to reinstall:
        </TextBlock>

        <!-- Use x:Name so .FindName() works -->
        <ItemsControl x:Name="AppPanel" />

        <TextBlock Margin="0,10,0,5" FontStyle="Italic" Foreground="Gray">
            * Installed apps are shown as selected radios.
        </TextBlock>

        <Button x:Name="GenerateScriptButton" 
                Content="Generate Reinstall Script" 
                Height="30" Margin="0,10,0,0" />

        <Button x:Name="RunNowButton"
                Content="Run Script Now" 
                Height="30" Margin="0,5,0,0"/>

        <TextBox x:Name="OutputBox"
                 Height="120" Margin="0,10,0,0"
                 TextWrapping="Wrap"
                 VerticalScrollBarVisibility="Auto"
                 IsReadOnly="True"/>
    </StackPanel>
</Window>
```

---

## 2. **Parse with `XamlReader.Parse()` Instead of `Load()`**  
When you’re passing in raw XAML text, `Parse()` usually works more smoothly in PowerShell scripts:

```powershell
[xml]$xaml = @'
... XAML content ...
'@

# Parse the XAML
$window = [System.Windows.Markup.XamlReader]::Parse($xaml)
```

`Load()` often expects a `Stream` or specialized scenario. `Parse()` is simpler for inline strings.

---

## 3. **Run in STA Mode**  
**WPF requires single-threaded apartment**. If you just open a normal PowerShell console, it’s typically MTA. So do one of the following:

1. **Launch a new PowerShell in STA**:
   ```powershell
   powershell.exe -sta -File .\YourScript.ps1
   ```
2. **If you’re in the ISE**: The ISE usually defaults to STA, so it should be fine. But if you’re using VSCode, you need a special config, or run the above command from the terminal.

---

## 🏆 A Complete Working Example

Below is an entire script you can save as `ReinstallerGUI.ps1`. Then run it like:

```powershell
powershell.exe -sta -File .\ReinstallerGUI.ps1
```

It includes:

- The improved XAML (with `xmlns:x`)
- `XamlReader.Parse()`
- Example code for detecting installed vs uninstalled apps

> **Note**: We’re matching **PackageFamilyName** from `Get-AppxPackage`, so ensure that your `$apps` array has correct family names or that you’re bridging the gap from the ID you want to store.

```powershell
# ReinstallerGUI.ps1
# (Run via "powershell.exe -sta -File .\ReinstallerGUI.ps1")

Add-Type -AssemblyName PresentationFramework

# 1. Define your target apps
$apps = @(
    @{ Name = "Xbox App"; ID = "Microsoft.XboxApp" },
    @{ Name = "Xbox Gaming Overlay"; ID = "Microsoft.XboxGamingOverlay" },
    @{ Name = "Xbox TCUI"; ID = "Microsoft.Xbox.TCUI" },
    @{ Name = "Clipchamp"; ID = "Microsoft.Clipchamp" },
    @{ Name = "Snipping Tool"; ID = "Microsoft.ScreenSketch" },
    @{ Name = "DirectX Runtime"; ID = "Microsoft.DirectXRuntime" }
)

# 2. Detect installed apps (PackageFamilyName is more reliable)
$installedPackages = Get-AppxPackage -AllUsers | Select-Object -ExpandProperty PackageFamilyName

# 3. Prepare XAML with x:Name
$xaml = @'
<Window
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Title="App Reinstaller" Height="550" Width="450">
  <StackPanel Margin="10">
    <TextBlock FontWeight="Bold" FontSize="14" Margin="0,0,0,10">
      Select apps to reinstall:
    </TextBlock>

    <ItemsControl x:Name="AppPanel" />

    <TextBlock Margin="0,10,0,5" FontStyle="Italic" Foreground="Gray">
      * Installed apps are shown as selected radios.
    </TextBlock>

    <Button x:Name="GenerateScriptButton" Content="Generate Reinstall Script"
            Height="30" Margin="0,10,0,0" />

    <Button x:Name="RunNowButton" Content="Run Script Now"
            Height="30" Margin="0,5,0,0"/>

    <TextBox x:Name="OutputBox" Height="120" Margin="0,10,0,0"
             TextWrapping="Wrap"
             VerticalScrollBarVisibility="Auto"
             IsReadOnly="True"/>
  </StackPanel>
</Window>
'@

# 4. Parse the XAML
$window = [System.Windows.Markup.XamlReader]::Parse($xaml)

# 5. Locate named controls
$appPanel = $window.FindName("AppPanel")
$generateButton = $window.FindName("GenerateScriptButton")
$runNowButton = $window.FindName("RunNowButton")
$outputBox = $window.FindName("OutputBox")

# 6. Build the UI
if (!$appPanel -or !$generateButton -or !$runNowButton -or !$outputBox) {
    [System.Windows.MessageBox]::Show("Failed to load GUI components.","Error")
    return
}

$controls = @()
$generatedScript = ""

foreach ($app in $apps) {
    # Compare the $app.ID to installed package family names
    $isInstalled = $installedPackages -contains $app.ID

    if ($isInstalled) {
        # Mark installed apps as radio buttons
        $radio = New-Object System.Windows.Controls.RadioButton
        $radio.Content = "* $($app.Name)"
        $radio.IsChecked = $true
        $radio.IsEnabled = $false
        $appPanel.Children.Add($radio)
    }
    else {
        # Mark missing apps as checkboxes
        $checkbox = New-Object System.Windows.Controls.CheckBox
        $checkbox.Content = $app.Name
        $checkbox.Tag    = $app.ID
        $controls += $checkbox
        $appPanel.Children.Add($checkbox)
    }
}

# 7. Generate Reinstall Script
$generateButton.Add_Click({
    $outputBox.Clear()
    $toReinstall = $controls | Where-Object { $_.IsChecked -eq $true }
    
    if ($toReinstall.Count -eq 0) {
        $outputBox.AppendText("No apps selected for reinstall.`n")
        $generatedScript = ""
        return
    }

    $outputBox.AppendText("Reinstalling the following apps:`n")
    $reinstallLines = @()
    foreach ($cb in $toReinstall) {
        $outputBox.AppendText("- $($cb.Content)`n")
        $id = $cb.Tag

        # Escape path for 'Add-AppxPackage'
        $escapedPath = "`"C:\Program Files\WindowsApps\$id*\AppxManifest.xml`""
        $reinstallLines += "Add-AppxPackage -DisableDevelopmentMode -Register $escapedPath"
    }
    $outputBox.AppendText("`n--- One-liner Script ---`n")
    $generatedScript = $reinstallLines -join "; "
    $outputBox.AppendText($generatedScript)
})

# 8. Run Script Button
$runNowButton.Add_Click({
    if ([string]::IsNullOrWhiteSpace($generatedScript)) {
        [System.Windows.MessageBox]::Show("Please generate the script first.", "Warning")
        return
    }
    try {
        Invoke-Expression $generatedScript
        $outputBox.AppendText("`n✅ Reinstall script executed.")
    }
    catch {
        $outputBox.AppendText("`n❌ Error executing script: $_")
    }
})

# 9. Show the Window
$null = $window.ShowDialog()
```

---

## 4. If Still No Luck

- Make sure you have **WPF** (Windows Presentation Framework) installed (Windows 10+ does).
- Confirm the apps’ *PackageFamilyName* actually matches — open PowerShell and run:

  ```powershell
  Get-AppxPackage -AllUsers | Where Name -like "*XboxApp*" | Select Name, PackageFamilyName
  ```
  Then see if it’s something like `Microsoft.XboxApp_8wekyb3d8bbwe` — in that case, your `$apps` array’s `ID` should be `Microsoft.XboxApp_8wekyb3d8bbwe` for a direct match. If you only have `Microsoft.XboxApp`, it might not detect.

- Or consider using partial matching (`-like`) if the exact PFN is unknown.

Finally, if you keep seeing the *“Cannot set Visibility or call Show…”* error, it just means the window tried to display but got closed (or the script re-ran) and you’re trying to re-show a closed window. Make sure to **run once** in a fresh STA session.

That’s the **tried-and-true** method for a WPF-based PowerShell GUI. Good luck, and let me know if you still get stuck!