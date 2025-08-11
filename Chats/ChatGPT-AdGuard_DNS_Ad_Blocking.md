# AdGuard DNS Ad Blocking

#### You:
How do you change your dns with qbittorrent

#### ChatGPT:
Hey there! So you wanna change your DNS settings with qBittorrent? I gotcha covered! Here’s the lowdown:

1. **Change System DNS Settings**:
   First, you'll wanna change the DNS settings on your computer. This way, all your internet traffic, including qBittorrent, will go through the new DNS.

   - **Windows**:
     1. Open `Control Panel`.
     2. Go to `Network and Sharing Center`.
     3. Click on your connection (Wi-Fi or Ethernet).
     4. Click `Properties`.
     5. Select `Internet Protocol Version 4 (TCP/IPv4)` and click `Properties`.
     6. Choose `Use the following DNS server addresses` and enter your preferred DNS servers (e.g., Google DNS: 8.8.8.8 and 8.8.4.4).
     7. Click `OK` to save.

   - **Mac**:
     1. Open `System Preferences`.
     2. Click `Network`.
     3. Select your network connection and click `Advanced`.
     4. Go to the `DNS` tab.
     5. Click the `+` button and add your preferred DNS servers (e.g., 8.8.8.8, 8.8.4.4).
     6. Click `OK`, then `Apply`.

2. **Configure DNS in qBittorrent** (Optional):
   While qBittorrent itself doesn't have a built-in DNS setting, you can make sure it’s using your system’s DNS by ensuring it’s not overridden by VPN settings or other network configurations.

   - If you use a VPN, make sure your VPN client is set to use your desired DNS servers. Most VPNs have an option to specify DNS servers in their settings.
   - Ensure your router’s DNS settings are aligned if you’re setting DNS at the router level. This ensures all devices connected to your network use the same DNS.

3. **Check DNS Configuration**:
   After changing your DNS settings, it’s a good idea to confirm they’re working properly:
   - Open Command Prompt (Windows) or Terminal (Mac).
   - Type `nslookup google.com` and hit Enter.
   - The DNS server addresses in the response should match the ones you configured.

And there ya go! Your qBittorrent should now be using your new DNS settings. Happy torrenting, and keep it safe! If you need more help, just holler!Hey there! So you wanna change your DNS settings with qBittorrent? I gotcha covered! Here’s the lowdown:

1. **Change System DNS Settings**:
   First, you'll wanna change the DNS settings on your computer. This way, all your internet traffic, including qBittorrent, will go through the new DNS.

   - **Windows**:
     1. Open `Control Panel`.
     2. Go to `Network and Sharing Center`.
     3. Click on your connection (Wi-Fi or Ethernet).
     4. Click `Properties`.
     5. Select `Internet Protocol Version 4 (TCP/IPv4)` and click `Properties`.
     6. Choose `Use the following DNS server addresses` and enter your preferred DNS servers (e.g., Google DNS: 8.8.8.8 and 8.8.4.4).
     7. Click `OK` to save.

   - **Mac**:
     1. Open `System Preferences`.
     2. Click `Network`.
     3. Select your network connection and click `Advanced`.
     4. Go to the `DNS` tab.
     5. Click the `+` button and add your preferred DNS servers (e.g., 8.8.8.8, 8.8.4.4).
     6. Click `OK`, then `Apply`.

2. **Configure DNS in qBittorrent** (Optional):
   While qBittorrent itself doesn't have a built-in DNS setting, you can make sure it’s using your system’s DNS by ensuring it’s not overridden by VPN settings or other network configurations.

   - If you use a VPN, make sure your VPN client is set to use your desired DNS servers. Most VPNs have an option to specify DNS servers in their settings.
   - Ensure your router’s DNS settings are aligned if you’re setting DNS at the router level. This ensures all devices connected to your network use the same DNS.

3. **Check DNS Configuration**:
   After changing your DNS settings, it’s a good idea to confirm they’re working properly:
   - Open Command Prompt (Windows) or Terminal (Mac).
   - Type `nslookup google.com` and hit Enter.
   - The DNS server addresses in the response should match the ones you configured.

And there ya go! Your qBittorrent should now be using your new DNS settings. Happy torrenting, and keep it safe! If you need more help, just holler!


#### You:
If I change my DNS to adguard, will I lose ads? 

#### ChatGPT:
Oh, absolutely! Switching your DNS to AdGuard can help you cut down on those pesky ads. Here’s the scoop:

### What is AdGuard DNS?

AdGuard DNS is a privacy-focused DNS service that blocks ads, trackers, and malicious websites at the DNS level. When you use AdGuard DNS, it filters out unwanted content before it even reaches your device.

### How to Set Up AdGuard DNS:

