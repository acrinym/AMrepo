# AHK Auto-Walk and Like

#### You:
Remember we talked about creating an AHK "like" button for Death Stranding? Here's an AHK script that "autowalks" after pressing F11. We could discern the key for "like" and then use the existing script to adapt for "like". What you'll need is the list of keybinds though for death stranding. 

#### ChatGPT:
Perfect. Since you've uploaded the zip file for the AHK autowalk script (`DS_AutoWalk v1.0`), I’ll begin by extracting and reviewing its contents. Then I’ll guide you on how to adapt the script to automate "likes" in *Death Stranding* by:

1. Identifying the "Like" keybind in the game.
2. Adding a hotkey that simulates pressing the "Like" button repeatedly or on-demand.

Let’s start by unpacking the zip and inspecting the script.Perfect. Since you've uploaded the zip file for the AHK autowalk script (`DS_AutoWalk v1.0`), I’ll begin by extracting and reviewing its contents. Then I’ll guide you on how to adapt the script to automate "likes" in *Death Stranding* by:

1. Identifying the "Like" keybind in the game.
2. Adding a hotkey that simulates pressing the "Like" button repeatedly or on-demand.

Let’s start by unpacking the zip and inspecting the script.


#### ChatGPT:
The archive contains a single AHK script file: `DS_AutoWalk.ahk`.

Next, I’ll open and review the contents of that script so we can understand how it works—then we’ll add functionality to simulate the "Like" action.


#### ChatGPT:
Here’s a breakdown of what the script currently does:

### 🔍 Current Function: `Auto-Walk`

- **Toggle key**: `F12`
- **When ON**:
  - Holds down the **W** key (to walk forward).
  - Simulates **left and right mouse button press** (likely to keep balance or grip).

---

### ✅ To Add: "Like" Button Press

To do this, we need:

1. **The keybind for "Like"** in *Death Stranding*.\
   On most PC setups, this is usually bound to **\[F]** by default.

2. Add a **new hotkey** (e.g., `F11`) that:
   - Simulates pressing `F` repeatedly.
   - Optionally: Loops while held down or toggled.

---

### 🔧 Example Enhancement

Here’s what we can append to the script if `F` is the "Like" key:

```ahk
; Press F11 to spam the "Like" key (F key)
F11::ToggleLikeSpam()

ToggleLikeSpam() {
  static isLiking := false
  isLiking := !isLiking

  if (isLiking) {
    SetTimer(() => Send("{f}"), 100) ; Send F every 100 ms
  } else {
    SetTimer(() => Send("{f}"), 0) ; Stop the timer
  }
}
```

---

Would you like me to generate a fully combined script for you with this included, or should we also consider allowing for key rebinding just in case “F” isn’t the correct one on your setup?


#### You:
You need to search for Death Stranding Director's cut keybinds (for pc) 

#### ChatGPT:
iturn0image0Absolutely, Justin! Let's integrate the "Like" functionality into your existing AutoHotkey (AHK) script for *Death Stranding: Director's Cut*.

---

### 🎮 Default "Like" Keybind

In *Death Stranding: Director's Cut* on PC, the default key for "Like/Call Out" is **`5`** on the keyboard. citeturn0search0

---

### 🛠️ Updated AHK Script with "Like" Functionality

Below is the enhanced AHK script that includes both the auto-walk feature and a toggle for sending "likes":

```ahk
#Requires AutoHotkey v2.0

; Death Stranding Auto-Walk and Like Script

; Toggle auto-walk with F12
F12::ToggleAutoWalk()

ToggleAutoWalk() {
    static isWalking := false
    isWalking := !isWalking

    if (isWalking) {
        Send("{w down}")
        Click("down", "L")
        Click("down", "R")
    } else {
        Send("{w up}")
        Click("up", "L")
        Click("up", "R")
    }
}

; Toggle sending likes with F11
F11::ToggleLikeSpam()

ToggleLikeSpam() {
    static isLiking := false
    isLiking := !isLiking

    if (isLiking) {
        SetTimer(() => Send("{5}"), 100) ; Send '5' every 100 ms
    } else {
        SetTimer(() => Send("{5}"), 0) ; Stop sending '5'
    }
}
```

---

### 📝 Notes

