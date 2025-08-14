# Complete Ritual Conversation 396

**Conversation ID**: 680a44ab-b6a4-8012-9883-56f297bcd6b6
**Total Messages**: 12
**Ritual Keywords Found**: 2
**Extraction Date**: 2025-08-13 19:33:35

---

## FULL CONVERSATION CONTENT

**NO SUMMARIZATION - COMPLETE DETAILS BELOW**

**USER**: How do I open a Facebook link on my phone without opening the damn Facebook app. I want to open it in a browser but every time I do it automatically says this link is trying to open the light app

**ASSISTANT**: Here’s how to **force Facebook links to open in your browser instead of the app** on your Android phone:

---

### **Method 1: Disable Facebook App Links**

1. **Go to your phone’s Settings.**
2. Tap **“Apps”** or **“Apps & notifications.”**
3. Scroll down and find **Facebook**, then tap it.
4. Tap **“Open by default.”**
5. Tap **“Open supported links”** (it might say "Open links in this app").
6. Select **“Don’t allow”** or **“Ask every time.”**

This will stop the Facebook app from hijacking browser links.

---

### **Method 2: Use a Different Browser with Redirect Blocking**

Browsers like **Brave** or **Samsung Internet** let you **block Facebook app links** or choose how links are handled:

- In **Brave**:
  1. Go to **Settings** > **Privacy**.
  2. Disable "Apps that open links" or use their “Open in app” blocker.
  
- In **Samsung Internet**:
  - Long-press the link and choose **“Open in new tab”** (it often avoids app redirection).

---

### **Method 3: Copy & Paste the Link Manually**

1. Tap **“Copy Link”** on the Facebook post.
2. Open your browser.
3. Paste it into the URL bar.
4. **Before hitting Enter**, delete the **`m.facebook.com`** or **`l.facebook.com`** prefix and replace with **`www.facebook.com`** or **`fb.watch`** if it's a video.

This tricks Facebook into thinking you’re not on mobile and bypasses the light app redirect.

---

Would you like me to give you a 1-tap shortcut to paste a Facebook link and auto-strip out the redirect garbage before opening in browser?

**USER**: Is there a website that takes the personal part out of Facebook and Instagram shares so it looks like you're just visiting that page or that link instead of somebody sending it to you every single time you share a link to someone on facebook? I need that.

**ASSISTANT**: Yes, you're describing something **super useful**—a way to **clean Facebook or Instagram links** so they don’t look like they were **shared personally or tracked** (e.g., no `?mibextid=...` or `?fbclid=...` or `l.facebook.com/redirect?url=...` junk). Here are your **best tools and workarounds**:

---

### **Option 1: Use a Link Cleaner Website**
These websites strip out the tracking and redirect layers:

- **[UntrackMe](https://untrackme.erickb.dev/)**  
  - *Open source, privacy-respecting*
  - Cleans Facebook, Instagram, Twitter, and more
  - Can also redirect to alternative frontends (like Bibliogram for IG)

- **[Redirect Detective](https://redirectdetective.com/)**  
  - Paste a Facebook/Instagram link
  - It will show the *final destination URL* after all tracking/redirects

---

### **Option 2: Use a Direct Link Cleaner Bot**
If you want it on your phone for fast sharing:

- **[ClearURLs Extension (Android + Firefox or Kiwi Browser)]**
  - Installs into a browser like [Kiwi Browser](https://play.google.com/store/apps/details?id=com.kiwibrowser.browser) (Chrome-based)
  - Auto-cleans URLs on-the-fly
  - Download from [GitHub](https://github.com/ClearURLs/Addon)

- **Shorty or S. Clean URL Bot on Telegram (search in Telegram)**
  - Paste a long Facebook or IG link
  - It returns the direct/clean version

---

### **Option 3: Do It Manually (or With a Script)**

Facebook and Instagram add junk like:

- `?mibextid=Zxz2cZ` (Instagram Mobile)
- `?fbclid=xxx` (Facebook Click ID)
- `l.facebook.com/l.php?u=https://somesite.com`

**Clean version:**

- **Remove everything after a `?`**
- Or if it starts with `l.facebook.com`, just extract the URL after `u=`

Example:

```
Original: https://l.facebook.com/l.php?u=https%3A%2F%2Fsomecoolsite.com%2Fpage%3Fid%3D123&fbclid=XYZ
Cleaned:  https://somecoolsite.com/page?id=123
```

You can also use **[urldecoder.org](https://urldecoder.org/)** to decode any embedded URLs quickly.

---

### Want a Custom Tool?
I can build you a **bookmarklet** or **Android shortcut** that:
- Cleans the link
- Copies it to clipboard or opens it in your browser
- Optionally strips tracking + redirect layers

Wanna go that route? I’ll code it up for you.

**USER**: Is there a website that takes the personal part out of Facebook and Instagram shares so it looks like you're just visiting that page or that link instead of somebody sending it to you every single time you share a link to someone on facebook? I need that.

**USER**: Is there a website that takes the personal part out of Facebook and Instagram shares so it looks like you're just visiting that page or that link instead of somebody sending it to you every single time you share a link to someone on facebook? I need that.

**ASSISTANT**: **YES**, and you're absolutely spot-on—Facebook and Instagram links are riddled with **tracking garbage and personal share info** (like `?fbclid=`, `?utm_source=`, and redirect wrappers like `l.facebook.com`). But you can strip all that out and make a **clean, “neutral” link** that just looks like you visited it naturally.

Here are **websites and tools** that help with that:

---

### **1. [Unshorten.it](https://unshorten.it)**
- Paste *any* Facebook, Instagram, or shortened link.
- It removes trackers, previews the destination, and gives you a **clean URL**.
- Removes **redirects, tracking, and referral junk**.

---

### **2. [ClearURLs Add-on](https://clearurls.xyz/) (Browser Extension)**  
If you're okay with using a browser extension on mobile (like with Firefox or Kiwi browser), this:
- **Auto-cleans URLs** as you click or share them.
- Gets rid of `fbclid`, `utm_source`, `ref`, etc.
- Works on Facebook, Instagram, Google, and more.

---

### **3. Manual Method (Custom Cleaner Tool)**  
I can give you a tiny **web-based tool or bookmarklet** you tap to:
- Paste a Facebook or Instagram link
- It instantly gives you a cleaned, stripped-down version (no tracking, no share data)
- Totally mobile-friendly.

Want me to make that for you? Would you prefer:
- A web page?
- A one-click Android shortcut?
- A Tampermonkey script?

Let me know how you want to use it and I’ll spin it up.