1. **Change System DNS Settings**:
   - **Windows**:
     1. Open `Control Panel`.
     2. Go to `Network and Sharing Center`.
     3. Click on your connection (Wi-Fi or Ethernet).
     4. Click `Properties`.
     5. Select `Internet Protocol Version 4 (TCP/IPv4)` and click `Properties`.
     6. Choose `Use the following DNS server addresses` and enter AdGuard DNS addresses:
        - For regular DNS: `94.140.14.14` and `94.140.15.15`
        - For Family Protection (blocks adult content): `94.140.14.15` and `94.140.15.16`
     7. Click `OK` to save.

   - **Mac**:
     1. Open `System Preferences`.
     2. Click `Network`.
     3. Select your network connection and click `Advanced`.
     4. Go to the `DNS` tab.
     5. Click the `+` button and add AdGuard DNS addresses.
     6. Click `OK`, then `Apply`.

2. **Check DNS Configuration**:
   - Open Command Prompt (Windows) or Terminal (Mac).
   - Type `nslookup google.com` and hit Enter.
   - The DNS server addresses in the response should match the AdGuard DNS servers.

### Benefits of Using AdGuard DNS:

1. **Ad Blocking**:
   AdGuard DNS blocks ads across your entire network, including in apps, games, and browsers.

2. **Privacy Protection**:
   It blocks trackers, protecting your privacy online.

3. **Malware and Phishing Protection**:
   AdGuard DNS prevents access to malicious websites, adding an extra layer of security.

### Will You Lose All Ads?

While AdGuard DNS will significantly reduce the number of ads you see, some ads might still slip through, especially those that are embedded within apps or use advanced techniques. But overall, your browsing experience should be much cleaner and faster.

So, there ya have it! Switching to AdGuard DNS should give you a smoother, ad-free experience. Give it a whirl and enjoy the peaceful, ad-free internet! If you need more tips, you know where to find me.


#### You:
Can I change my router's dns? 

#### ChatGPT:
Oh, you betcha! Changing your router’s DNS settings is a great way to ensure all devices on your network benefit from the new DNS without having to change settings on each device individually. Here’s how you can do it:

### Steps to Change DNS on Your Router:

1. **Access Router Settings**:
   - Open a web browser and type your router’s IP address in the address bar. Common IP addresses are `192.168.1.1` or `192.168.0.1`. Check your router’s manual if these don’t work.
   - Enter your username and password. If you haven’t changed them, the default credentials are usually `admin`/`admin` or `admin`/`password`.

2. **Find DNS Settings**:
   - The exact location of the DNS settings can vary depending on your router’s brand and firmware. Generally, you’ll find it under sections like `Network`, `Internet`, or `WAN` settings.
   - Look for fields labeled `Primary DNS` and `Secondary DNS`.

3. **Enter New DNS Addresses**:
   - Replace the existing DNS addresses with the ones you want to use. For AdGuard DNS, enter:
     - Primary DNS: `94.140.14.14`
     - Secondary DNS: `94.140.15.15`
   - For AdGuard Family Protection:
     - Primary DNS: `94.140.14.15`
     - Secondary DNS: `94.140.15.16`

4. **Save Settings**:
   - Save or apply the changes. Your router may need to reboot for the new settings to take effect.

5. **Confirm DNS Change**:
   - After your router restarts, you can confirm the DNS change by visiting a site like `dnsleaktest.com` or using the `nslookup` command in Command Prompt or Terminal.

### Common Router Brands – Quick Guide:

- **Netgear**:
  - Go to `Basic` > `Internet`.
  - Set `DNS Address` to `Use These DNS Servers`.
  - Enter the DNS addresses.

- **TP-Link**:
  - Go to `Advanced` > `Network` > `Internet`.
  - Set `Primary DNS` and `Secondary DNS`.

- **Linksys**:
  - Go to `Setup` > `Basic Setup`.
  - Scroll down to `Static DNS` fields and enter the DNS addresses.

- **Asus**:
  - Go to `WAN` > `Internet Connection`.
  - Enter DNS Server fields.

### Benefits:

- **Network-Wide Ad Blocking**: AdGuard DNS will block ads for all devices connected to your network.
- **Simplified Management**: No need to configure each device individually.
- **Enhanced Privacy and Security**: All devices benefit from the same level of protection.

There ya go! Now your entire network is cruising with your new DNS settings. Enjoy the cleaner, faster internet! If you need more help or got any other questions, hit me up!


#### You:
Can I setup obfuscation in qbitorrent

#### ChatGPT:
Sure thing, setting up obfuscation in qBittorrent is a smart move to keep your torrenting activities on the down-low. While qBittorrent doesn’t have built-in support for obfuscation like some other clients, you can still achieve it through a couple of methods: enabling encryption and using a VPN. Let’s break it down:

### 1. Enable Encryption in qBittorrent:

1. **Open qBittorrent**.
2. Go to `Tools` > `Options`.
3. Click on the `BitTorrent` section.
4. Look for the `Privacy` section.
5. Under `Encryption mode`, select `Require encryption`. This ensures that your connections are encrypted, though it might reduce the number of peers you can connect to.

