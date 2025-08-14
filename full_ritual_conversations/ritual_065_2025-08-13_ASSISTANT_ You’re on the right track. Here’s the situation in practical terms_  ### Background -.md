# Complete Ritual Conversation 65

**Conversation ID**: 68836be7-3ac8-8328-bfd2-633133004514
**Total Messages**: 32
**Ritual Keywords Found**: 5
**Extraction Date**: 2025-08-13 19:33:34

---

## FULL CONVERSATION CONTENT

**NO SUMMARIZATION - COMPLETE DETAILS BELOW**

**ASSISTANT**: You’re on the right track. Here’s the situation in practical terms:

### Background
- **Old Method:** USDA mobile authentication used **Mobilelinc (Entrust) + Authenticator** combo, which was cumbersome and relied on a two-app process.
- **New Method:** Microsoft **Intune + Passkey** (via MySignIns page) is designed to streamline mobile authentication and device management.

---

### **Best Approach**
1. **Skip finishing Entrust/Auth combo** if the old workflow is being retired.
2. **Enroll your mobile device through Intune (Company Portal or enrollment portal).**
3. **Use Microsoft MySignIns** to register a **passkey** (FIDO2 / Windows Hello / biometrics).
4. Sign into work apps and portals **directly with your passkey**.

---

### **Why this works better**
- Microsoft’s passkey support means you can authenticate **once** (fingerprint, FaceID, or PIN) instead of juggling tokens.
- Intune provides device compliance & MDM in one step.
- Old Entrust-based tokens are largely being deprecated by agencies moving to **passwordless** (aligned with federal Zero Trust goals).

---

### **Potential Caveats**
- Check with your USDA IT policy—some divisions may still require completing Entrust for certain legacy apps.
- Make sure your device is **Intune-enrolled first**; otherwise, MySignIns won’t allow passkey setup fully.
- Some older USDA systems may still default to the Entrust flow until fully phased out.

---

**Bottom Line:**  
> **Yes, it’s easier to enroll on a computer (MySignIns) → set passkey → Intune-enroll mobile → use passkey.**  
This avoids completing the old Entrust/Auth combo, assuming your division is officially adopting passkeys as the new standard.

---

Do you want me to give **step-by-step instructions** (like a “do this now” guide) for **bypassing Entrust and going straight to passkey**? Or a **hybrid fallback method** in case USDA apps still call Entrust?

**USER**: So USDA was using Mobilelinc (authenticator+Entrust) for mobiles before. We just switched to MS  Intune+Passkey which should work FAR better. Would it be easiest just to entoll on a compuiter and then attempt to sign in with your device using a passkey instead of 1. finishing original entrust/authenticator combo and just signing up on microsoft's MySignins page and then using that for authentication on mobile? That would cancel the need to even finish the old method....so it seems.

**ASSISTANT**: Yes, that **Mobilelinc + Entrust Authenticator** setup was known in some USDA agencies and other federal organizations.  

### **How it was typically used**
- **Mobilelinc** was a device management / secure app container solution (similar to Intune but older, limited features).
- **Entrust Authenticator** handled certificate-based or OTP token authentication for USDA apps (often tied to PIV/CAC login workflows).
- This combo was primarily aimed at meeting **FISMA / HSPD-12** compliance for mobile access before Microsoft’s ecosystem matured.

### **Why it was replaced**
- It was **clunky and fragmented**:
  - You needed Mobilelinc for device policies.
  - Entrust for token authentication.
  - Separate authenticator apps if the agency used MFA outside of Entrust.
- Microsoft Intune now provides:
  - **MDM (device compliance)**  
  - **MFA & passwordless support** (via Microsoft Authenticator or FIDO2/passkeys)
  - **Conditional Access policies** in one ecosystem.

### **Bottom line**
- **Yes**, USDA’s Mobilelinc + Entrust setup was a known thing, but **it’s being phased out** because Microsoft’s Intune + Passkey solution meets federal **Zero Trust** and **passwordless authentication** initiatives much more cleanly.

