# Connect MyBook Live Router

#### You:
How do I conect to my WD Mybooklive when it is connected to the router's switch? 

I couldn;t connect directly with an ethernet to the drive, so I want to map it now. Issue is it won't connect to it without a username/password (which are not assigned to "public" fileshare. 

#### ChatGPT:
To connect to your WD MyBook Live when it's connected to your router's switch, follow these steps:

### Step 1: Ensure MyBook Live is Connected and Powered On

1. **Check Connections**: Make sure the MyBook Live is properly connected to your router’s switch using an Ethernet cable and that it is powered on.
2. **Check Lights**: Verify the LED indicators on both the MyBook Live and the router's switch are showing proper connection (typically solid green or blue for active connection).

### Step 2: Find the IP Address of MyBook Live

1. **Router's Web Interface**: Log into your router's web interface. This is usually accessible via a web browser by entering the router's IP address (commonly `192.168.1.1` or `192.168.0.1`).
2. **DHCP Client List**: Navigate to the section that shows connected devices or DHCP client list. Find the IP address assigned to the MyBook Live.

### Step 3: Access MyBook Live's Web Interface

1. **Open Browser**: Open a web browser and enter the IP address of the MyBook Live.
2. **Login**: Log in to the MyBook Live dashboard if prompted. If you haven’t set a custom username/password, the default username might be `admin` with no password, or refer to the device manual for default login details.

### Step 4: Map Network Drive on Your Computer

#### On Windows:

1. **Open File Explorer**: Open `File Explorer`.
2. **Map Network Drive**: Click on `This PC` or `Computer` in the left-hand sidebar, then click on the `Map network drive` button in the ribbon at the top.
3. **Enter Folder Path**: In the `Folder` field, enter the network path to your MyBook Live share. This is usually in the format `\$MyBookLive_IP_Address]$ShareName]`, e.g., `\\192.168.1.100\Public`.
4. **Connect Using Different Credentials**: If it prompts for a username and password, select the option to `Connect using different credentials` and use `admin` as the username and leave the password blank (if no password is set).

#### On macOS:

1. **Open Finder**: Open `Finder`.
2. **Go to Server**: From the `Go` menu, select `Connect to Server`.
3. **Enter Server Address**: Enter the server address in the format `smb://[MyBookLive_IP_Address]/[ShareName]`, e.g., `smb://192.168.1.100/Public`.
4. **Connect**: Click `Connect` and if prompted, enter `admin` as the username and leave the password blank (if no password is set).

### Step 5: Troubleshooting

- **Firewall/Security Software**: Ensure that any firewall or security software on your computer isn’t blocking the connection.
- **Reset MyBook Live**: If you are unable to log in due to forgotten credentials, consider resetting the MyBook Live to factory settings. Refer to the device’s manual for reset instructions.
- **Firmware Update**: Ensure that your MyBook Live firmware is up-to-date.

By following these steps, you should be able to connect and map your WD MyBook Live to your computer even when it’s connected to your router's switch.To connect to your WD MyBook Live when it's connected to your router's switch, follow these steps:

### Step 1: Ensure MyBook Live is Connected and Powered On

1. **Check Connections**: Make sure the MyBook Live is properly connected to your router’s switch using an Ethernet cable and that it is powered on.
2. **Check Lights**: Verify the LED indicators on both the MyBook Live and the router's switch are showing proper connection (typically solid green or blue for active connection).

### Step 2: Find the IP Address of MyBook Live

1. **Router's Web Interface**: Log into your router's web interface. This is usually accessible via a web browser by entering the router's IP address (commonly `192.168.1.1` or `192.168.0.1`).
2. **DHCP Client List**: Navigate to the section that shows connected devices or DHCP client list. Find the IP address assigned to the MyBook Live.

### Step 3: Access MyBook Live's Web Interface

1. **Open Browser**: Open a web browser and enter the IP address of the MyBook Live.
2. **Login**: Log in to the MyBook Live dashboard if prompted. If you haven’t set a custom username/password, the default username might be `admin` with no password, or refer to the device manual for default login details.

### Step 4: Map Network Drive on Your Computer

#### On Windows:

1. **Open File Explorer**: Open `File Explorer`.
2. **Map Network Drive**: Click on `This PC` or `Computer` in the left-hand sidebar, then click on the `Map network drive` button in the ribbon at the top.
3. **Enter Folder Path**: In the `Folder` field, enter the network path to your MyBook Live share. This is usually in the format `\$MyBookLive_IP_Address]$ShareName]`, e.g., `\\192.168.1.100\Public`.
4. **Connect Using Different Credentials**: If it prompts for a username and password, select the option to `Connect using different credentials` and use `admin` as the username and leave the password blank (if no password is set).

#### On macOS:

1. **Open Finder**: Open `Finder`.
2. **Go to Server**: From the `Go` menu, select `Connect to Server`.
3. **Enter Server Address**: Enter the server address in the format `smb://[MyBookLive_IP_Address]/[ShareName]`, e.g., `smb://192.168.1.100/Public`.
4. **Connect**: Click `Connect` and if prompted, enter `admin` as the username and leave the password blank (if no password is set).

### Step 5: Troubleshooting

- **Firewall/Security Software**: Ensure that any firewall or security software on your computer isn’t blocking the connection.
- **Reset MyBook Live**: If you are unable to log in due to forgotten credentials, consider resetting the MyBook Live to factory settings. Refer to the device’s manual for reset instructions.
- **Firmware Update**: Ensure that your MyBook Live firmware is up-to-date.

