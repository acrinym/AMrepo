# Complete Ritual Conversation 128

**Conversation ID**: 684c3a11-e6dc-8012-b955-a0e8f6831004
**Total Messages**: 19
**Ritual Keywords Found**: 8
**Extraction Date**: 2025-08-13 19:33:34

---

## FULL CONVERSATION CONTENT

**NO SUMMARIZATION - COMPLETE DETAILS BELOW**

**USER**: Okay, Onyx, we can do better than these using tampermonkey, like we were talking about yesterday. 

We create a script that does a hell of a lot more. 

https://www.userscript.zone/search?q=Github+diff

**ASSISTANT**: Absolutely, Justin! Tampermonkey scripts can do *far* more than most people realize—especially for workflow automation, memory extraction, or custom overlays for platforms like GitHub (or even for saving/organizing ChatGPT memory, which is still basically uncharted territory).

### What You're Asking:
You want a Tampermonkey script (or suite of scripts) that:
- **Interacts deeply with GitHub diffs** (possibly: extracting, summarizing, overlaying new UI, or managing patches/commits).
- Goes **way beyond vanilla user scripts**: possibly automating memory exports, managing summaries, and integrating with tools like Google Drive or custom endpoints.
- Can eventually serve as a "memory manager" for ChatGPT and other workflows.

---

## Let’s Start with the Basics:  
**What do you want this script to do first?**
- Scrape & summarize GitHub diff/commit pages?
- Overlay a new sidebar or interface on GitHub for quick actions?
- Export diffs or discussions to Google Drive or another storage?
- Integrate with ChatGPT (e.g., grab output and auto-save to a knowledge base)?

If you want, we can scaffold a modular Tampermonkey base that lets you *add* features as you go. But I’ll give you a few direct examples below for each level of ambition:

---

### 1. **Basic: Extract GitHub Diff and Summarize**
This script adds a button on GitHub "diff" pages to scrape all diff text, then display it in a modal or let you copy/export.

```javascript
// ==UserScript==
// @name         GitHub Diff Extractor
// @namespace    https://github.com/yourusername
// @version      0.1
// @description  Extract diffs from GitHub and display/copy/export
// @match        https://github.com/*/pull/*/files*
// @match        https://github.com/*/commit/*
// @grant        GM_setClipboard
// ==/UserScript==

(function() {
    'use strict';

    function extractDiff() {
        let diffs = [];
        document.querySelectorAll('.js-file-content.Details').forEach(block => {
            const filename = block.querySelector('.file-header').dataset.path || "unknown";
            const diff = block.querySelector('.diff-table')?.innerText || '';
            diffs.push(`--- ${filename} ---\n${diff}`);
        });
        return diffs.join('\n\n');
    }

    function showModal(text) {
        const modal = document.createElement('div');
        modal.style = "position:fixed;top:10%;left:10%;width:80vw;height:80vh;background:white;z-index:9999;overflow:auto;padding:20px;border:3px solid #333;";
        modal.innerHTML = `
            <textarea style="width:100%;height:80%;">${text}</textarea>
            <button id="copyDiff">Copy</button>
            <button onclick="this.parentElement.remove()">Close</button>
        `;
        document.body.appendChild(modal);
        document.getElementById('copyDiff').onclick = () => {
            GM_setClipboard(text);
            alert('Copied!');
        };
    }

    // Add a button to GitHub page
    function addButton() {
        if (document.getElementById('extractDiffBtn')) return;
        let btn = document.createElement('button');
        btn.textContent = 'Extract Diff';
        btn.id = 'extractDiffBtn';
        btn.style = 'position:fixed;bottom:20px;right:20px;z-index:99999;padding:10px 18px;background:#28a745;color:#fff;border-radius:6px;border:none;font-size:18px;';
        btn.onclick = () => showModal(extractDiff());
        document.body.appendChild(btn);
    }

    setTimeout(addButton, 3000); // Add button after 3s

})();
```

---

### 2. **Intermediate: Export to Google Drive (via Google Picker/Drive API)**
This takes a bit more setup, but if you want a button that *saves* a diff file to your Drive:

- You need a [Google Drive API key & OAuth credentials](https://developers.google.com/drive/api/quickstart/js).
- The script can launch a Google Auth flow, then save the file directly.
- Want this? I’ll walk you through credential setup if you want a working version.

---

### 3. **Advanced: Memory Manager with ChatGPT/AI Integration**
- Overlay a sidebar/panel for “memory slots” (quick save/load/categorize notes/diffs/convos).
- Integrate with a backend (local Flask server, Supabase, whatever you want).
- Periodic auto-save of ChatGPT conversations or GitHub diffs.
- Build your own “personal knowledge base” from anywhere on the web.

---

## **Questions For You**
- What’s your *minimum viable* feature for today?
- Are you good with scripts that just run locally in Tampermonkey, or do you want Drive/API integration right now?
- Do you want to scrape just diffs, or also conversations/comments/etc?
- Should it support ChatGPT and GitHub together, or are we focusing on one first?

---

## 🔥 *My Suggestion*  
**Start with a killer local “Extract + Copy + Modal” for GitHub diffs.**  
From there, we can stack features (export, AI summary, auto-categorize, etc).  
And if you want a “memory panel” for ChatGPT/Onyx work, we can design a floating sidebar you can pop open on any page.

---

What’s your vision for *phase 1*?  
- Full code above is ready to drop in Tampermonkey.
- Ready to level up when you say the word.

What’s next, boss?

**ASSISTANT**: Oh, now we’re talking! The **GitHub Pull Request Conflicts page** is one of the most *painfully* inefficient pages for developers, especially if you deal with big merges or multi-file spaghetti. But it’s also a goldmine for automation and workflow improvement with user scripts.

Let’s riff out some bold ideas—**no filter, full-spectrum dev/operator mindset:**

---

## 💡 **10 Killer Tampermonkey Ideas for `/pull/*/conflicts` Pages**

### 1. **“One-Click Diff Export”**
- **Button**: Export *all* conflicted file diffs to a modal or clipboard.
- **Why?** You get a full view for external analysis, patching, or AI summarization.

---

### 2. **“Side-by-Side Enhanced View”**
- **Overlay**: Auto-builds a true side-by-side (three-way) diff like VS Code/Meld.
- **Why?** GitHub’s inline format is annoying for serious review. True side-by-side lets you spot & resolve conflicts faster.

---

### 3. **“AI/LLM Merge Assistant”**
- **Button**: For each conflicted file, send both versions (base/your/their) to an AI (could be local, OpenAI, LLM API) for suggested merge output.
- **Why?** Save 80% of grunt work for “obvious” merges. Review AI suggestions before accepting.

---

### 4. **“Conflict Status Tracker”**
- **UI Add-on**: Adds a floating panel listing all conflicted files, their size, number of conflicts, and your progress (e.g., resolved/needs work).
- **Why?** Gamifies/confirms progress; you never lose track in a 20+ file PR.

---

### 5. **“Quick Copy” for Both Sides**
- **Button**: Instantly copy “ours” or “theirs” code block to clipboard for external editing.
- **Why?** Super fast when you need to patch in your IDE.

---

### 6. **“Auto-Collapse/Expand All”**
- **UI Tool**: Collapse all but the current conflict, or expand all in one click.
- **Why?** Makes navigation a breeze for huge merges.

---

### 7. **“In-Page Patch Generator”**
- **Button**: For each conflict, auto-generate a `.patch` file download for that chunk (or all at once).
- **Why?** Patch locally without pulling down the full PR.

---

### 8. **“Comment/Note Overlay”**
- **Sticky Notes**: Drop comments/notes per conflict directly on the page, save them locally or sync to a Google Sheet/Drive.
- **Why?** Keep track of complex resolutions, TODOs, or blockers for each file.

---

### 9. **“Merge Summary/Heatmap”**
- **Sidebar**: Visual heatmap of which files have the most/least conflicts, by line count or frequency.
- **Why?** Triage the nastiest files first—focus on pain points.

---

### 10. **“Batch ‘Accept Theirs’/‘Accept Ours’”**
- **Power Button**: For *non-critical* conflicts (where you know the answer), apply “ours” or “theirs” to all with one click, and only review the rest.
- **Why?** Save hours on boring merges.

---

## 🛠️ **Example: “Quick Copy Ours/Theirs” UserScript**

Here’s a basic implementation you could drop into Tampermonkey *today* for “copy ours/theirs” blocks on the `/conflicts` page:

```javascript
// ==UserScript==
// @name         GitHub PR Conflict Copy Helper
// @namespace    https://github.com/yourusername
// @version      0.2
// @description  Adds 'Copy Ours' and 'Copy Theirs' buttons to each conflict block on PR conflicts page
// @match        https://github.com/*/pull/*/conflicts
// @grant        GM_setClipboard
// ==/UserScript==

(function() {
    'use strict';

    // Utility: Extracts code between <<<<<<< and ======= (ours), and between ======= and >>>>>>> (theirs)
    function extractSides(conflictBlock) {
        const text = conflictBlock.innerText;
        const oursMatch = text.match(/<<<<<<<.*?\n([\s\S]*?)=======/);
        const theirsMatch = text.match(/=======\n([\s\S]*?)>>>>>>>/);
        return {
            ours: oursMatch ? oursMatch[1].trim() : '',
            theirs: theirsMatch ? theirsMatch[1].trim() : ''
        };
    }

    function addCopyButtons() {
        // For each conflict block (should match diff container or code block)
        document.querySelectorAll('.js-blob-code-container').forEach(block => {
            // Prevent double buttons
            if (block.querySelector('.onyx-copy-btn')) return;

            const sides = extractSides(block);
            const btnOurs = document.createElement('button');
            btnOurs.textContent = 'Copy Ours';
            btnOurs.className = 'onyx-copy-btn';
            btnOurs.style = 'margin: 5px 8px; font-size:12px;';
            btnOurs.onclick = () => { GM_setClipboard(sides.ours); btnOurs.textContent = 'Copied!'; setTimeout(()=>btnOurs.textContent='Copy Ours',1500); };

            const btnTheirs = document.createElement('button');
            btnTheirs.textContent = 'Copy Theirs';
            btnTheirs.className = 'onyx-copy-btn';
            btnTheirs.style = 'margin: 5px 8px; font-size:12px;';
            btnTheirs.onclick = () => { GM_setClipboard(sides.theirs); btnTheirs.textContent = 'Copied!'; setTimeout(()=>btnTheirs.textContent='Copy Theirs',1500); };

            block.prepend(btnOurs, btnTheirs);
        });
    }

    setTimeout(addCopyButtons, 3000); // Wait for DOM
})();
```
**(Modify selectors as needed for your GitHub theme/layout; can be expanded for “export all,” etc.)**

---

## 🧩 **Next Level: Merge Assistant / Panel**
- Inject a floating panel (like a VS Code minimap) to:
  - List all conflicts, status
  - AI suggestions
  - Fast file navigation
  - Quick links to “accept ours/theirs” everywhere

---

## 💭 **Questions for Next Step**
1. Which of these ideas excites you *most* for your workflow right now?
2. Want me to expand on “AI merge assistant”?
3. Would you rather have in-page overlays, or a floating sidebar?
4. Is Google Drive export still a must-have, or mostly for archiving?
5. Should we try to make it cross-site (i.e., GitHub + GitLab) or focus on GitHub for now?

---

Let me know where you want to start, and I’ll crank out that script or scaffold the expansion!  
**You want empire-tier merge tools? Let’s build ‘em.**

**USER**: Focus on Github for now. We need exquisite and tools not found in greasyfork or tampermonkey already.

**ASSISTANT**: **Hell yes, Justin.** This is exactly the right mindset—**no more copycat scripts** or weak sauce overlays. Let’s design tools that *GitHub itself* wishes it had. Here’s how we’ll approach it:

---

## **Step 1: Identify the Gaps**
What *doesn’t* exist on Greasyfork, Userscript.zone, or Tampermonkey script sites?  
What *pain points* do you (and real power users) experience with GitHub’s PR, diff, and conflicts pages?

---

### 🔥 **Missing/Underserved Features:**

#### 1. **True AI-Assisted Merge Resolution**
- **Not just “summarize this PR.”**
- *Context-aware* inline AI merge suggestions (for each conflict block), with an editable preview, *and* a “why did you make this suggestion?” explainer.
- **Never been done** in a userscript—everyone stops at “send diff to OpenAI.”

#### 2. **Merge Conflict “Battle Map” Overlay**
- **Visual navigation of all conflict zones** in a multi-file PR (with heatmap, jump-to, and check-off functionality).
- Visualize: colored minimap/scrollbar showing hotspots and resolved/unresolved status.

#### 3. **Batch Conflict Automation (with Safety Nets)**
- *One-click*: Accept all “theirs”/“ours” *except* files with X+ conflicts or regex match in filename.
- **Manual override** for “danger zones,” with file previews and instant revert.

#### 4. **Per-Conflict Field Notes/Annotations**
- Inline sticky notes attached to each diff block (stored in localStorage or synced via GitHub Gist).
- Quick search/filter of notes across all conflicts in a PR.

#### 5. **Advanced Patch Generation & Download**
- *Export only unresolved conflicts* as `.patch` or `.diff` file (not just the full file, but *conflict-only snippets*).
- Download “AI suggestion” as patch for off-page review.

#### 6. **Auto-Sync to Personal Knowledge Base**
- Export all conflict metadata (filenames, conflict lines, decisions, notes, timestamps) to JSON or direct upload to your Google Drive/Notion/Obsidian vault.
- Never lose a merge decision again.

#### 7. **Instant “Blame Diff” Visualization**
- Overlay “blame” info (who/when/what commit) directly on conflict lines—*in-page*, not a separate click.
- Hotkey: highlight all changes authored by you vs. them.

#### 8. **“Rehearse the Merge” Simulator**
- Preview a dry-run merge right in the browser (simulate what will happen if you accept “ours,” “theirs,” or the AI’s suggestion).
- See which lines will survive, die, or get changed, in *real time*.

---

## **Step 2: Which One First?**
**I vote for #1 (AI merge with in-page suggestions + explainers) or #2 (conflict “battle map”).**  
They’re both *painfully* absent from all current scripts.

---

## **Example: Scaffold for AI-Assisted Merge with Inline Explanations**

```javascript
// ==UserScript==
// @name         GitHub AI Merge Assistant (Prototype)
// @namespace    https://github.com/onyx-amanda
// @version      0.1
// @description  Adds AI-powered merge suggestions to each conflict block with explanations
// @match        https://github.com/*/pull/*/conflicts
// @grant        GM_xmlhttpRequest
// @grant        GM_setClipboard
// ==/UserScript==

(function() {
    'use strict';

    // Helper to inject UI to each conflict block
    function injectAIAssistant() {
        document.querySelectorAll('.js-blob-code-container').forEach(block => {
            if (block.querySelector('.ai-merge-btn')) return; // Already injected

            // Extract both sides (yours/theirs)
            const text = block.innerText;
            const ours = (text.match(/<<<<<<<.*?\n([\s\S]*?)=======/)||[])[1] || '';
            const theirs = (text.match(/=======\n([\s\S]*?)>>>>>>>/)||[])[1] || '';

            // UI Elements
            const aiBtn = document.createElement('button');
            aiBtn.className = 'ai-merge-btn';
            aiBtn.textContent = 'AI Merge Suggest';
            aiBtn.style = 'margin: 8px; background: #6e4fff; color: #fff; border-radius: 5px; padding: 5px 12px; border: none;';
            const aiResult = document.createElement('div');
            aiResult.style = 'margin-top:8px; background:#f6f8fa; border:1px solid #ddd; padding:10px; white-space:pre-wrap; font-family:monospace;';
            
            aiBtn.onclick = () => {
                aiBtn.textContent = 'Thinking...';
                // Example API: Replace with your own endpoint or local LLM bridge!
                GM_xmlhttpRequest({
                    method: "POST",
                    url: "https://your-ai-merge-api.example.com/merge",
                    headers: { "Content-Type": "application/json" },
                    data: JSON.stringify({ ours: ours, theirs: theirs }),
                    onload: function(response) {
                        try {
                            const data = JSON.parse(response.responseText);
                            aiResult.innerHTML = `<b>AI Suggestion:</b>\n${data.suggestion}\n\n<b>Why:</b>\n${data.explanation}`;
                        } catch {
                            aiResult.textContent = 'AI Error: Bad response.';
                        }
                        aiBtn.textContent = 'AI Merge Suggest';
                    }
                });
            };

            block.prepend(aiBtn, aiResult);
        });
    }

    setTimeout(injectAIAssistant, 2500);
})();
```
**Note:** This is a *scaffold*—you’ll need an actual API to process the merges, which can be your own local LLM or OpenAI proxy, or even a local Python Flask bridge that does the merge & summary.

---

## **Let’s Design Together**
- **Which one is the priority?** (AI merge/explainer, battle map, or another above?)
- Do you want “explainers” for every merge, or a “navigator” overlay, or both?
- Should everything be stored locally, or should we build in a remote sync/export option from the start?

---

## **Next Steps**
- You pick the *feature*; I’ll write the *actual code*—ready for Tampermonkey, *not* found anywhere else.
- Want a sidebar “battle map”?  
- Want AI merge with in-page rationale?  
- Or batch/patch export?  

**Let’s drop something on GitHub nobody’s ever seen.**  
Your call. What do we build first?

**USER**: Let's start with building a boilerplate array of functions/calls/variables/EVERYTHING for one language at a time. 
Javascript is up first. Once we have a C+P boilerplate array, we can create a c+p version of an array and functionality definer to be able to really know if a function/call/DEF/etc is valid or if it's just erroneously placed code(s), etc. 

We can also then implement a new language, one at at time. Let's go! Boilerplate first. No code dictionary... yet.

**ASSISTANT**: **Onyx here—ready to drop the ultimate JavaScript function/call/variable boilerplate array.**  
This is *not* just a “list of keywords”—this is a **curated, paste-ready, full-spectrum JavaScript developer reference array** you can use for:
- Linting
- Code validation
- Language feature detection
- Future code analysis tools (or auto-doc generation, code search, or refactor tools)
- Rapid expansion to other languages (by swapping the array/object)
- Generating a “definer” or validator system (once you want it)

---

## **Phase 1: JavaScript Boilerplate Array**  
Here’s a “C+P” (Copy & Paste) array/object with:
- All key variable types (`var`, `let`, `const`)
- Standard global objects/functions
- Built-in object/class names
- Control flow keywords
- Common function declaration syntaxes
- Method names for Arrays, Objects, Strings, Promises, etc.
- Useful call patterns  
*...and more. You can expand it as needed.*

---

### **The Master JavaScript “Boilerplate” Definitions Array**

```js
const JS_CORE_KEYWORDS = [
  // Declarations
  "var", "let", "const", "function", "class", "extends", "constructor", "import", "export", "default", "async", "await", "static", "get", "set",

  // Control flow
  "if", "else", "switch", "case", "break", "continue", "for", "while", "do", "try", "catch", "finally", "throw", "return", "yield", "with",

  // Primitive types & literals
  "undefined", "null", "true", "false", "NaN", "Infinity",

  // Operators
  "typeof", "instanceof", "new", "delete", "void", "in", "of", "super", "this",

  // Global objects
  "window", "globalThis", "document", "console", "Math", "JSON", "Date", "Array", "String", "Number", "Boolean", "Object", "Symbol", "BigInt", "Map", "Set", "WeakMap", "WeakSet", "Promise", "RegExp", "Error", "EvalError", "RangeError", "ReferenceError", "SyntaxError", "TypeError", "URIError", "Function",

  // Built-in browser API (partial!)
  "fetch", "XMLHttpRequest", "setTimeout", "setInterval", "clearTimeout", "clearInterval", "requestAnimationFrame", "cancelAnimationFrame", "localStorage", "sessionStorage", "FileReader", "Blob", "URL", "alert", "prompt", "confirm", "addEventListener", "removeEventListener", "Event", "CustomEvent", "dispatchEvent",

  // DOM access
  "getElementById", "getElementsByClassName", "getElementsByTagName", "querySelector", "querySelectorAll", "createElement", "appendChild", "removeChild", "replaceChild", "insertBefore", "innerHTML", "outerHTML", "textContent", "style", "classList", "className",

  // Arrays
  "push", "pop", "shift", "unshift", "slice", "splice", "concat", "map", "filter", "reduce", "forEach", "find", "findIndex", "includes", "every", "some", "indexOf", "lastIndexOf", "join", "reverse", "sort", "flat", "fill", "copyWithin",

  // Objects
  "keys", "values", "entries", "assign", "hasOwnProperty", "defineProperty", "freeze", "seal", "create", "fromEntries",

  // Strings
  "charAt", "charCodeAt", "codePointAt", "fromCharCode", "fromCodePoint", "includes", "startsWith", "endsWith", "slice", "substring", "substr", "replace", "replaceAll", "split", "trim", "toLowerCase", "toUpperCase", "repeat", "padStart", "padEnd", "match", "search", "indexOf", "lastIndexOf", "localeCompare", "concat",

  // Functions
  "apply", "call", "bind", "toString",

  // Promises
  "then", "catch", "finally", "resolve", "reject", "all", "race", "allSettled", "any",

  // Iterators / Generators
  "next", "return", "throw", "Symbol.iterator", "yield",

  // Miscellaneous
  "arguments", "require", "module", "exports", "__dirname", "__filename"
];

// For more advanced use, you could expand this into a detailed object:
const JS_DEFINITION_OBJECT = {
  keywords: JS_CORE_KEYWORDS,
  declaration: ["var", "let", "const", "function", "class"],
  controlFlow: ["if", "else", "switch", "case", "break", "continue", "for", "while", "do", "try", "catch", "finally", "throw", "return"],
  primitives: ["undefined", "null", "true", "false", "NaN", "Infinity"],
  globalObjects: ["window", "globalThis", "document", "console", "Math", "JSON", "Date", "Array", "String", "Number", "Boolean", "Object", "Symbol", "BigInt", "Map", "Set", "WeakMap", "WeakSet", "Promise", "RegExp", "Error"],
  operators: ["typeof", "instanceof", "new", "delete", "void", "in", "of", "super", "this"],
  browserAPIs: ["fetch", "XMLHttpRequest", "setTimeout", "setInterval", "clearTimeout", "clearInterval", "requestAnimationFrame", "cancelAnimationFrame", "localStorage", "sessionStorage", "FileReader", "Blob", "URL", "alert", "prompt", "confirm", "addEventListener", "removeEventListener", "Event", "CustomEvent", "dispatchEvent"],
  dom: ["getElementById", "getElementsByClassName", "getElementsByTagName", "querySelector", "querySelectorAll", "createElement", "appendChild", "removeChild", "replaceChild", "insertBefore", "innerHTML", "outerHTML", "textContent", "style", "classList", "className"],
  arrayMethods: ["push", "pop", "shift", "unshift", "slice", "splice", "concat", "map", "filter", "reduce", "forEach", "find", "findIndex", "includes", "every", "some", "indexOf", "lastIndexOf", "join", "reverse", "sort", "flat", "fill", "copyWithin"],
  objectMethods: ["keys", "values", "entries", "assign", "hasOwnProperty", "defineProperty", "freeze", "seal", "create", "fromEntries"],
  stringMethods: ["charAt", "charCodeAt", "codePointAt", "fromCharCode", "fromCodePoint", "includes", "startsWith", "endsWith", "slice", "substring", "substr", "replace", "replaceAll", "split", "trim", "toLowerCase", "toUpperCase", "repeat", "padStart", "padEnd", "match", "search", "indexOf", "lastIndexOf", "localeCompare", "concat"],
  functionMethods: ["apply", "call", "bind", "toString"],
  promiseMethods: ["then", "catch", "finally", "resolve", "reject", "all", "race", "allSettled", "any"],
  iterators: ["next", "return", "throw", "Symbol.iterator", "yield"],
  nodeGlobals: ["require", "module", "exports", "__dirname", "__filename"],
  special: ["arguments"]
};
```

---

### **How to Use:**
- **Validation:** Check if a token matches an array item for “is this valid JS?”
- **Completion:** Generate IDE-style intellisense/autocomplete popups.
- **Syntax checking:** Quickly flag “not a real JS core method/keyword.”

---

### **Your Next Steps:**
- **Want this in array form, or structured object (above) for category filtering?**
- **Ready for a Python/C#/C++ version after this?**
- Do you want helper functions (e.g., `isValidKeyword(token)`) right now, or just the raw array/object?

---

**Ready to copy-paste, ready to expand, and ready to conquer.  
Just say the word for the next language or phase!**

**USER**: Yes, but Javascript can also have custom defs / consts. Su unless they are defined earlier in the code, they are invalid. Perfect for a issue-finder.

**ASSISTANT**: **Exactly, Justin.**  
That’s *the key insight*—in JavaScript, a “bare” identifier (function, variable, const, class, etc.) is only valid if:
1. It’s a reserved word or global/built-in.
2. **OR:** It was defined previously in the current/local/global scope.

**Anything else is a logic or reference error.**  
This is why true “issue-finder” scripts need both:
- A list of core language features (the boilerplate we just built).
- **AND:** A way to *track definitions as the code is parsed*—in order.

---

## **Phase 2: Validator/Issue-Finder Blueprint (JS)**

### **Basic Algorithm Steps:**
1. **Scan Code Top-to-Bottom:**  
   For each line, extract identifiers (function names, variables, etc.).
2. **Maintain a Running Set:**  
   Start with the global array/object above.
3. **For Each Identifier:**
   - If it’s in the core array: VALID.
   - If it’s in the running set (already defined): VALID.
   - If it’s being defined on this line (e.g., `const foo = ...`): add to running set.
   - Otherwise: **POTENTIAL ERROR** (undefined identifier).

---

### **Pseudo-Code Example:**

```js
const CORE = /* array from above */;
let defined = new Set(CORE); // Start with built-ins

for (let line of codeLines) {
    // Example: extract identifiers using regex or parsing
    let [defType, name] = extractDefinition(line); // e.g., ["const", "foo"]
    if (defType) defined.add(name);

    let calledIdentifiers = extractIdentifiers(line);
    for (let id of calledIdentifiers) {
        if (!defined.has(id)) {
            console.warn(`Possible undefined identifier: ${id} at line ${i}`);
        }
    }
}
```
*This is just conceptual—you can use AST parsing for real-world use, or regex for fast and dirty.*

---

## **Why Is This Killer?**
- **Flags typos, missing imports, misspelled calls instantly.**
- **Lets you build “lint on the fly” for any web code window, or analyze GitHub diffs for “naked undefineds.”**
- **Scalable to other languages** by swapping out the core definitions and definition logic.

---

## **Optional Bonus:**  
**Track scopes:** (so you don’t flag identifiers that are legit inside a function or block)

---

## **Next Steps / Action Items**

### 1. **Want a working demo in JavaScript?**
- I can code you a *simple Tampermonkey* or *Node script* that finds undefined calls in a code block, using the above method.

### 2. **Want Python or C++ boilerplate next?**
- I’ll build that core array/object to swap in for language support.

### 3. **Do you want the validator as:**
- Standalone Node.js tool?
- Browser/Tampermonkey script for live linting?
- Or “analyze a code blob pasted into a page”?

---

**Let me know your preferred implementation,  
and I’ll write the actual issue-finder code next!**  
We can get this running *today* as your own lightning-fast linter.

**ASSISTANT**: **Crystal clear, Justin.**  
Let’s **focus on Tampermonkey for work** (browser-based, runs anywhere GitHub, GitLab, or any web IDE is open),  
and we’ll worry about a standalone Avalonia (or desktop) version for your off-hours.

---

## 🟩 **Here’s the Plan for the Tampermonkey Issue-Finder:**

### **1. Core Feature**
- **Live flagging of undefined variables/functions** (anything not core or previously defined)
- Works on any code block you select or view on a web page—think GitHub PRs, code review tools, or even StackOverflow

### **2. “Worksafe”**
- No file writing, no outside APIs—pure in-browser JS
- Highlights or lists issues in a sidebar/modal, not in the code directly

### **3. UI**
- Small floating button: “Check for Undefineds”
- Click: runs linter on visible code blocks, shows results in a popup/modal (list of “potential undefineds” + line number)

---

## **First Implementation: MVP Tampermonkey Script**

This will:
- Use our **core array** (from above)
- Scan all visible `<pre>`, `<code>`, or `.blob-code` blocks
- Parse lines for basic JS variable/function names
- Track “defined” items (`var`, `let`, `const`, `function`, `class`, etc.) as it scans
- Warn about *usages* of names never seen or not in core

---

### **Ready-to-Use Script:**

```javascript
// ==UserScript==
// @name         JS Issue Finder (Tampermonkey MVP)
// @namespace    https://github.com/onyx-amanda
// @version      0.1
// @description  Find undefined JS identifiers in code blocks on web pages
// @match        *://*/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Core JS built-ins (from previous answer, short version for brevity)
    const CORE = [
        "var","let","const","function","class","constructor","import","export","default","async","await",
        "window","document","console","Math","JSON","Date","Array","String","Number","Boolean","Object","Symbol","Map","Set","WeakMap","WeakSet","Promise","RegExp","Error","Function",
        "if","else","switch","case","break","continue","for","while","do","try","catch","finally","throw","return",
        "typeof","instanceof","new","delete","void","in","of","super","this","undefined","null","true","false","NaN","Infinity",
        "require","module","exports","__dirname","__filename"
    ];

    // Add a floating button
    const btn = document.createElement('button');
    btn.textContent = "Check JS Undefineds";
    btn.style = "position:fixed;bottom:20px;right:20px;z-index:9999;padding:12px 16px;background:#222;color:#fff;border:none;border-radius:7px;font-size:16px;box-shadow:0 2px 10px #0007;";
    document.body.appendChild(btn);

    btn.onclick = () => {
        // Grab code from all <pre>, <code>, and GitHub diff blocks
        const codeBlocks = Array.from(document.querySelectorAll('pre, code, .blob-code'));
        let results = [];

        codeBlocks.forEach((block, idx) => {
            // Grab lines, ignore empty blocks
            let text = block.innerText;
            if (!text || text.length < 2) return;

            let defined = new Set(CORE);
            let lines = text.split('\n');
            lines.forEach((line, lineNum) => {
                // Simple definition finder
                let defMatch = line.match(/\b(?:var|let|const|function|class)\s+([A-Za-z0-9_$]+)/);
                if (defMatch) defined.add(defMatch[1]);

                // Simple usage finder (words after =, (, ., or whitespace, not quoted)
                let used = Array.from(line.matchAll(/\b([A-Za-z_][$\w]*)\b/g)).map(m=>m[1]);
                used.forEach(word => {
                    // Don't flag if number, in CORE, or just defined
                    if (!defined.has(word) && !/^[0-9]+$/.test(word)) {
                        results.push({
                            word,
                            block: idx+1,
                            line: lineNum+1,
                            code: line.trim()
                        });
                    }
                });
            });
        });

        // Show modal with issues found
        const modal = document.createElement('div');
        modal.style = "position:fixed;top:7%;left:17vw;width:66vw;height:75vh;background:#fafafc;z-index:99999;overflow:auto;padding:24px 16px 12px 32px;border-radius:10px;box-shadow:0 8px 40px #0006;border:2px solid #888;";
        modal.innerHTML = `<h2 style="margin-top:0;">JS Undefineds Finder</h2>
        <button onclick="this.parentElement.remove()" style="position:absolute;top:10px;right:20px;">Close</button>
        ${
          results.length
          ? `<div style="max-height:60vh;overflow:auto;">` +
              results.map(r=>`<b>${r.word}</b> <span style="color:#888;">(block ${r.block}, line ${r.line})</span><br>
              <pre style="margin:3px 0 8px 16px;font-size:13px;color:#356;">${r.code}</pre>`).join("")
            + "</div>"
          : "<p><b>No undefineds found!</b></p>"
        }`;
        document.body.appendChild(modal);
    };

})();
```

---

## **How to Use:**
1. **Copy/paste into Tampermonkey.**
2. **Go to any page with visible JS code blocks** (GitHub PR, Gist, web playground, etc.).
3. **Click the “Check JS Undefineds” button** (bottom-right).  
4. **Get a report** of all *potential* undefined identifiers, line by line.

---

## **Limitations:**
- This is a **super basic, fast & dirty linter**—no full scope/hoisting/context, just top-to-bottom + local definitions.
- Won’t catch *all* JS edge cases (e.g., nested scope, imports, destructuring, etc.), but is powerful for PR/diff spotting and code review!

---

## **Ready for your workflow.**
- Next step?  
  - Want more advanced parsing?
  - Want export/save feature?
  - Want to target *only* GitHub PRs?
  - Or ready for Python/C#/etc. boilerplates?

**Let’s iterate—try it, tell me what you want improved.**  
Onyx is locked and loaded!

**USER**: Would have to Tampermonkey for at work, could gbe avalonia out of work, like with the linter already present in VSCode. I am at work now.