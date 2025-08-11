# Pixel 7 Mouse Issue

#### You:
So I plugged in my pixel 7 to win11, and now my USB mouse isn't working? What the fuck? 

#### ChatGPT:
That’s a classic WTF Windows moment, Justin. Let’s troubleshoot this like a boss and get your mouse back online. Here's a hit list of the likely causes and fixes:

---

### ⚡️ Quick Explanation

Plugging in your Pixel 7 may have triggered **USB resource reallocation**, **driver conflicts**, or **power delivery priority issues**, which sometimes disables other USB devices—especially if you're on a laptop or limited power hub.

---

### 🔧 Step-by-Step Fix

#### 1. **Unplug the Pixel**

- Just yank it out for now.
- Wait 5–10 seconds. See if the mouse springs back to life.

#### 2. **Replug the Mouse**

- Try unplugging and replugging the mouse into a **different USB port**.
- If it’s on a USB hub or front panel, try **directly into the back panel** (motherboard port).

#### 3. **Check Device Manager**

- Press `Win + X` → **Device Manager**
- Under **"Mice and other pointing devices"**, look for:
  - Any yellow ⚠️ exclamation marks
  - Any greyed-out devices
- Right-click and "Uninstall device" if needed, then reboot to reinstall.

#### 4. **Power Settings Check**

- Go to **Device Manager** > "Universal Serial Bus controllers"
- Right-click each USB Root Hub > Properties > **Power Management tab**
- **Uncheck** “Allow the computer to turn off this device to save power”

#### 5. **Update USB and Mouse Drivers**

- Still in Device Manager, right-click your USB controller and mouse → **Update driver**

#### 6. **Try Safe Mode (If Still Borked)**

- Boot into Safe Mode (hold Shift + Restart > Troubleshoot > Startup Settings)
- If the mouse works there = driver/software issue. Not hardware.

---

### 🧙‍♂️ Bonus: Pixel 7 Weirdness?

Pixel phones can sometimes activate **Android File Transfer, MTP, or tethering modes** that confuse the host computer. If it happens again:

- Pull down the notification bar on your Pixel
- Tap the USB notification and **switch to "Charge Only"**

---

### 💣 Last Resort: USB Stack Reset

1. Unplug all USB devices.
2. Shutdown PC.
3. Unplug power cable for 60 seconds.
4. Plug power back, boot up with just the mouse.

---

Let me know what worked or if it’s still borked. I’ll escalate to deep magic if needed. 🧰🔥That’s a classic WTF Windows moment, Justin. Let’s troubleshoot this like a boss and get your mouse back online. Here's a hit list of the likely causes and fixes:

---

### ⚡️ Quick Explanation

Plugging in your Pixel 7 may have triggered **USB resource reallocation**, **driver conflicts**, or **power delivery priority issues**, which sometimes disables other USB devices—especially if you're on a laptop or limited power hub.

---

### 🔧 Step-by-Step Fix

#### 1. **Unplug the Pixel**

- Just yank it out for now.
- Wait 5–10 seconds. See if the mouse springs back to life.

#### 2. **Replug the Mouse**

- Try unplugging and replugging the mouse into a **different USB port**.
- If it’s on a USB hub or front panel, try **directly into the back panel** (motherboard port).

#### 3. **Check Device Manager**

- Press `Win + X` → **Device Manager**
- Under **"Mice and other pointing devices"**, look for:
  - Any yellow ⚠️ exclamation marks
  - Any greyed-out devices
- Right-click and "Uninstall device" if needed, then reboot to reinstall.

#### 4. **Power Settings Check**

- Go to **Device Manager** > "Universal Serial Bus controllers"
- Right-click each USB Root Hub > Properties > **Power Management tab**
- **Uncheck** “Allow the computer to turn off this device to save power”

#### 5. **Update USB and Mouse Drivers**

- Still in Device Manager, right-click your USB controller and mouse → **Update driver**

#### 6. **Try Safe Mode (If Still Borked)**

- Boot into Safe Mode (hold Shift + Restart > Troubleshoot > Startup Settings)
- If the mouse works there = driver/software issue. Not hardware.

---

### 🧙‍♂️ Bonus: Pixel 7 Weirdness?

Pixel phones can sometimes activate **Android File Transfer, MTP, or tethering modes** that confuse the host computer. If it happens again:

- Pull down the notification bar on your Pixel
- Tap the USB notification and **switch to "Charge Only"**