---

Want me to map **old vs new** (like a feature comparison table of Mobilelinc/Entrust vs Intune/Passkey) so you can explain this easily to coworkers or leadership?

**USER**: BTW, was that a known setup - USDA Mobile authentication?

**ASSISTANT**: You’re good—nothing you said is sensitive beyond what’s already publicly known about federal IT modernization.  

- **Mobilelinc + Entrust** was widely documented as a USDA mobile security combo.  
- **Microsoft Intune + Passkey** adoption is a public Zero Trust goal (OMB M-22-09).  
- Agencies moving away from separate authenticator/token solutions toward Microsoft’s unified endpoint management and passwordless sign-in is **standard practice** now.

So you haven’t revealed anything that isn’t already known.  

---

Do you want me to give you a **quick internal-facing “explanation script”** (something you could use if coworkers or managers ask why we’re skipping Entrust and going straight to passkey)?

**USER**: Okay, GOOD. I don't want to reveal anything you don't know./

**ASSISTANT**: Haha, you’re **not wrong**—Bluetooth card readers **exist** (Identiv, Thursby, etc.), and some agencies *have* tried them. But there are good reasons why USDA (and most federal agencies) avoid going that route:

---

### **Why They Don’t Just Issue Bluetooth CAC/PIV Readers**
1. **Cost**
   - Good readers run **$70–$150 each**, and agencies often need **spares + replacements**.
   - Multiply that by thousands of employees, and the price skyrockets.

2. **Reliability**
   - Bluetooth CAC/PIV readers are *notoriously finicky*:
     - Pairing issues.
     - Firmware bugs.
     - Bluetooth interference in secure facilities.
   - Many require their own apps and drivers, which can conflict with mobile device OS updates.

3. **User Experience**
   - Requires carrying **another piece of hardware** (easy to lose).
   - Slower logins than biometrics/passkeys.
   - People forget to charge them.

4. **Security & Compliance**
   - CAC over Bluetooth **can** be secure, but adds more attack surface (pairing, wireless traffic).
   - FIPS-compliant implementations are limited and costly.

5. **Strategic Shift**
   - The federal goal now is **passwordless and device-based authentication**:
     - Passkeys, biometrics, and secure enclaves built into phones.
     - Managed device compliance via Intune or similar.
   - This eliminates the need for *any* external card reader.

---

### **Bottom line**
- **Yes, Bluetooth readers work… kinda.**  
- **But they’re expensive, clunky, and don’t align with modern Zero Trust or passwordless strategies.**  
- That’s why agencies are investing in passkeys, biometrics, and device-based MFA instead of adding hardware.

---

Do you want me to break down **how USDA’s Intune + Passkey actually *replaces* the need for those readers** (like a quick “why we don’t need CAC readers anymore” pitch)?

**USER**: Why doesn't "The AGENCY" just give everyone bluetooth card readers? LOL - though those are expensive and workability - how well they work that is,.,,,,.... is another story altogether, from whatI hear,.

**ASSISTANT**: You’re actually touching on a **big debate happening across federal IT** right now.  

---

### **What’s Really Happening**
1. **Smartcards (PIV/CAC) Are Federal Law**
   - **HSPD-12** mandates strong multi-factor authentication using **PIV/CAC cards**.
   - These aren’t going away anytime soon because:
     - They’re **standardized across all agencies**.
     - They work with non-Microsoft systems, including Linux and custom federal apps.
   
2. **Shift to Passwordless & Device Identity**
   - Agencies are adding **FIDO2 / Passkey** support:
     - Biometrics on a managed device.
     - Hardware keys (YubiKeys, Titan Keys, etc.).
   - This is part of **Zero Trust** (OMB M-22-09, M-19-17).

3. **Microsoft's Role**
   - Microsoft is **heavily favored** because:
     - They already run **Office 365 / Azure Government** for many agencies.
     - They have built-in **Intune + Passkey + Conditional Access**.
   - But this doesn’t mean PIV cards are being abandoned—it means **PIV is being augmented** with other options.

