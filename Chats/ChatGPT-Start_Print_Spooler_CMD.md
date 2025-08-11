# Start Print Spooler CMD

#### You:
I need the CMD to start spooler for win10 and all it's dependencies. 

#### ChatGPT:
To start the print spooler service and all its dependencies in Windows 10 using the Command Prompt (CMD), you can use the following commands:

1. Open Command Prompt as an administrator. To do this, search for `cmd` in the Start menu, right-click on `Command Prompt`, and select `Run as administrator`.

2. Run the following commands to start the print spooler and its dependencies:

```cmd
net start RpcSs
net start DcomLaunch
net start PlugPlay
net start Spooler
```

Here's a brief explanation of each service:

- `RpcSs` (Remote Procedure Call): This is a crucial service for Windows that other services depend on.
- `DcomLaunch` (DCOM Server Process Launcher): This service launches COM and DCOM servers in response to object activation requests.
- `PlugPlay` (Plug and Play): This service manages device installations and configurations.
- `Spooler` (Print Spooler): This service manages print jobs and the printer itself.

By starting these services in the given order, you ensure that all necessary dependencies for the Print Spooler are running.

If you encounter any issues, please let me know!To start the print spooler service and all its dependencies in Windows 10 using the Command Prompt (CMD), you can use the following commands:

1. Open Command Prompt as an administrator. To do this, search for `cmd` in the Start menu, right-click on `Command Prompt`, and select `Run as administrator`.

2. Run the following commands to start the print spooler and its dependencies:

```cmd
net start RpcSs
net start DcomLaunch
net start PlugPlay
net start Spooler
```

Here's a brief explanation of each service:

- `RpcSs` (Remote Procedure Call): This is a crucial service for Windows that other services depend on.
- `DcomLaunch` (DCOM Server Process Launcher): This service launches COM and DCOM servers in response to object activation requests.
- `PlugPlay` (Plug and Play): This service manages device installations and configurations.
- `Spooler` (Print Spooler): This service manages print jobs and the printer itself.

By starting these services in the given order, you ensure that all necessary dependencies for the Print Spooler are running.

If you encounter any issues, please let me know!


#### You:
Help? 

net start Spooler
System error 1058 has occurred.

The service cannot be started, either because it is disabled or because it has no enabled devices associated with it.

#### ChatGPT:
To resolve the issue where the Print Spooler service cannot be started due to it being disabled, follow these steps:

1. **Open Command Prompt as Administrator:**
   - Search for `cmd` in the Start menu.
   - Right-click on `Command Prompt` and select `Run as administrator`.

2. **Enable and Start the Print Spooler Service:**
   Run the following commands to enable the Print Spooler service and start it:

```cmd
sc config Spooler start= auto
net start Spooler
```

These commands will set the Print Spooler service to start automatically and then start the service.

3. **Verify Dependencies:**
   Ensure that all dependencies for the Print Spooler service are enabled. Run the following commands:

```cmd
sc config RpcSs start= auto
sc config DcomLaunch start= auto
sc config PlugPlay start= auto
net start RpcSs
net start DcomLaunch
net start PlugPlay
net start Spooler
```

These commands will ensure that the necessary services for the Print Spooler are also set to start automatically and are running.

4. **Check the Services Configuration:**
   If the above steps do not work, you can manually check and configure the services through the Services management console:

   - Press `Win + R` to open the Run dialog box.
   - Type `services.msc` and press `Enter`.
   - In the Services window, locate the following services:
     - `Print Spooler`
     - `Remote Procedure Call (RPC)`
     - `DCOM Server Process Launcher`
     - `Plug and Play`
   - For each of these services, right-click and select `Properties`.
   - Ensure that the Startup type is set to `Automatic`.
   - Click `Apply` and `OK`.
   - If any of these services are not running, click the `Start` button.

After completing these steps, the Print Spooler service should be enabled and running. If you encounter any further issues, please let me know!


#### You:
Can you rewrite this? 

User's locked out of his ipad, forgot the passcode or the passcode no longer works. 

I unlocked it for him and he had not gotten the "reset your unlock code " screen, so I had him open settings. and it showed up. 

He was able to reset his unlock code successfully and regain access to his ipad. 

Resolved. 

#### ChatGPT:
Certainly! Here's the rewritten version:

---

**Issue:**

User was locked out of his iPad due to forgetting the passcode or the passcode no longer working.

**Resolution:**

I unlocked the iPad for the user. He had not yet received the "reset your unlock code" prompt, so I instructed him to open the Settings app. The prompt then appeared, and he was able to successfully reset his unlock code and regain access to his iPad.

**Status: Resolved.**

---

Let me know if you need any further adjustments!Certainly! Here's the rewritten version:

---

**Issue:**

User was locked out of his iPad due to forgetting the passcode or the passcode no longer working.

**Resolution:**

I unlocked the iPad for the user. He had not yet received the "reset your unlock code" prompt, so I instructed him to open the Settings app. The prompt then appeared, and he was able to successfully reset his unlock code and regain access to his iPad.

**Status: Resolved.**

---

Let me know if you need any further adjustments!
