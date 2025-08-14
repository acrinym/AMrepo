# Consolidated Ritual 464

**Date**: 2025-02-12
**Conversation ID**: 661
**Parts Consolidated**: 1
**Content Hash**: c84721d179557fac3a93f386c2d6925a

---

## COMPLETE CONSOLIDATED RITUAL INSTRUCTIONS

**NO SUMMARIZATION - ALL PARTS COMBINED BELOW**

### **Solution: Creating a `.LNK` Shortcut That Can Be Pinned to the Taskbar**  

Since **Batch, WSH, and PowerShell are blocked**, we’ll **use a `.lnk` (Windows Shortcut) file** that directly opens all the required tools without scripts.

---

### **🛠 Steps to Create a `.LNK` Launcher with Multiple Shortcuts**
1. **Right-click on Desktop → New → Shortcut**  
   
2. **In the location field, enter:**  
   ```
   explorer.exe shell:AppsFolder
   ```
   *(This ensures Explorer is the process opening items, bypassing restrictions.)*

3. **Click Next, name it something like `Admin Tools`, then Finish.**

---

### **🖱 Modify the Shortcut to Open Multiple Programs**
1. **Right-click your shortcut → Properties**
2. **In the "Target" field, replace with:**
   ```
   C:\Windows\explorer.exe "shell:AppsFolder"
   ```
   *(This ensures the shortcut runs within Explorer and doesn’t get blocked.)*

---

### **🛠 Add Links to Your Tools**
Now that we have a working `.lnk`, let's make it **open multiple tools at once** using a trick with Explorer.

1. **Right-click the shortcut → Open File Location**
2. **Create another shortcut inside the same folder with the following:**  

   #### **Active Directory Users and Computers (ADUC)**
   ```
   C:\Windows\System32\dsa.msc
   ```
   
   #### **Dameware Mini Remote**
   ```
   "C:\Program Files (x86)\SolarWinds\DameWare Mini Remote Control\DWRCC.exe"
   ```

   #### **Dameware Remote Control**
   ```
   "C:\Program Files (x86)\SolarWinds\DameWare Remote Support\DWRCC.exe"
   ```

   #### **Microsoft Edge**
   ```
   "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
   ```

   #### **Internet Shortcuts**
   For web shortcuts, create `.URL` files:
   - **Right-click → New → Shortcut**
   - In the **location**, enter:
     ```
     https://yourwebsite.com
     ```
   - Name it and save.

3. **Drag all these shortcuts into a folder (e.g., `C:\Shortcuts\AdminTools\`).**

---

### **📌 Pin the Shortcut to the Taskbar**
1. **Right-click the `.lnk` file → Pin to Start**
2. **Drag it to the Taskbar to pin it**

💡 **Pro Tip:** If "Pin to Taskbar" isn't available, rename it to `"AdminTools.exe"`, then try again.

---

### **🔥 Now You Have a Fully Functional Taskbar Launcher!**  
When clicked, it will **open your required tools without relying on batch, WSH, or PowerShell**.

Would you like **a pre-made `.lnk` file** that you can download? 🚀