- **Auto-Walk Toggle (`F12`)**: Starts or stops continuous walking by holding down the `W` key and both mouse buttons.
- **Like Toggle (`F11`)**: Begins or ends the rapid sending of "likes" by pressing the `5` key every 100 milliseconds.

Feel free to adjust the timing interval in the `SetTimer` function to suit your preference. If you need further customization or assistance, don't hesitate to ask!


#### You:
Issue we had before is the buttons never reach DS for some reason. This seems like it might. 

#### ChatGPT:
iturn0image0Absolutely, Justin. Let's delve deeper into ensuring your AutoHotkey (AHK) script effectively sends the "Like" input to *Death Stranding: Director's Cut*.

---

### 🎮 Default "Like" Keybind

In *Death Stranding: Director's Cut* on PC, the default key for "Like/Call Out" is **`5`** on the keyboard. citeturn0search1

---

### 🛠️ Updated AHK Script with "Like" Functionality

Below is the enhanced AHK script that includes both the auto-walk feature and a toggle for sending "likes":

```ahk
#Requires AutoHotkey v2.0

; Death Stranding Auto-Walk and Like Script

; Toggle auto-walk with F12
F12::ToggleAutoWalk()

ToggleAutoWalk() {
    static isWalking := false
    isWalking := !isWalking

    if (isWalking) {
        Send("{w down}")
        Click("down", "L")
        Click("down", "R")
    } else {
        Send("{w up}")
        Click("up", "L")
        Click("up", "R")
    }
}

; Toggle sending likes with F11
F11::ToggleLikeSpam()

ToggleLikeSpam() {
    static isLiking := false
    isLiking := !isLiking

    if (isLiking) {
        SetTimer(() => Send("{5}"), 100) ; Send '5' every 100 ms
    } else {
        SetTimer(() => Send("{5}"), 0) ; Stop sending '5'
    }
}
```

---

### 📝 Notes

- **Auto-Walk Toggle (`F12`)**: Starts or stops continuous walking by holding down the `W` key and both mouse buttons.
- **Like Toggle (`F11`)**: Begins or ends the rapid sending of "likes" by pressing the `5` key every 100 milliseconds.

Feel free to adjust the timing interval in the `SetTimer` function to suit your preference. If you need further customization or assistance, don't hesitate to ask!


#### You:
Issue we had before is the buttons never reach DS for some reason. This seems like it might. 

#### ChatGPT:
Ah yes, I remember now—and you're right to focus on that critical detail.

AutoHotkey **often fails to send keystrokes or clicks** to certain games like *Death Stranding: Director's Cut* due to **how the game handles input**, especially when:

- It uses **DirectInput** or **Raw Input** (bypassing the Windows input stack).
- It's running in **exclusive fullscreen** or with **elevated privileges (admin)**.
- There's **anti-cheat or input filtering** even in single-player titles (often baked into engine layers).

---

### ✅ Why This Might Work Now

The current script uses:

```ahk
Send("{5}")
```

But that **still uses standard Windows messaging** unless modified.

What might *actually* get through to Death Stranding is switching to **hardware-level input simulation**, such as:

---

### 🔧 Fix: Use `SendEvent` or `SendInput`

Try **modifying the script** like this:

```ahk
SendInput("{5}") ; preferred for game compatibility
```

Or more directly:

```ahk
F11::ToggleLikeSpam()

ToggleLikeSpam() {
    static isLiking := false
    isLiking := !isLiking

    if (isLiking) {
        SetTimer(SendLikeKey, 100)
    } else {
        SetTimer(SendLikeKey, 0)
    }
}

SendLikeKey() {
    SendInput("{5}")
}
```

---

### 💡 Additional Solutions (if it still doesn't register):

1. **Run AHK as Administrator**\
   Death Stranding might be running as admin. Match the privilege level of the AHK script.

2. **Use `ControlSend` with window targeting**\
   This often fails in fullscreen, but can help in borderless window mode.

3. **Inject Raw Input with External Tools**\
   You can use tools like **Interception Driver**, **reWASD**, or **vMulti** for deep hardware-level mapping. Some users map keyboard keys to virtual controllers using these to bypass input blocks.

---

### 🧪 Next Test Step:

Try swapping `Send("{5}")` with `SendInput("{5}")`, and **run the script as Administrator**. That should give us a clearer idea whether the input is reaching the game.

Would you like me to generate a pre-modified version of the script now with `SendInput` already patched in?