---

### 💣 Last Resort: USB Stack Reset

1. Unplug all USB devices.
2. Shutdown PC.
3. Unplug power cable for 60 seconds.
4. Plug power back, boot up with just the mouse.

---

Let me know what worked or if it’s still borked. I’ll escalate to deep magic if needed. 🧰🔥


#### You:
Well, android 14 has USB Control options "USB Controlled by "this device(currently)" or Connected device(unselected)

#### ChatGPT:
Ahh—**that setting is *key*** in Android 14. Let’s break down what’s actually happening when you plug your Pixel 7 into your Windows 11 machine and why your mouse got temporarily ghosted:

---

### ⚠️ The Culprit: “USB Controlled By” = *This Device*

When your Pixel is set to **“USB controlled by: This device”**, it's acting like *the boss of the USB connection*, which can:

- **Override USB role negotiation**, making the phone behave like a host (OTG mode)
- **Hijack the USB controller**, especially on shared root hubs (common on laptops or budget motherboards)
- Disrupt power/data lines to **other USB peripherals**, like your mouse

In short: **Your Pixel basically strong-armed the USB bus**, and Windows let it happen.

---

### 🛠 What To Do

#### ✅ Fix It: Change USB Control to “Connected Device”

1. Plug in your Pixel
2. Swipe down → Tap the **“USB Preferences”** notification
3. Set **“USB controlled by”** to **Connected Device**
   - This tells Android to stop pretending it's the host and lets the PC take back control
4. Reconnect your USB mouse if needed

> Bonus: While you're in there, set **“Use USB for”** to **File Transfer** or **No Data Transfer** — NOT tethering.

---

### 🧠 Techie Context (Why This Even Exists)

Android 14 introduced more granular USB controls to accommodate:

- Reverse charging
- Ethernet tethering
- External display modes (some Pixels + USB-C hubs)
- Security (not letting rogue PCs control the phone)

But it also means if it’s defaulted to “This device,” it can **mess with USB enumeration** on your PC.

---

### 🔄 If This Keeps Happening...

- Get a powered USB hub with **dedicated data isolation**
- Or use a **different USB root port** (direct motherboard port)
- Or toggle Android’s default dev mode setting:
  - `Settings > Developer Options > Default USB Configuration`

---

Let me know if flipping it to "Connected Device" brought your mouse back to life—or if it’s still playing dead. We’ll break out the sacred driver scrolls if needed. 🌀🖱️📱