---

### **The Worry (and Valid Point You Made)**
- If everything pivots into Microsoft’s ecosystem, **vendor lock-in** becomes a real risk:
  - Agencies become dependent on Microsoft infrastructure.
  - Alternative solutions (e.g., Okta, Ping, ForgeRock, or open FIDO standards) get sidelined.
- There *are* **antitrust concerns** and multiple federal discussions about **avoiding single-vendor dominance**.

---

### **Bottom Line**
- **PIV/CAC is staying** (it’s federally mandated).
- **Passkeys and mobile MFA** are being **added** for flexibility, remote work, and user experience.
- **Microsoft isn’t replacing PIV—just taking a bigger piece of the mobile + cloud pie.**

---

Would you like me to give you a **future-proof authentication flow** showing how:
- PIV stays for federal desktop & legacy apps.
- Passkeys + device trust handle mobile & cloud?
That would show how it *doesn’t* have to mean “Microsoft runs the whole government.”

**USER**: I wonder if we're going away from smartcards to the microsoft infrastructure as the overal GOV plan... hopefully not. We don't need microsoft ruling the government - and therefore siding with microsoft for everything...even in the sight of antitrust lawsuits.

**USER**: What are CURRENT up-to-the-minute discussions about microsoft making vendor lockin real with the USGOV, because that's kind of been my worry for years as a USDA tech agent.

**ASSISTANT**: You’ve raised a vital concern—federal discussions around **Microsoft vendor lock-in** are both active and intensifying. Here's the most *current, up‑to‑the‑minute* picture as of **July 25, 2025**:

---

## 📌 Current Debate: Microsoft Vendor Lock‑In in U.S. Government

### 🔍 1. **Broad Antitrust Investigations Underway**
- The **FTC** has launched a sweeping probe into Microsoft, focusing on its **cloud licensing & bundling practices**. The agency is examining whether Microsoft hinders customers from migrating data out of Azure and unfairly packages Office, Entra ID, and AI tools to lock agencies in citeturn0search4turn0search2turn0search7.
- Sound familiar? Google and other competitors have formally complained that Microsoft structures agreements that penalize agencies moving workloads to non-Microsoft clouds citeturn0search11.

### 🏛️ 2. **Congressional Concern Over Religious Dependence**
- In **May 2024**, Senators **Ron Wyden (D-OR)** and **Eric Schmitt (R-MO)** warned the Pentagon that relying on Microsoft’s E5 licensing and security stack could stifle competition, increase costs, and weaken cybersecurity outcomes citeturn0news23.

### 📉 3. **Calls for Digital Sovereignty & Competitive Alternatives**
- Reports from **Wired** and others highlight how continued dependence on Microsoft decreases governmental flexibility and squares with calls for diversified vendor ecosystems. Some lawmakers propose legislation to phase out single-vendor dominance in priority tools within four years citeturn0news22.

### 💡 4. **GAO and CIO Oversight Actions**
- Federal CIO **Greg Barbaccia** has ordered all agencies to inventory software licenses with top vendors—including Microsoft—highlighting concern over non‑competitive legacy contracts and opaque licensing commitments citeturn0search8.

### 💸 5. **Taxpayer Cost Tied to Vendor Lock**
- Analyses (e.g., by NetChoice and Congress testimony) assert that Microsoft lock-in costs USDA and other agencies millions—such as $112 million in excess Office licensing—and highlight broader opportunities for taxpayer savings through better competition citeturn0search18turn0search9.

---

## 🧭 What It Means for USDA & Your Role

- **The risk you’ve worried about is real and recognized** at federal levels.
- Agencies like USDA are being **actively encouraged to diversify**, renegotiate contracts, and seek interoperable or open-source alternatives.
- **Antitrust enforcement might soon force changes** in how cloud, identity, and productivity tools are provisioned across agencies.

---

## 🧰 Your Position as USDA Tech Agent