By following these steps, you should be able to connect and map your WD MyBook Live to your computer even when it’s connected to your router's switch.


#### You:
What is the default IP of the mybooklive? 

#### ChatGPT:
The default IP address of a WD MyBook Live is typically assigned dynamically by your router using DHCP. This means that there isn't a specific default IP address; instead, the router will assign an IP address to the MyBook Live when it connects to the network.

However, you can find the IP address assigned to your MyBook Live by following these steps:

### Using the Router's Web Interface

1. **Log into the Router**: Access your router’s web interface by entering its IP address into a web browser. Common default IP addresses for routers are `192.168.1.1` or `192.168.0.1`.
2. **Find Connected Devices**: Look for a section that lists connected devices or DHCP clients. This is often under headings like "Attached Devices", "DHCP Client List", "Network Map", or "Connected Devices".
3. **Identify MyBook Live**: Find the MyBook Live in the list. It might be listed by its hostname (e.g., `MYBOOKLIVE`), MAC address, or you might recognize it by the IP address it has been assigned.

### Using WD Software

1. **WD Discovery Tool**: Download and install the WD Discovery software from the WD website. This tool can automatically detect WD devices on your network and display their IP addresses.
2. **Run the Tool**: Open the WD Discovery tool and it should show your MyBook Live along with its IP address.

### Using Command Prompt (Windows) or Terminal (macOS/Linux)

If you have a general idea of the IP address range your router uses (e.g., `192.168.1.x` or `192.168.0.x`), you can use the following methods to find devices on your network:

#### On Windows:

1. **Open Command Prompt**: Press `Win + R`, type `cmd`, and press Enter.
2. **Run ARP Command**: Type `arp -a` and press Enter. This will show a list of IP addresses and their associated MAC addresses.
3. **Identify MyBook Live**: Look through the list for the MAC address that matches your MyBook Live. The MAC address is usually found on a label on the device.

#### On macOS/Linux:

1. **Open Terminal**: Go to Applications > Utilities > Terminal.
2. **Run ARP Command**: Type `arp -a` and press Enter. This will show a list of IP addresses and their associated MAC addresses.
3. **Identify MyBook Live**: Look through the list for the MAC address that matches your MyBook Live.

By identifying the IP address through one of these methods, you should be able to connect to and map your WD MyBook Live on your network.


#### You:
Can I do a 4-second reset on the drive? 

#### ChatGPT:
Yes, you can perform a 4-second reset on the WD MyBook Live. This type of reset is useful for restoring the default network settings without affecting your data. Here’s how you can do it:

### Steps to Perform a 4-Second Reset

1. **Locate the Reset Button**: The reset button is usually a small hole located on the back of the MyBook Live device. You will need a paperclip or a similar pointed object to press it.
2. **Press and Hold**: Insert the paperclip into the reset hole and press the button inside. Hold it for 4 seconds and then release it.
3. **Wait for Reboot**: After you release the button, the device will reboot. This process may take a few minutes.

### What the 4-Second Reset Does

- **Network Configuration**: Resets the network configuration to DHCP. This means the MyBook Live will attempt to obtain an IP address from your router automatically.
- **Admin Password**: Resets the admin password to the default (no password).

### What the 4-Second Reset Does Not Do

- **Data**: It does not affect the data stored on the drive.
- **Shares**: It does not change the shared folders or their contents.
- **User Accounts**: It does not delete user accounts but resets the admin account password.

### After the Reset

1. **Access the Dashboard**: Use a web browser to access the MyBook Live dashboard by entering the IP address assigned by your router. If you don’t know the new IP address, you can find it using the methods described earlier (router’s web interface, WD Discovery tool, or network scan).
2. **Login**: Log in using the default credentials (admin with no password, unless you had set a custom username/password before).
3. **Reconfigure Settings**: You may need to reconfigure some network settings if you had custom configurations before the reset.

Performing a 4-second reset is a safe way to regain access to your MyBook Live if you are having trouble connecting to it due to network configuration issues or forgotten admin passwords.Yes, you can perform a 4-second reset on the WD MyBook Live. This type of reset is useful for restoring the default network settings without affecting your data. Here’s how you can do it:

### Steps to Perform a 4-Second Reset

1. **Locate the Reset Button**: The reset button is usually a small hole located on the back of the MyBook Live device. You will need a paperclip or a similar pointed object to press it.
2. **Press and Hold**: Insert the paperclip into the reset hole and press the button inside. Hold it for 4 seconds and then release it.
3. **Wait for Reboot**: After you release the button, the device will reboot. This process may take a few minutes.

### What the 4-Second Reset Does

- **Network Configuration**: Resets the network configuration to DHCP. This means the MyBook Live will attempt to obtain an IP address from your router automatically.
- **Admin Password**: Resets the admin password to the default (no password).

### What the 4-Second Reset Does Not Do

- **Data**: It does not affect the data stored on the drive.
- **Shares**: It does not change the shared folders or their contents.
- **User Accounts**: It does not delete user accounts but resets the admin account password.

### After the Reset

1. **Access the Dashboard**: Use a web browser to access the MyBook Live dashboard by entering the IP address assigned by your router. If you don’t know the new IP address, you can find it using the methods described earlier (router’s web interface, WD Discovery tool, or network scan).
2. **Login**: Log in using the default credentials (admin with no password, unless you had set a custom username/password before).
3. **Reconfigure Settings**: You may need to reconfigure some network settings if you had custom configurations before the reset.

Performing a 4-second reset is a safe way to regain access to your MyBook Live if you are having trouble connecting to it due to network configuration issues or forgotten admin passwords.