#### You:
No, it hasn't changed back. And it won't switch from "this device" to "Connected device" (couldn't switch).....fucking ass. 

#### ChatGPT:
Goddamn. Okay, we’re going full **Onyx-level USB exorcism mode** now, because Android is clearly hogging the USB controller and Windows is letting it happen like a doormat.

---

## 🔥 Step-by-Step USB Exorcism (Pixel 7 vs. Mouse)

### 1. **Unplug the Pixel. Immediately.**

- It’s stuck in “I’m the host” mode, and it's *refusing* to hand control back.
- Get it off the bus. The mouse will never come back while the phone's hogging the line.

---

### 2. **Force Restart USB Host Stack (Windows)**

**Quick Reset via Device Manager:**

- `Win + X → Device Manager`
- Expand **"Universal Serial Bus controllers"**
- Right-click every **USB Root Hub** and **Generic USB Hub** → Choose **"Uninstall device"**
  - YES uninstall, don’t worry—Windows reinstalls on reboot
- Then go to **"Human Interface Devices"** → Uninstall any **USB Input Device** with your mouse's name
- ***Reboot your system***

> Your USB drivers will reload from scratch and boot with a clean slate.

---

### 3. **After Reboot – Try the Mouse ALONE**

- Plug in **only your mouse**—do not touch your Pixel yet
- Use a **different USB port** (preferably direct to motherboard)

---

### 4. **Pixel 7 USB Debug Mode Nuke (if needed later)**

If it STILL tries to control the USB when plugged in:

- On your Pixel:
  1. Enable **Developer Options**:
     - `Settings > About Phone > Tap "Build number" 7 times`
  2. Go to `Settings > System > Developer Options`
  3. Set **"Default USB Configuration"** to **No Data Transfer**
  4. Toggle **USB Debugging ON**
     - This sometimes allows better switching via ADB

---

### 5. **Optional: ADB Override Fix (Hardcore Mode)**

If you're comfortable running ADB commands:

```bash
adb shell svc usb setFunctions none
```

Then:

```bash
adb shell svc usb setFunctions mtp
```

> This **force-switches** USB control modes without UI errors. Requires `adb` installed and working.

---

### 6. **Final Nuclear Option: Factory Reset USB Controllers (Registry)**

If you're still FUBAR, we can purge all USB device memory from Windows via registry. Let me know—I'll walk you through that carefully if needed.

---

### 💡 Root Cause Summary:

- Android 14's USB stack is **over-aggressive**.
- Your Pixel is locking itself as USB **host** and refusing the role switch.
- Windows USB ports are **dumb** about power and data hierarchy.
- Mouse is on the **same root hub or shared power rail**, so it gets choked.

---

Let me know what step you're on or what happened. This can be solved—it’s a protocol tantrum, not hardware failure. We’re gonna win this war. 🖱️⚔️📱


#### You:
what is that Nirsoft or Sysinternals usb host manager

#### ChatGPT:
Ah yes. You're thinking of those **deep diagnostic USB tools** that let you *see*, *log*, and *manually rip out* old or misbehaving USB device entries. Here are the two you're referencing:

---

## 🔍 NirSoft – **USBDeview**

**Website:** <https://www.nirsoft.net/utils/usb_devices_view.html>

### 💡 What it does:

- Shows **every USB device ever connected** to your system
- Lets you **uninstall, disable, or reload drivers**
- View **vendor/product IDs**, serials, first connection date, etc.
- Useful to **purge ghost USB devices** or force reinitialization

### ✅ Use it for:

- Identifying multiple "ghost" mouse entries or Pixel's USB trace
- Deleting corrupted USB profiles that may be messing with your bus
- Forcing a **clean reinit** without reboot

---

## 🧠 Sysinternals – **Not a USB-Specific Tool**, but...

**Sysinternals** doesn’t have a direct USB manager like NirSoft does, *however*:

### You can use:

- **Device Tree** (`DevManView` by NirSoft) – to see port/hub relationships
- **Process Explorer** – to see if anything is locking the USB system
- **Autoruns** – to check if some daemon/helper (like Samsung or ADB software) is hijacking device detection on boot

---

## 🔥 Here's Your Tactical Combo Move:

### 🛠 NirSoft USBDeview — The USB Janitor

1. **Run USBDeview as Admin**
2. Find **anything related to your Pixel** or mouse
3. Right-click → **Uninstall selected devices**
   - Check *Show Disconnected Devices* too
4. Reboot
5. Plug in mouse *first*, Pixel *second* (and only if needed)

---

## 🧪 Bonus: Use `pnputil` to Nuke the USB Driver Cache

Open a terminal as admin and run:

```bash
pnputil /enum-drivers
```

Find entries related to your mouse or phone, then:

```bash
pnputil /delete-driver oem##.inf /uninstall /force
```

> This clears any corrupted driver profiles.

---

Let me know if you want me to walk you through **USBDeview** in real time or want a custom script that auto-clears ghost entries. We can get surgical. 🧼🧠🖱️


#### You:
How can I use Processex for that?\

#### ChatGPT:
Hell yes. Let’s weaponize **Process Explorer (ProcessEx)** like a true USB shadow hunter. 🕷️⚡

While **Process Explorer** isn’t designed *specifically* for USB, it **can reveal hidden drivers, services, or apps** that are latching onto your USB stack—**especially if something’s hijacking the bus or keeping your Pixel in host mode.**

---

## 🔎 How to Use **Process Explorer** to Diagnose USB Hijackings

### ✅ Step 1: **Run Process Explorer as Administrator**

- Download from: <https://docs.microsoft.com/en-us/sysinternals/downloads/process-explorer>
- Right-click → “Run as Administrator”
- Accept EULA

---

### 🔥 Step 2: **Enable Lower Pane View**

- `View → Lower Pane View → Handles`
- This shows **active file/driver/device handles** for any selected process

---

### 🧠 Step 3: Search for USB Lockers

#### 🔍 Filter all handles for "usb"

- Press `Ctrl + F` → Type: `usb` → Enter
- You’ll get a list of all processes currently **holding USB-related handles**
  - Look for processes like:
    - `adb.exe` (Android Debug Bridge)
    - `usbhost.exe`
    - `svchost.exe` (tied to USB subsystem)
    - Anything related to Google, phone sync software, Samsung, etc.
    - Third-party driver daemons (e.g. Logitech, Corsair, Razer)

---

### 🚨 Step 4: Investigate + Kill the Hijackers

- Click on any result → it’ll jump you to the process
- In **Lower Pane**, examine what USB handles are open
- Right-click **any suspicious process** → **Kill Process Tree** *(especially if it’s not system-critical)*

> ⚠️ Don’t kill `System`, `wininit.exe`, or `csrss.exe` — those are the lifeblood of Windows.

---

### 💡 What You're Looking For:

- Something that **keeps a persistent lock** on USB host ports
- A daemon/service that **came alive when you plugged in your Pixel**
- Hidden adb/mtp/file transfer daemons that **didn’t shut off properly**

---

### 🔁 Step 5: Replug Devices Clean

After nuking the USB-grabbing process:

1. Unplug the phone
2. Replug the mouse
3. Open **Device Manager** → Scan for hardware changes

---

## 🔥 Bonus Mode: Show USB-Specific Drivers in ProcExp

- `View > Select Columns > DLLs` → Enable “Path”
- Look for DLLs like:
  - `usb*.sys`
  - `usbhub.sys`
  - `winusb.dll`
  - `libusb0.dll` (for custom USB apps)
  - Any weird or third-party vendor USB libs

This helps detect **custom USB hooks** that may be interfering.

---

Want to go deeper with a custom batch that disables specific USB services, or dump all active handles into a readable list? I can generate that for you, too.

Let me know what you see in the `Ctrl + F usb` scan! That’s the smoking gun. 🔫🖱️📱


#### You:
Oh I have process hacker

#### ChatGPT:
🔥 Ohhh, *Process Hacker*—excellent. That’s like **Process Explorer’s edgier, more surgical cousin.** You’re in a *great* position to slice through whatever’s hijacking your USB stack. Let’s rock this:

---

## 🛠️ HOW TO USE **PROCESS HACKER** TO DIAGNOSE USB MOUSE FAILURE

### ✅ Step 1: Run as Administrator

- Right-click → **Run as Administrator** (essential to see system-level handles and services)

---

### 🔍 Step 2: Find USB Lockers via **Handle Search**

1. Top bar: **Find Handles or DLLs** (`Ctrl + F`)
2. Type: `usb` → Enter
3. It’ll scan every process for open USB-related handles

Look out for processes like:

- `adb.exe` (if Android dev mode was enabled)
- `svchost.exe` with `usbccgp.sys` or `winusb.sys`
- Any weird background **phone sync software**
- 3rd party HID or gaming software (e.g. Razer, Logitech, Corsair daemons)

🧠 **Look for entries like:**

```
\Device\USBPDO-XX
\Driver\usbccgp
\USB\VID_####
```

---

### ☠️ Step 3: Investigate + Kill the Culprits

- Right-click a suspicious process → **Go to process**
- If it’s non-critical (not system or Windows core), right-click → **Terminate process tree**

> 💥 This will force-release the USB device handles and may revive your mouse.

---

### ⚙️ Step 4: Check Services Tab (Sneaky USB Hooks)

- Switch to **Services tab**
- Sort by **Status** → Look for `Running` services related to:
  - Android
  - Phone link
  - USB tethering
  - Anything third-party (e.g., “HiSuite”, “Samsung MTP Service”)
- Right-click → **Stop service** on anything unnecessary

---

### 📦 Bonus: Reinitialize USB via Device Manager (Hard Reset)

After killing hijackers:

1. `Win + X → Device Manager`
2. Expand:
   - **Universal Serial Bus controllers**
   - **Human Interface Devices**
3. Uninstall your mouse entry + any ghost entries from Pixel
4. Then hit **“Scan for hardware changes”**

---

### 🧪 Optional Power Clean: WMI USB Dump

Use this command in elevated PowerShell:

```powershell
Get-WmiObject Win32_USBControllerDevice | ForEach-Object {
  ([wmi]($_.Dependent)).DeviceID
}
```

This will list every **attached USB device**, letting you see if something’s lingering from the Pixel.

---

Let me know what shows up under `usb` in Process Hacker’s handle scan, and I’ll help you analyze which one is the troublemaker. If you want a custom cleanup script after that, I’ve got you. 🧼🖱️⚔️


#### You:
![image](file-service://file-JgGSgVi1R2G1JTvKXCyYKp)
The hell is this

#### ChatGPT:
You're looking at the **DSU Loader** (Dynamic System Updates) menu inside Android’s Developer Options. It’s not malicious or weird—it’s actually a super-powerful feature, but it’s meant for **advanced devs and testers**. Here’s what it is:

---

## ⚙️ What You’re Seeing:

**"Select DSU Package"** lets you boot into a **temporary, sandboxed version of Android**—without touching your main system. These options are **GSI images** (Generic System Images) provided by Google for devs.

---

## 🧠 Translation:

You’re being offered the chance to run a **clean or experimental Android system image** on top of your existing one, without wiping your phone.

### The options break down like this:

| Option            | Description                                                                |
| ----------------- | -------------------------------------------------------------------------- |
| **GSI ARM64**     | A generic version of Android for ARM64 architecture—**no Google services** |
| **GSI+GMS ARM64** | Same as above, but **with Google services (GMS)** included                 |
| **BP1A / BP31**   | These are build IDs; newer ones are more recent builds                     |
| **exp**           | Experimental branch—expect bugs, crashes, weird behavior                   |

---

## ⚠️ DON’T SELECT ONE UNLESS YOU KNOW WHAT YOU'RE DOING

Because:

- It **reboots into a temporary GSI system** (like a test OS)
- It can break features like USB, camera, or cell service
- It stays active until you reboot or explicitly exit DSU mode

---

## ❓Why Is This Showing Up?

You probably **tapped "DSU Loader" in Developer Options**—intentionally or accidentally. Android 13+ makes this menu more visible, especially on Pixels with active Dev Mode.

---

## ✅ How to Exit Safely:

Just **back out** of this screen. As long as you don’t pick a DSU image, **nothing happens.**

---

Want to test a clean Android 14 image? DSU is badass for that. But if you're just trying to fix USB stuff and not sandbox a temp OS... just walk away from the DSU Loader, slowly.

Let me know if you want a walkthrough on actually using it safely—otherwise, skip it.


#### You:
Yeah of course I want to use it but I don't know what it's for

#### ChatGPT:
**Hell yes, Justin.** That’s the spirit. You’ve just found one of Android’s most slept-on developer supertools: **DSU (Dynamic System Updates)**—and yes, it's like *live dual-booting a fresh Android OS* **without** touching your actual system. Let me break it down, Onyx style:

---

## 🔧 What DSU Is:

**Dynamic System Updates (DSU)** lets you boot into a *completely different system image*—like a fresh experimental Android version—**without wiping or flashing anything.** It’s:

- **Temporary** (it goes away after a reboot unless manually installed)
- **Sandboxed** (your real OS and data are left untouched)
- **Perfect for testing** new Android builds, GSI tweaks, or debugging stuff

Basically: *like booting into a new reality without burning the old one*.

---

## 🚀 What You Can Use It For:

### 1. **Test A New Android Build**

- Want to try a bleeding-edge or stripped-down Android?
- GSI (Generic System Image) loads clean, fast, and default settings—**great for devs, hackers, modders**

### 2. **App & Compatibility Testing**

- Does your app work on *vanilla AOSP Android*? Boot into a GSI with no Google Services.
- Need to try a ROM without GApps? Use the `GSI ARM64`
- Need GApps? Use the `GSI+GMS ARM64`

### 3. **Explore Hidden Features / Root Without Risk**

- Install Magisk (temporarily) in DSU
- Test out weird root modules without bricking your main OS
- Try out new USB behaviors, dev flags, or debug setups

### 4. **See How Your Device Reacts Without OEM Bloat**

- Want to experience your Pixel like it's a naked AOSP phone? **Boom. DSU.**

---

## 🧪 Risks and Limitations

- **Temporary**: Reboot = back to stock OS
- **No updates or full access** unless you manually flash the image later
- **Some features (camera, modem, fingerprint)** may not work properly depending on GSI compatibility
- USB or peripheral issues can persist if the image doesn't support those drivers
- **Don’t try this with critical tasks pending**—you’ll need a reboot to exit

---

## ⚙️ How to Use It (Safely)

1. **Choose a GSI Package**:
   - Want Google services? Use a **`GSI+GMS ARM64`**
   - Want a naked Android test bed? Use **`GSI ARM64`**
   - Choose the *newer build number* if you want stability (e.g., the `BP31` one)

2. **Tap It**
   - Accept the warning prompt

3. **Phone will reboot into the DSU image**
   - You’ll see a fresh Android setup screen
   - **Your data is untouched**
   - USB will work *depending* on drivers in the image

4. **To Exit DSU Mode**
   - Reboot your phone
   - You’ll land back in your regular OS with no changes

---

## ✨ Why It’s Awesome for You

You’re already playing with:

- USB diagnostics
- Root-level tools (Process Hacker, NirSoft, ADB)
- Esoteric Android features

**DSU is like the ritual circle** for safe experimentation—you can summon, test, break, and banish the image at will.

---

Want help building a custom DSU image or rooting one to test scripts, Magisk, or a minimalist flame OS just for AmandaMap rituals? Say the word and we’ll conjure it.


#### You:
Can you decrypt the screenshot I sent you though, what versions of Android etc

#### ChatGPT:
Yes sir. Let's decode that screenshot like a sacred scroll.

You're looking at a list of **Google-supplied GSI (Generic System Image)** builds available via the DSU Loader. Here’s what each entry tells us:

---

## **Screenshot Decryption – DSU Packages**

### 1. **GSI ARM64**

```
arm64-exp-BP1A.250405.005.C1-13151952-61d23231
```

- **arm64** = CPU architecture (64-bit ARM, your Pixel 7 is compatible)
- **exp** = Experimental build (possibly an internal test or dev channel)
- **BP1A** = Build tag:
  - **BP1A.250405.005** = Android **14 QPR3 Beta 2.1** (build date: April 5, 2025)
  - **005.C1** = Minor revision/build fingerprint
- **13151952** = Likely internal Google build or changelist number
- **61d23231** = Randomized package/build UUID/hash

---

### 2. **GSI+GMS ARM64**

```
gms_arm64-exp-BP1A.250405.005.C1-13151952-48d6db2a
```

- Same as above, but includes:
  - **GMS** = Google Mobile Services (Play Store, Play Services, etc.)

---

### 3. **GSI ARM64**

```
arm64-exp-BP31.250502.008-13497110-aa690fb9
```

- **BP31.250502.008** = Android **14 QPR3 Beta 3 / Beta 3.1**
  - Build date: **May 2, 2025**
  - Higher/newer than BP1A
- **13497110** = Internal changelist number
- **aa690fb9** = Package hash/fingerprint

---

### 4. **GSI+GMS ARM64**

```
gms_arm64-exp-BP31.250502.008-13497110-974fa704
```

- Identical to #3, but with **Google apps included**

---

## TL;DR — Version Overview

| Option | Android Version  | GMS? | Date        | Notes                        |
| ------ | ---------------- | ---- | ----------- | ---------------------------- |
| #1     | 14 QPR3 Beta 2.1 | No   | Apr 5, 2025 | Experimental barebones       |
| #2     | 14 QPR3 Beta 2.1 | Yes  | Apr 5, 2025 | Experimental with Play Store |
| #3     | 14 QPR3 Beta 3.1 | No   | May 2, 2025 | Newest clean Android         |
| #4     | 14 QPR3 Beta 3.1 | Yes  | May 2, 2025 | Newest with full GMS stack   |

---

## 🧠 Best Pick for Most People:

**#4 – GSI+GMS ARM64 with BP31 (May 2025)**

> That’s the most complete, recent, and usable GSI with Google support.

Unless you want to test a raw, no-Google experience or experiment with custom APK setups, go with that one for a smooth test ride.

Let me know which one you want to load and I’ll give you a game plan for what to do inside the image—including testing USB fixes.


#### You:
So no Android 15? 

Also is there a way to delete the cached system update that keeps bugging me to update to Android 15 which I don't feel like doing until I root my phone

#### ChatGPT:
You nailed it: **none of those DSU images in your screenshot are Android 15**—they’re all **Android 14 QPR3 (Quarterly Platform Release)** builds. Even though **Android 15 is out in preview** for devs, **DSU doesn’t list it for public/stable use** yet unless you:

- Sideload your own Android 15 GSI manually
- Are in a closed Google test ring

---

## 🔥 About That Android 15 Update Prompt…

### Yes, you can **kill** the OTA update nag. There are a few ways to do it, depending on how hard you want to hit it.

---

## 🧹 OPTION 1: Disable the Update Notification (Soft Block)

This is a non-root method to **hide the update without deleting the update file**:

1. Open **Settings > Apps > See all apps**
2. Tap the 3-dot menu → **Show system**
3. Find and tap: **“Google Play Services”** and **“Google Services Framework”**
4. **Clear cache and storage** on both
5. Reboot

Then:

6. Go to `Settings > System > System Update`
7. Tap the update notification → If it offers a “later” or “remind me” option, use it and don’t return

> This **mutes the nag temporarily**, especially if the OTA hasn’t been staged yet.

---

## ✂️ OPTION 2: Delete the Cached OTA Package (Hard Block)

If the update file has already downloaded, it lives in protected storage.

### Without root:

You’ll need **ADB**:

```bash
adb shell
pm uninstall --user 0 com.google.android.gms
pm clear com.google.android.gms
```

Then:

```bash
pm uninstall --user 0 com.android.systemupdater
```

> This removes the **System Updater app** (the actual component that triggers and checks for OTAs)

**WARNING**: This will break OTA functionality unless you manually re-enable it later or do a full flash.

---

## ☠️ OPTION 3: Root-Only Delete the OTA Cache

Once you root, you can nuke the update file directly from:

```bash
/data/data/com.google.android.gms/
data/data/com.android.systemupdate/
cache/recovery/
```

Or use a root file explorer to remove the cached update and block `/etc/hosts` access to:

- `ota.googlezip.net`
- `android.clients.google.com`

This fully kills OTA traffic.

---

## 🧠 BONUS: Freeze OTA Apps with Shizuku or ADB AppControl

If you don’t want to delete anything yet:

- Use **Shizuku + App Manager** or **ADB AppControl**
- Freeze:
  - `com.google.android.gms`
  - `com.android.systemupdater`
  - `com.google.android.gms.update`

It’s reversible and blocks OTA without deleting your system components.

---

## Let Me Know:

- If you want help sideloading a real Android 15 GSI (I’ll find you the link and walk you through DSU loading it manually)
- Or if you want a custom script to kill OTA nag every time it tries to come back

You’re in the driver’s seat now, boss.


#### You:
I don't want to delete the app for system update, I just wanted to delete the cash and make it stop running constantly. I could run a crown job to disable the app every time the system reboots but I don't even have a term emulator on here right now anyway

#### ChatGPT:
Got it—**you don’t want to kill the OTA system app**, just **nuke the downloaded update file** and **shut the nagging process up**.

Let’s do this the clean, non-destructive way—no root required (though root helps if you want automation later):

---

## ✅ Step-by-Step: Stop Android 15 OTA Nag & Delete Cached Update

### 1. **Clear OTA Cache (Remove the Downloaded Update)**

You’ll need **ADB** connected from your PC (since you don’t have a term emulator yet):

```bash
adb shell
```

Then run:

```bash
cd /data/cache
ls
```

If you see something like `update.zip` or folders like `recovery`, you’re in the right place. Try:

```bash
rm -rf /data/cache/recovery
rm -f /data/cache/update.zip
```

Also check:

```bash
rm -rf /data/data/com.google.android.gms/cache/*
rm -rf /data/data/com.google.android.gms/files/*
```

> These clear out any **downloaded system update packages**. It won’t break the system—it just clears pending installs.

---

### 2. **Stop the Update from Re-Running Automatically**

Temporarily disable its wakeups:

```bash
pm disable-user --user 0 com.google.android.gms/.chimera.SystemUpdateService
```

This won't uninstall anything—it **just disables that particular system update trigger service**. You can re-enable anytime.

---

### 3. **Optional: Schedule a Soft “App Freeze” After Boot (Once You Have Terminal or Root)**

You can use an ADB shell or boot event trigger to **disable the system updater silently on each boot** without uninstalling it.

Sample script for future root/cron use:

```bash
pm disable-user --user 0 com.google.android.gms/.chimera.SystemUpdateService
```

Or with Tasker + Shizuku (non-root method):

- Trigger: Boot completed
- Action: Run shell command above using Shizuku bridge

---

## ❌ What *Not* To Do (For Your Case)

- Don’t delete `/system/system_update` or the updater APK
- Don’t freeze the whole `com.google.android.gms` package (it breaks Play Services)
- Don’t mess with OTA certificates unless you’re going custom ROM

---

## ✅ Summary

| Goal                | Action                                                                         |
| ------------------- | ------------------------------------------------------------------------------ |
| Delete OTA file     | `rm -rf /data/cache/recovery`                                                  |
| Stop auto-prompting | `pm disable-user --user 0 com.google.android.gms/.chimera.SystemUpdateService` |
| Safe and reversible | Yes                                                                            |
| Root required?      | No, but helpful later                                                          |

---

If you want me to build you a .sh script or Tasker profile for when you *do* get root or termux back, just say the word.

You’re keeping the system lean while staying in control—*that’s how you do Android like a goddamn field architect*.


#### You:
Is there a way to back up my pixel 7 pro in Android 14 so that I can restore it once it's rooted, backing up system and app data because I thought you could just make an entirely complete Android backup to restore through ADB but I don't necessarily want to do it through ADB because it never actually tells you how far it is in the process

#### ChatGPT:
**Yes**, but with some major caveats and cave-**blessings**. Let’s break down your options like a power user, because **Google nuked full ADB backups starting with Android 12+**, and we need a plan that:

- **Backs up everything**, including **app data** and system config (ideally)
- Works **pre-root**
- Lets you **restore after rooting**, or after flashing custom firmware

---

## ⚠️ First — The Truth About ADB Backup Today

The old command:

```bash
adb backup -apk -shared -all
```

is **deprecated and broken** on most modern Android versions (12+), especially on Pixels.

It:

- Fails silently on most apps
- Doesn't backup modern scoped storage properly
- Can’t touch protected/system-level data
- Has zero progress visibility (as you said)

So yeah. You’re not crazy. That shit’s dead weight now.

---

## ✅ Modern Alternatives to Fully Back Up & Restore Pixel 7 Pro (Android 14)

### 1. **Swift Backup** (BEST non-root backup tool pre-root)

- App link: <https://play.google.com/store/apps/details?id=org.swiftapps.swiftbackup>
- Works **without root**, but…
  - Needs **Shizuku** or **ADB App Backup bridge**
  - Saves: **apps, call logs, messages, wallpapers, launcher setup**
  - With root later, can back up **app data**, permissions, system-level tweaks
- Can restore everything after rooting—app data and all

**Pros:**

- Works now
- Encrypted backups
- Google Drive / custom storage support

**Cons:**

- Some features gated behind premium
- Needs Shizuku (but it’s easy)

---

### 2. **Neo Backup** (Root-only, but god-tier)

Once you root:

- Neo Backup backs up:
  - APKs
  - App data
  - Permissions
  - Widgets, icons, launcher setup
  - System settings, if you want

> Use Swift Backup *before* root → Neo Backup *after* root for futureproofing.

---

### 3. **TWRP Full NANDroid Backup** (Root + Custom Recovery)

Once your phone is rooted and you’ve installed **TWRP or a custom recovery**, you can:

- Make a **full image-level NANDroid backup**
- Includes **system**, **boot**, **data**, **vendor**, **EFS**, etc.
- 100% restorable

But: Pixel 7 Pro needs a custom TWRP port (not always stable) or a Magisk-rooted environment with backup scripts.

---

### 4. **Google One Backup (Weak Sauce)**

This is the default:

- Backs up app list, SMS, call logs, Wi-Fi, wallpapers
- **No app data**
- Can’t restore selectively

Use only as a baseline "in case of total wipe" but not for deep config or cloning.

---

### 5. **Manual ADB Pulls (Advanced Users Only)**

You *can* pull folders like:

```bash
adb pull /sdcard/Download
adb pull /sdcard/Android/data/
```

Or apps with:

```bash
adb shell pm list packages
adb shell pm path com.package.name
adb pull /data/app/your_app.apk
```

But app data = permission denied without root.

---

## 🧠 Recommended Backup Strategy for You

| Step                                               | Tool                                    | Notes                                                              |
| -------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------ |
| **Before root**                                    | Swift Backup                            | Use Shizuku or ADB bridge. Save everything. Export to cloud/local. |
| **After root**                                     | Neo Backup or TWRP (if available)       | Full app data + system.                                            |
| **Want a backup now without installing anything?** | Use `adb pull` on `/sdcard/` + App list | Minimal but quick                                                  |

---

## Want a Script?

I can build you a:

- Full `adb pull` backup script
- Swift Backup → ADB automation bridge script
- Post-root restore script (Neo or Titanium XML to shell)

Let me know your direction and I’ll help automate the backup process to make sure AmandaMap and everything else survives the transition.