### 2. Use a VPN for Obfuscation:

A VPN is the most effective way to obfuscate your torrent traffic. It encrypts your entire internet connection, making it difficult for anyone to see what you’re doing online. Here’s how to set it up:

1. **Choose a VPN Provider**:
   - Pick a reputable VPN provider that supports P2P file sharing (like NordVPN, ExpressVPN, or CyberGhost).

2. **Install the VPN Client**:
   - Download and install the VPN client from your provider’s website.

3. **Configure VPN Settings**:
   - Open the VPN client.
   - Connect to a server that supports P2P. Some VPNs have dedicated P2P servers.
   - Ensure that the VPN’s kill switch is enabled. This feature prevents your real IP from being exposed if the VPN connection drops.

4. **Start qBittorrent**:
   - Once your VPN is connected, open qBittorrent and start torrenting as usual. Your traffic will be encrypted and obfuscated by the VPN.

### 3. Use a Proxy (Optional):

If you prefer not to use a VPN, you can use a SOCKS5 proxy for additional privacy.

1. **Choose a Proxy Service**:
   - Some VPN providers also offer SOCKS5 proxy (like NordVPN and Private Internet Access).

2. **Configure qBittorrent**:
   - Go to `Tools` > `Options`.
   - Click on the `Connection` section.
   - Under `Proxy Server`, choose `SOCKS5`.
   - Enter the proxy server address and port (provided by your proxy service).
   - Enter your username and password (if required).
   - Ensure `Use proxy for peer connections` is checked.

### Summary:

- **Encryption**: Enable encryption in qBittorrent’s settings for basic obfuscation.
- **VPN**: Use a reputable VPN for the best level of privacy and obfuscation.
- **Proxy**: Use a SOCKS5 proxy if you prefer an alternative to a VPN.

By following these steps, you can make your torrenting activities more private and secure. Enjoy your safer torrenting experience, and if you need more help, I'm here for ya!


#### You:
Can you tell me about fopnu and tixati? 

#### ChatGPT:
Sure thing! Fopnu and Tixati are both peer-to-peer (P2P) file-sharing programs created by the same developer. They offer different features and cater to slightly different audiences, but both are well-regarded in the file-sharing community. Here's a rundown on each:

### **Fopnu**

**Overview**:
Fopnu is a relatively new P2P file-sharing network and application. It emphasizes simplicity and efficiency, aiming to provide a straightforward way to share and download files without the bloat or complexity found in some other P2P software.

**Key Features**:

1. **Pure P2P**: Fopnu is designed to be a pure P2P network, meaning it doesn't rely on any central servers. This makes it more resilient and less prone to downtime.
2. **Easy to Use**: The user interface is clean and straightforward, making it accessible for beginners.
3. **Encryption**: All connections are encrypted for security and privacy.
4. **No Ads or Spyware**: Fopnu is free of advertisements and spyware, offering a clean user experience.
5. **File Sharing**: It supports fast and efficient sharing of files, with features like file hashing, efficient downloading, and file integrity checking.
6. **Chat**: Built-in chat rooms and private messaging for community interaction.

**Pros**:

- Simple and intuitive interface.
- Secure with encrypted connections.
- No ads or bloatware.

**Cons**:

- Smaller user base compared to more established networks.
- Fewer advanced features compared to some other P2P clients.

### **Tixati**

**Overview**:
Tixati is a more mature P2P file-sharing client, primarily used for downloading torrents. It's known for its powerful features, detailed statistics, and efficient performance.

**Key Features**:

1. **Torrent Client**: Tixati is a full-featured torrent client that supports magnet links, DHT, PEX, and RSS.
2. **Detailed Statistics**: It provides detailed charts and graphs for bandwidth usage, download/upload speeds, and peer connections.
3. **Encryption**: Tixati supports full connection encryption to enhance privacy.
4. **Bandwidth Management**: Advanced bandwidth throttling and scheduling features.
5. **Event Scheduler**: Allows users to automate tasks like starting/stopping torrents at specific times.
6. **Channel Feature**: Tixati includes a unique feature called "Channels" which allows users to create and join channels for chat and file sharing.

**Pros**:

- Highly detailed statistics and charts.
- Powerful and flexible bandwidth management.
- Supports a wide range of torrenting features.
- No ads or spyware.

**Cons**:

- More complex interface, which may be overwhelming for beginners.
- No support for macOS (Windows and Linux only).

### Summary

- **Fopnu**: Great for users who want a simple, secure, and efficient P2P file-sharing experience without the complexity of torrenting.
- **Tixati**: Ideal for advanced users who need detailed statistics, powerful bandwidth management, and a full-featured torrent client.

Both Fopnu and Tixati are solid choices depending on your needs. If you want something straightforward, go for Fopnu. If you need more advanced features and are comfortable with a more complex interface, Tixati is the way to go.

If you have more questions or need further details, feel free to ask!
