# Consolidated Ritual 577

**Date**: 2024-07-28
**Conversation ID**: 1128
**Parts Consolidated**: 1
**Content Hash**: 1924480df3795ec9529ebba47fb883b4

---

## COMPLETE CONSOLIDATED RITUAL INSTRUCTIONS

**NO SUMMARIZATION - ALL PARTS COMBINED BELOW**

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

And there ya go! Your qBittorrent should now be using your new DNS settings. Happy torrenting, and keep it safe! If you need more help, just holler!