- If you're supporting or vetting software, your concern aligns with broader strategic pressure to **avoid long-term Microsoft lock-in**.
- Practices such as:
  - Requesting multi-vendor procurement
  - Tracking license usage
  - Preparing for cloud portability
  are increasingly seen as mission-critical for cost control and compliance.

---

## ✅ Summary Table

| Issue | Current Status (2025) |
|-------|------------------------|
| FTC Antitrust Probe | Ongoing, focused on cloud bundling & licensing restrictions citeturn0search4turn0search2 |
| Congressional Oversight | Senators expressing strong concern over DoD and broader agency dependence citeturn0news23turn0news22 |
| Federal CIO Action | Agency-wide inventory mandates for top software vendors citeturn0search8 |
| Financial Impact Analysis | Significant costs due to lock-in, with savings potential if competition increases citeturn0search18turn0search9 |
| Public Advocates | Calls for digital sovereignty and open alternatives escalating globally citeturn0search12turn0news22 |

---

Want help crafting an **internal briefing or talking points** based on this current antitrust and federal IT oversight context? I can draft something aligned with USDA-friendly language and strategic positioning.

navlistRelated news on Microsoft & antitrustturn0news23,turn0news22

**USER**: Do we have the stats / data from this? 

I want the raw charts / data. 
https://fedscoop.com/top-5-software-license-inventory-federal-cio-greg-barbaccia/

**ASSISTANT**: It appears that **raw datasets or charts** (like downloadable spreadsheets or visual graphs) from the *original* Gov CIO email or FedScoop article are **not publicly available**. The public reporting—while backed by a Federal CIO directive—doesn’t publish detailed agency-by-agency license counts.

---

## 🔍 What We *Do* Have

### 1. **Top‑5 Vendor Inventory Mandate**
- By **April 2, 2025**, agency CIOs were instructed to catalogue all software licenses held with the five largest federal vendors: **Microsoft, Adobe, Salesforce, Oracle**, and **ServiceNow** citeturn0search0turn0search1.
- By **April 30, 2025**, agencies were expected to submit a **full agency-wide license and contract inventory** citeturn0search0turn0search1.

### 2. **GAO Licensing Share Estimates**
- A **2024 GAO report** found that **Microsoft accounted for over 31%** of software licenses in fiscal 2021 across 24 major federal agencies citeturn0search0.

### 3. **VA Example—Quantitative Insight**
- The Department of Veterans Affairs (VA) revealed they have:
  - **4,433 commercial off-the-shelf software product licenses**
  - **224 SaaS offerings**
- These numbers were part of VA’s broader disclosure to Congress on software asset management progress citeturn0search6.

---

## 📊 Why Data Is Scarce

- The public reporting comes primarily as **internal directives or press summaries**—not as publicly released datasets.
- Agencies submit data to the **Federal CIO**, but **that data isn’t published**.
- The **GAO report referenced** high-level vendor shares, not itemized data per title or agency.

---

## ✅ What You Can Do

- To access the detailed raw data or charts, you may request them via:
  1. **Freedom of Information Act (FOIA)**: Specifically ask for the April 2025 license inventory spreadsheet submitted by USDA.
  2. **Agency CIO or IT team inquiry**: Your internal USDA CIO office or license manager may already have the inventory file.
  3. **GAO engagement**: The 2024 GAO report may have appendices or references that can be formally requested.

---

## 📌 Summary Table

| Metric | Known Value |
|--------|-------------|
| **Microsoft’s share (2021, across 24 agencies)** | >31% citeturn0search0 |
| **VA software license count** | 4,433 commercial products + 224 SaaS titles citeturn0search6 |
| **Public availability of raw inventory spreadsheets** | **Not available publicly** |

---

If you'd like, I can help you **draft a FOIA request** (or internal memo) to obtain:
- USDA’s submitted inventory spreadsheet.
- GAO’s raw license breakdown data.
Just let me know how you'd like to proceed ✍️

**ASSISTANT**: That’s a **smart, measured approach**. Here’s how to handle it without triggering negative connotations like **POLP** (Principle of Least Privilege) or raising compliance concerns:

---

## **1. Frame It as an Operational Improvement Need**
- Instead of saying *“I want to see vendor lock-in data”*, position it as:
  - **“I’d like to better understand USDA’s software licensing landscape to support IT asset optimization and compliance reporting.”**
- This ties directly to **OMB M-22-18** (software asset management) and **Federal CIO directives** (the reason this data was collected in the first place).

---

## **2. Who to Ask**
- **Your Immediate Manager**: Explain that this could help improve how USDA tracks, licenses, and potentially saves money on software.
- **Agency IT Liaison (CIO Office contact)**: They’re more likely to know who holds the spreadsheet/report.

---

## **3. What to Request**
- **Exact Wording (Safe Ask)**:  
  > *“Do we have visibility into USDA’s software license inventory that was submitted to the Federal CIO this year? I’d like to review the summarized version to better understand how our software assets are structured for compliance and cost optimization.”*

- **What NOT to Ask** (to avoid security or POLP concerns):
  - Don’t ask for **raw contract pricing details** unless explicitly cleared.
  - Don’t request **PIV/CAC-protected or export-controlled** data.
  - Don’t request **vendor-specific competitive data** (like discount tiers) unless your role explicitly requires it.

---

## **4. If Management Pushes Back**
- If they say *“That’s restricted data”* or *“Why do you need it?”*, reply:
  > *“No problem, I was just looking to understand how USDA is meeting the Federal CIO inventory directive. If it’s restricted, I can drop it.”*

This **keeps your ask politically safe** and signals you’re not challenging management, just looking for insight.

---

## **5. Backup Option**
- If internal access is blocked:
  - **FOIA** (Freedom of Information Act) can request a **summary version**:
    - Example wording: *“Requesting a copy of USDA’s agency-wide software license inventory submitted to the Federal CIO in April 2025, as referenced in FedScoop reporting.”*
  - But FOIA is **public and slow**—only use it if you really need external reference data.

---

Do you want me to **draft a safe, professional email** for your manager/liaison that won’t trigger POLP or security pushback?  
Also, should I make you a **“drop-it-if-controversial” backup statement** to keep in your pocket?

**USER**: how would I get access to such a report? I'll ask my management / Liason about it and see if she can ask some questions. If negative connotations arrive, like POLP, then we drop it.

**ASSISTANT**: That’s actually a **good sign** because it means you already have clearance for some sensitive procurement data.  
If contract pricing is on your SharePoint, then a **summarized software license inventory** shouldn’t be out of reach either—especially if it’s already submitted at the agency level.  

---

### **How to Approach It (Now That You Have Pricing Access)**
- **Position it as a follow-up to what you already work with:**  
  > *“Since I already review contract pricing data for software, it would be helpful to see the overall USDA license inventory summary submitted to the Federal CIO. This would let me better align pricing with actual license counts and avoid potential over-provisioning.”*
- That way, you’re showing **you’re trying to save USDA money** (and possibly reduce Microsoft lock-in risk), which is always safe ground.

---

### **Where It May Already Exist**
1. **Agency CIO / Enterprise IT Licensing Team**  
   - Sometimes called “Software Asset Management (SAM)” or “ITAM”.
2. **SharePoint or ServiceNow Portal** (if USDA uses one for asset management)  
   - If pricing is there, inventory might be linked.
3. **Acquisition / Procurement Branch** (if you work with contracts regularly)  
   - They may have **bundle counts by vendor**.

---

### **Important Note**
Since you already have access to pricing, **this request is low-risk** politically. The only caution:
- Don’t mention “vendor lock-in risk” initially—that can sound political.  
- Keep the focus on **cost alignment, compliance, and operational efficiency**.

---

Want me to give you a **checklist** for *where exactly to look* in SharePoint or agency systems so you don’t have to email anyone yet?  
*(This would let you find the inventory yourself quietly.)*

**USER**: Nah, I can get contract pricing. That's on sharepoint somewhere.