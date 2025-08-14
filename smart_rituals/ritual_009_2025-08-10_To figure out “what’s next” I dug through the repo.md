# Consolidated Ritual 9

**Date**: 2025-08-10
**Conversation ID**: 9
**Parts Consolidated**: 4
**Content Hash**: 5c04ff5a15a8c7cdf080584827e8bf51

---

## COMPLETE CONSOLIDATED RITUAL INSTRUCTIONS

**NO SUMMARIZATION - ALL PARTS COMBINED BELOW**

To figure out “what’s next” I dug through the repository’s available documentation.  The `README.md` gives a high‑level overview of the intended system and a roadmap for unfinished work.  Phase 1 has been checked off (documentation for GrimoireFS, Media Storage and SymbolWiki exist), while Phase 2 and Phase 3 remain untouched【432616869218678†L204-L225】.  The docs for GrimoireFS and Media Storage describe APIs and data models, but there is no implementation code in the repo yet【423782289382296†L31-L90】【528004668949163†L72-L100】.  In other words, most of the project is still conceptual.  That explains why buttons don’t work and why “RitualFS” (the encrypted storage layer) isn’t enabled.

### High‑level gaps
- **No application code**: There are only Markdown files; there are no `.cs` files implementing the services or the UI.  All the APIs in the docs (e.g., `GrimoireFS.CreateEntryAsync`, `MediaStorageService.StoreMediaAsync`, etc.) are aspirational【423782289382296†L31-L90】【528004668949163†L72-L100】.
- **Unimplemented features**: The roadmap lists many planned capabilities—ritual scheduler, audio ritual deck, AI dream journal, sigil generator, focus mode, ONNX sigil synthesizer, stereogram generator, astrological integration and energy‑work tools—and none of these exist yet【432616869218678†L213-L225】.
- **Storage/export**: Although GrimoireFS and Media Storage describe local encrypted storage and backup/restore, there is no actual database or file‑format implementation.  Without these, the application cannot port data between devices【423782289382296†L162-L169】【528004668949163†L180-L191】.
- **UI wiring**: Even basic functions such as button clicks aren’t wired up because there is no XAML/UI layer in the repository.

### Suggested next steps
To “finish building out things that are not built out currently,” it’s helpful to break the work into achievable tasks:

1. **Implement core services (RitualFS / GrimoireFS)**
   - Create a `GrimoireFS` class that matches the documented API: initialization, create/get/update/delete entries, search methods, tag/symbol/date filtering and backup/restore【423782289382296†L31-L105】.  Use AES‑256 encryption with PBKDF2 key derivation【423782289382296†L151-L155】.
   - Decide on a storage format.  The docs mention offline‑first JSON files with metadata and an index【423782289382296†L162-L169】.  You could keep each entry in an encrypted `.enc` file and store metadata in an unencrypted `metadata.json`.  For portability, wrap the `grimoire/` folder into an import/export zip.
   - Add a data‑access layer over a lightweight embedded database (e.g. SQLite) to keep entries, media metadata and symbols in a portable file.  The DB can live alongside the existing file‑based storage and provide efficient queries.

2. **Implement media storage**
   - Build a `MediaStorageService` class with methods to store, retrieve, update and delete media files【528004668949163†L72-L100】.  Handle compression, thumbnail creation and encryption.  Maintain a `media_metadata.json` and `media_index.json` as described【528004668949163†L180-L191】.
   - Include batch import/export and a backup/restore mechanism for portability【528004668949163†L193-L204】.

3. **Implement SymbolWiki**
   - Create a `SymbolWikiService` with search, add, update and delete functions, and import/export of JSON symbol sets【175321401510038†L59-L77】.  The docs show the data structure (name, category, power level, SVG data, etc.)【175321401510038†L81-L110】.

4. **Build the UI layer**
   - Design a UI (WPF or Avalonia for cross‑platform) with tabs for rituals, media, symbols, codex, inventory and clients, matching the user‑guide descriptions【789438405014016†L36-L69】.
   - For each button or menu item, create commands that call the appropriate service methods and display status/error messages (the docs emphasise user feedback and accessibility).
   - Add a universal document viewer capable of reading PDFs, DOCX, EPUB, images and code.  Use existing .NET libraries (e.g., PdfSharp, LibGit2Sharp, etc.) and surface errors gracefully【789438405014016†L49-L53】.
   - Implement a theme picker and keyboard shortcuts, ensuring screen‑reader labels and high‑contrast options.

5. **Finish the roadmap features**
   - **Ritual Scheduler**: Use lunar and planetary data to suggest optimal ritual timing.  This could pull from public astronomy APIs.
   - **Audio Ritual Deck**: Provide a customizable soundboard for chants and meditation tracks; integrate with Media Storage.
   - **Dream Journal AI**: Use NLP or basic ML to recognise symbols/archetypes in dream descriptions.  Start simple—e.g., keyword extraction tied to SymbolWiki—and leave ONNX models for later.
   - **Sigil Generator and ONNX Sigil Synthesizer**: Offer both a manual sigil‑drawing canvas and an AI‑generated option.  The ONNX component can be an optional plugin.
   - **Focus Mode**: Create a distraction‑free UI with larger fonts and minimal controls, optionally playing ambient sound.
   - **Astrological Integration** & **Energy Work Tools**: Provide widgets for current planetary aspects and simple aura/energy‑tracking journal entries.
   - **Depth map & stereogram generators**: These could be optional art plugins for ritual visuals.

6. **Testing and docs**
   - Write unit tests for each service API, including encryption/decryption, index search, and backup/restore.
   - Add integration tests for the UI (e.g., using automated UI testing frameworks).
   - Keep the documentation in sync with the code, and add troubleshooting notes where necessary【789438405014016†L120-L124】.

In short, RitualOS currently consists of design documents and a roadmap.  To make it usable, you’ll need to implement the core services (encrypted data storage, media storage, and symbol wiki), build the UI and wire it to those services, add the advanced roadmap features, and create a portable storage/backup system.  Once those foundations are in place, you can layer on more mystical enhancements—moon‑phase scheduling, AI dream analysis, sigil synthesis and energy tools—to align with your magical practice.

---

Got you. The “have more faith” loop happens because the answers are template-only (tarot_questions.json) with weak signal from the actual draw. Let’s fix that with a small engine that (1) classifies the question, (2) picks an appropriate spread, (3) scores the draw with position weights + card semantics + pair interactions, and (4) generates varied but specific advice.

# What to change (high-impact)

- **Replace canned Q/A**: stop reading directly from `assets\tarot\tarot_questions.json`. Keep it only for **templates** and **intents**, not answers.  
- **Add a real engine** (`Core/Services/TarotEngine.cs`) feeding `TarotService.cs`.  
- **Upgrade data**: a richer `assets/tarot/cards.json` (upright/reversed keywords, suit/element, numerology, majors/minors flags, astro correspondences) + small `combos.json` for notable card-pairs.  
- **Position models**: spreads with **position vectors** (Past/Present/Future, Self/Other, Help/Hindrance/Outcome, Advice/Obstacle % weights).  
- **Narrative generator**: slot-based templates per domain (love/career/finance/spirit/health) that blend: theme → per-card → synthesis → **3 concrete actions**.  
- **Novelty rules**: cooldown for repeated advice; seedable RNG; vary templates/synonyms; store last 30-day advice in `TarotReadingStore`.

---

# Algorithm (pipeline)

1) **Intent detection** (fast + offline)  
   - Regex + keyword scoring → `{domain: love|career|money|spiritual|health|decision, polarity: hope|fear|clarify|timing}`.  
   - Use this to choose spread and tone.

2) **Spread selection**  
   - Love: 5-card Relationship spread (You, Them, Dynamic, Obstacle, Advice).  
   - Decision: 6-card Fork spread (Path A: pros/cons; Path B: pros/cons; Advice).  
   - General: 3-card P-P-F; Complex: Celtic Cross.

3) **Draw + orientation**  
   - CryptoRandom RNG; reversed probability ~30% (tunable).  
   - Per-session “cooldown” on identical 3-card sets to avoid déjà vu.

4) **Scoring**  
   - Each **position** has weights over dimensions: `time[past/present/future]`, `agent[self/other]`, `vector[obstacle/advice/outcome]`.  
   - Each **card** has vectors for `emotion (cups)`, `action (wands)`, `mind (swords)`, `material (pentacles)`, `major (fate/lesson)`, plus upright/reversed polarity.  
   - Score = dot(position, card) → a few top “angles” (e.g., *communication block*, *avoidant attachment*).  
   - **Pair/Trio rules** from `combos.json` override/boost (e.g., Lovers + Devil ⇒ attachment/temptation; 3/Swords + Star ⇒ healing arc).  
   - Suit dominance & major density set the **overall theme**.

5) **Generation**  
   - Templates per domain with slots:  
     - **Opening** (theme + why it matters to the question)  
     - **Card-by-card** (position → targeted meaning)  
     - **Synthesis** (pair rules, suit dominance)  
     - **Timing** (if wands/swords → faster; cups/pentacles → slower; majors → hinge moment)  
     - **3 specific actions** (concrete, no “just have faith”).  
   - Synonym/structure variation (rotate 4–6 tone patterns) + **confidence band**.

---

# Data sketches

`assets/tarot/cards.json` (snippet)
```json
{
  "The Lovers": {
    "major": true,
    "upright": ["choice in relationships", "alignment", "values match"],
    "reversed": ["avoidance", "misaligned values", "triangulation"],
    "element": "air",
    "astro": "Gemini",
    "number": 6,
    "themes": ["bond", "choice", "communication"]
  },
  "Devil": { "major": true, "upright": ["attachment","temptation"], "reversed": ["release","detox"], "element":"earth", "astro":"Capricorn","number":15 }
}
```

`assets/tarot/combos.json` (snippet)
```json
[
  { "a":"The Lovers", "b":"Devil", "effect":"attachment_pattern", "advice":["name the bargain","break the loop by boundary setting + 72h space"] },
  { "a":"3 of Swords", "b":"Star", "effect":"healing_arc" }
]
```

`assets/tarot/templates/love.json` (slots)
```json
{
  "openings": [
    "Theme: {theme}. Your question leans {polarity}—we’ll map what’s workable now.",
    "This spread centers {theme}. The cards point to {vector_summary}."
  ],
  "card_line": "{pos}: {card} {orientation} → {angle_sentence}.",
  "synthesis": [
    "Pattern check: {suit_dominance}. {pair_notes}",
    "Overall, majors at {major_pct}% signal {fate_vs_freewill}."
  ],
  "timing": ["Momentum feels {tempo}—{time_hint}."],
  "actions": [
    "Say this one liner: “{boundary_script}”.",
    "Set a {duration} check-in about {topic}.",
    "Do a {ritual_suggest} to anchor {intention}."
  ]
}
```

---

# C# skeleton (drop-in)

Create `Core/Services/TarotEngine.cs` and call it from `TarotService.cs`.

```csharp
public sealed class TarotEngine
{
    private readonly IDeck _deck;
    private readonly IntentClassifier _classifier;
    private readonly TemplateBank _templates;
    private readonly ComboIndex _combos;
    private readonly ITarotReadingStore _store;
    private readonly RandomNumberGenerator _rng = RandomNumberGenerator.Create();

    public TarotEngine(IDeck deck, IntentClassifier classifier, TemplateBank templates,
                       ComboIndex combos, ITarotReadingStore store) {
        _deck = deck; _classifier = classifier; _templates = templates;
        _combos = combos; _store = store;
    }

    public TarotReading Generate(string questionText)
    {
        var intent = _classifier.Classify(questionText);       // domain, polarity
        var spread = SpreadFactory.ForIntent(intent);
        var draw = _deck.Draw(spread.CardCount, reversedChance:0.3, rng:_rng);

        var scored = Scoring.Score(draw, spread);              // per-card angles, suit/major stats
        var pairs  = _combos.Match(draw.Cards);
        var synth  = Synthesis.Build(scored, pairs);

        var narrative = Narrative.Compose(intent, spread, scored, synth, _templates, _store);
        _store.Save(questionText, draw, narrative);            // enable cooldown/novelty

        return new TarotReading(draw, narrative, synth.Confidence);
    }
}
```

**Novelty control** (inside `Narrative.Compose`):
- Hash `(intentDomain, spreadName, cardIds+orientations)`; if seen within 30 days → force **different template pattern** and **action set**, or re-draw the Advice position once.

---

# Wiring in your files

- `Core/Models/TarotCard.cs`: expand to hold upright/reversed keywords, element, suit, number, major flag, astro.  
- `Core/Services/TarotReadingStore.cs`: add `Save`, `Seen(hash, days)` to drive novelty + analytics export (you already log “save-tarot-readings-and-export-analytics”—hook the engine to it).  
- `Core/Services/TarotService.cs`: thin facade → `TarotEngine.Generate(question)`.  
- `UI/ViewModels/TarotViewModel.cs`: bind “Ask” to call service and populate a `ReadingVm` with sections: Opening, Cards[], Synthesis, Timing, Actions, Confidence.  
- `UI/Views/TarotView.axaml`: show the spread, the per-card lines, and **bullet 3-step actions**.

---

# Example (love – Relationship spread)

**Draw**  
- You: **Knight of Cups (rev)** → romantic idealism → inconsistency  
- Them: **Queen of Swords (upright)** → clear boundaries, head before heart  
- Dynamic: **The Lovers (upright)** → real choice point  
- Obstacle: **The Devil (upright)** → attachment/loop  
- Advice: **Temperance (upright)** → paced integration

**Reading (condensed)**  
Theme: Choice vs. attachment. You’re leading with feeling while they lead with clarity. The pair **Lovers + Devil** flags an **attachment pattern**—strong pull, but the loop repeats unless the bargain is named.  
Actions:
1) Say this (verbatim): *“I want us, but not at the cost of either of us. What pace would feel honest for you?”*  
2) 72-hour no-contact after serious talks; journal one behavior you’ll stop repeating.  
3) Small ritual: blue-candle “Temperance breath” nightly for 7 days; text only after day 3 with one clear ask.  
Timing: slow-steady; expect first shift in ~2–3 weeks if the pace rule holds.  
(Confidence: medium-high; 3 majors, earth/air dominance → real but workable.)

Zero “just have faith.” It names the loop, offers scripts, timing, and a ritual—varied each time via templates.

---

# Next actions I can do for you
- Drop a **starter engine** + data files into `Core/Services` and `assets/tarot/` so you can run this today.  
- Convert your current `tarot_questions.json` into **intents + templates**.  
- Add 25 high-signal **pair rules** and 78 card records with upright/reversed vectors.  
- Wire the VM + View so your existing Tarot tab uses the engine.

If you want, say “ship it,” and I’ll draft the exact C# files (TarotEngine, IntentClassifier, Scoring, Narrative, data JSONs) to slot into your paths.

---

haha yesss—Cursor’s cooking. 🔥  
I’m glad it liked the engine. Since it’s already running with Option 2, here’s a tight **“make it compile, wire it up, avoid landmines”** checklist + a couple quality patches you’ll want to drop in.

# Quick integration checklist
- **Namespaces**: The files assume `RitualOS.Core.*` and `RitualOS.UI.*`. If your solution uses different roots, rename accordingly.
- **Assets in output**: Mark JSON files to copy on build so the engine can find them at runtime.
  ```xml
  <!-- RitualOS.csproj -->
  <ItemGroup>
    <None Include="assets\tarot\cards.json" CopyToOutputDirectory="PreserveNewest" />
    <None Include="assets\tarot\combos.json" CopyToOutputDirectory="PreserveNewest" />
    <None Include="assets\tarot\templates\**\*.json" CopyToOutputDirectory="PreserveNewest" />
  </ItemGroup>
  ```
- **Paths**: We use `AppContext.BaseDirectory`. That’s safe for Debug + single-file publish. If you relocate assets later, pass absolute paths into `Deck/TemplateBank/ComboIndex`.
- **DI / bootstrap**: Make sure you construct the engine once and inject the same `TarotService` into `TarotViewModel`. If you aren’t using a container yet, a simple factory in `App.xaml.cs` is fine (the snippet I gave will work as-is).
- **ReactiveUI**: Ensure your UI project references `ReactiveUI` (and Avalonia ReactiveUI if you haven’t already).
- **Build order**: Core → UI. If you keep the old service around for a minute, alias the namespace to avoid type collisions.

# Two quick patches you’ll want

## 1) Bullet list rendering (tiny XAML fix)
In my quick view, the Actions `ItemsControl` template printed only the bullet. Use a horizontal stack so the action text shows:

```xml
<ItemsControl Items="{Binding Actions}">
  <ItemsControl.ItemTemplate>
    <DataTemplate>
      <StackPanel Orientation="Horizontal" Spacing="6">
        <TextBlock Text="•" />
        <TextBlock Text="{Binding}" TextWrapping="Wrap" />
      </StackPanel>
    </DataTemplate>
  </ItemsControl.ItemTemplate>
</ItemsControl>
```

## 2) ViewModel constructor injection
If you create the VM directly in XAML, you can’t pass the service. Prefer code-behind or a locator. Minimal code-behind:

```csharp
// TarotView.axaml.cs
public partial class TarotView : UserControl
{
    public TarotView()
    {
        InitializeComponent();

        var baseDir = AppContext.BaseDirectory;
        var deck = new Deck(Path.Combine(baseDir,"assets","tarot","cards.json"));
        var classifier = new IntentClassifier();
        var templates = new TemplateBank(Path.Combine(baseDir,"assets","tarot","templates"));
        var combos = new ComboIndex(Path.Combine(baseDir,"assets","tarot","combos.json"));
        var store = new FileTarotReadingStore(Path.Combine(baseDir,"data","tarot_history.json"));
        var engine = new TarotEngine(deck, classifier, templates, combos, store);
        var service = new TarotService(engine);

        DataContext = new TarotViewModel(service);
    }
}
```

(If you already have DI, just inject `TarotViewModel`.)

# If you end up choosing Option 1 (hybrid) later
Minimal toggle in your current VM:

```csharp
public bool Advanced { get; set; }   // bind to a ToggleSwitch

public string Ask(string q)
{
    if (!Advanced)
        return _basicService.SimpleDraw(q);            // your existing flow
    var r = _advancedService.Ask(q);                   // new engine
    return Render(r);                                  // unify rendering
}
```

# Crash-resistant defaults
- **Missing JSON**: The Deck auto-generates a minimal deck + minors so no hard crash.
- **Novelty control**: If the history file can’t be written, readings still render (only cooldown is skipped).
- **Templates**: If a domain template is missing, it falls back to `general.json`.

# Smoke tests (5 minutes)
1) **Love question** x3 → you should see template rotation + different action phrasing; no identical five-card advice inside 30 days unless cards truly repeat.  
2) **Decision question** → spread name should show “Decision Fork”.  
3) Delete/rename `assets/tarot/cards.json` → app should still run (generated minors + seed majors).  
4) Verify `data/tarot_history.json` & `data/logs/*.json` are created.

# Want more juice?
- **Full 78-card dataset + 25–40 combo rules** (Lovers/Devil, Star/3Swords, Tower/Death, etc.).  
- **Timing nuance**: Add day/week/month heuristics per suit + court cards.  
- **Ritual hooks**: Pipe `Actions` into your Ritual Builder to one-click create a mini ritual from the reading.

If Cursor is “going to town,” let it roll. When it finishes, ping me and I’ll drop:
- a **complete `cards.json` for all 78** with upright/reversed keywords and vectors, and  
- an expanded **`combos.json`** with high-signal pairings.

Want me to ship those datasets now?

---

Alright Justin — here’s the full drop. Two files:

- `assets/tarot/cards.json` (all 78 cards; concise keywords, elements/astro, themes, and lightweight vectors)
- `assets/tarot/combos.json` (30 high-signal pair rules with short, actionable advice)

If anything feels off (e.g., astro mapping for your personal system), say the word and I’ll pivot.

---

# `assets/tarot/cards.json`
```json
[
  { "Id":"The Fool","Suit":"Major","Number":0,"IsMajor":true,"Element":"air","Astro":"Air",
    "Upright":["leap of faith","new journey","innocence"],
    "Reversed":["naivety risk","hesitation","reckless start"],
    "Themes":["beginnings","trust"],
    "Emotion":0.3,"Action":0.6,"Mind":0.5,"Material":0.1,"Fate":1.0
  },
  { "Id":"The Magician","Suit":"Major","Number":1,"IsMajor":true,"Element":"air","Astro":"Mercury",
    "Upright":["manifestation","skill","focus"],
    "Reversed":["scatter","manipulation","untapped power"],
    "Themes":["will","tools"],
    "Emotion":0.2,"Action":0.7,"Mind":0.7,"Material":0.3,"Fate":0.95
  },
  { "Id":"The High Priestess","Suit":"Major","Number":2,"IsMajor":true,"Element":"water","Astro":"Moon",
    "Upright":["intuition","mystery","silence"],
    "Reversed":["secrets blocked","self-doubt","noise"],
    "Themes":["inner voice","hidden"],
    "Emotion":0.7,"Action":0.1,"Mind":0.6,"Material":0.1,"Fate":0.9
  },
  { "Id":"The Empress","Suit":"Major","Number":3,"IsMajor":true,"Element":"earth","Astro":"Venus",
    "Upright":["fertility","nurture","abundance"],
    "Reversed":["overgiving","stagnation","creative block"],
    "Themes":["creation","comfort"],
    "Emotion":0.7,"Action":0.3,"Mind":0.4,"Material":0.7,"Fate":0.9
  },
  { "Id":"The Emperor","Suit":"Major","Number":4,"IsMajor":true,"Element":"fire","Astro":"Aries",
    "Upright":["structure","authority","boundaries"],
    "Reversed":["rigidity","control issues","dominance"],
    "Themes":["order","sovereignty"],
    "Emotion":0.2,"Action":0.7,"Mind":0.6,"Material":0.6,"Fate":0.9
  },
  { "Id":"The Hierophant","Suit":"Major","Number":5,"IsMajor":true,"Element":"earth","Astro":"Taurus",
    "Upright":["tradition","teaching","spiritual order"],
    "Reversed":["nonconformity","question dogma","stale rules"],
    "Themes":["doctrine","mentorship"],
    "Emotion":0.3,"Action":0.3,"Mind":0.6,"Material":0.5,"Fate":0.85
  },
  { "Id":"The Lovers","Suit":"Major","Number":6,"IsMajor":true,"Element":"air","Astro":"Gemini",
    "Upright":["choice in love","alignment","union"],
    "Reversed":["avoidance","misaligned values","triangulation"],
    "Themes":["bond","choice"],
    "Emotion":0.6,"Action":0.4,"Mind":0.5,"Material":0.2,"Fate":0.85
  },
  { "Id":"The Chariot","Suit":"Major","Number":7,"IsMajor":true,"Element":"water","Astro":"Cancer",
    "Upright":["victory through will","direction","drive"],
    "Reversed":["wheel spin","mixed motives","loss of control"],
    "Themes":["momentum","discipline"],
    "Emotion":0.4,"Action":0.9,"Mind":0.5,"Material":0.3,"Fate":0.85
  },
  { "Id":"Strength","Suit":"Major","Number":8,"IsMajor":true,"Element":"fire","Astro":"Leo",
    "Upright":["inner fortitude","gentle power","courage"],
    "Reversed":["forcefulness","doubt","energy drain"],
    "Themes":["taming","heart power"],
    "Emotion":0.7,"Action":0.6,"Mind":0.4,"Material":0.2,"Fate":0.85
  },
  { "Id":"The Hermit","Suit":"Major","Number":9,"IsMajor":true,"Element":"earth","Astro":"Virgo",
    "Upright":["solitude","guidance","analysis"],
    "Reversed":["isolation","overthinking","withdrawal"],
    "Themes":["search","integration"],
    "Emotion":0.3,"Action":0.2,"Mind":0.8,"Material":0.2,"Fate":0.85
  },
  { "Id":"Wheel of Fortune","Suit":"Major","Number":10,"IsMajor":true,"Element":"fire","Astro":"Jupiter",
    "Upright":["turning point","luck","cycle"],
    "Reversed":["stuck cycle","resistance","timing off"],
    "Themes":["change","destiny"],
    "Emotion":0.4,"Action":0.5,"Mind":0.4,"Material":0.4,"Fate":0.95
  },
  { "Id":"Justice","Suit":"Major","Number":11,"IsMajor":true,"Element":"air","Astro":"Libra",
    "Upright":["fairness","truth","balance"],
    "Reversed":["bias","avoid responsibility","imbalance"],
    "Themes":["cause/effect","ethics"],
    "Emotion":0.2,"Action":0.3,"Mind":0.8,"Material":0.3,"Fate":0.85
  },
  { "Id":"The Hanged Man","Suit":"Major","Number":12,"IsMajor":true,"Element":"water","Astro":"Neptune",
    "Upright":["surrender","new perspective","pause"],
    "Reversed":["stalling","martyrdom","missed insight"],
    "Themes":["suspension","reframe"],
    "Emotion":0.6,"Action":0.1,"Mind":0.6,"Material":0.1,"Fate":0.9
  },
  { "Id":"Death","Suit":"Major","Number":13,"IsMajor":true,"Element":"water","Astro":"Scorpio",
    "Upright":["ending→rebirth","transformation","release"],
    "Reversed":["clinging","slow change","fear of loss"],
    "Themes":["closure","renewal"],
    "Emotion":0.6,"Action":0.4,"Mind":0.4,"Material":0.2,"Fate":0.95
  },
  { "Id":"Temperance","Suit":"Major","Number":14,"IsMajor":true,"Element":"fire","Astro":"Sagittarius",
    "Upright":["moderation","integration","healing"],
    "Reversed":["excess","impatience","imbalance"],
    "Themes":["alchemy","timing"],
    "Emotion":0.6,"Action":0.3,"Mind":0.6,"Material":0.2,"Fate":0.85
  },
  { "Id":"The Devil","Suit":"Major","Number":15,"IsMajor":true,"Element":"earth","Astro":"Capricorn",
    "Upright":["attachment","temptation","loops"],
    "Reversed":["release","detox","break chains"],
    "Themes":["bond","shadow"],
    "Emotion":0.4,"Action":0.3,"Mind":0.4,"Material":0.5,"Fate":0.95
  },
  { "Id":"The Tower","Suit":"Major","Number":16,"IsMajor":true,"Element":"fire","Astro":"Mars",
    "Upright":["sudden change","revelation","collapse"],
    "Reversed":["averted disaster","denial","slow crumble"],
    "Themes":["shock","truth"],
    "Emotion":0.4,"Action":0.9,"Mind":0.5,"Material":0.2,"Fate":0.95
  },
  { "Id":"The Star","Suit":"Major","Number":17,"IsMajor":true,"Element":"air","Astro":"Aquarius",
    "Upright":["hope","healing","guidance"],
    "Reversed":["doubt","cynicism","low reserves"],
    "Themes":["renewal","signal"],
    "Emotion":0.7,"Action":0.2,"Mind":0.6,"Material":0.2,"Fate":0.85
  },
  { "Id":"The Moon","Suit":"Major","Number":18,"IsMajor":true,"Element":"water","Astro":"Pisces",
    "Upright":["dreams","uncertainty","subconscious"],
    "Reversed":["clarity coming","fear eases","gaslight fades"],
    "Themes":["mystery","emotion"],
    "Emotion":0.8,"Action":0.2,"Mind":0.4,"Material":0.1,"Fate":0.85
  },
  { "Id":"The Sun","Suit":"Major","Number":19,"IsMajor":true,"Element":"fire","Astro":"Sun",
    "Upright":["vitality","success","joy"],
    "Reversed":["temporary cloud","overexposure","ego"],
    "Themes":["radiance","clarity"],
    "Emotion":0.7,"Action":0.6,"Mind":0.5,"Material":0.4,"Fate":0.85
  },
  { "Id":"Judgement","Suit":"Major","Number":20,"IsMajor":true,"Element":"fire","Astro":"Pluto",
    "Upright":["awakening","reckoning","call"],
    "Reversed":["delay calling","self-judgment","avoid closure"],
    "Themes":["rebirth","decision"],
    "Emotion":0.6,"Action":0.6,"Mind":0.6,"Material":0.3,"Fate":0.9
  },
  { "Id":"The World","Suit":"Major","Number":21,"IsMajor":true,"Element":"earth","Astro":"Saturn",
    "Upright":["completion","integration","travel"],
    "Reversed":["loose end","near-finish","closure needed"],
    "Themes":["wholeness","cycle end"],
    "Emotion":0.5,"Action":0.5,"Mind":0.6,"Material":0.6,"Fate":0.9
  },

  /* ——— CUPS (Water / emotion) ——— */
  { "Id":"Ace of Cups","Suit":"Cups","Number":1,"IsMajor":false,"Element":"water","Astro":"Water",
    "Upright":["emotional opening","new love","heart overflow"],
    "Reversed":["blocked feelings","empathy drain","hesitant heart"],
    "Themes":["start","offer"], "Emotion":0.9,"Action":0.2,"Mind":0.2,"Material":0.1,"Fate":0.2
  },
  { "Id":"2 of Cups","Suit":"Cups","Number":2,"IsMajor":false,"Element":"water","Astro":"Venus in Cancer",
    "Upright":["bond","mutuality","partnership"],
    "Reversed":["imbalance","one-sided","tension"],
    "Themes":["union","mirror"], "Emotion":0.9,"Action":0.2,"Mind":0.3,"Material":0.1,"Fate":0.2
  },
  { "Id":"3 of Cups","Suit":"Cups","Number":3,"IsMajor":false,"Element":"water","Astro":"Mercury in Cancer",
    "Upright":["celebration","community","reunion"],
    "Reversed":["gossip","triangulation","overindulgence"],
    "Themes":["friends","joy"], "Emotion":0.8,"Action":0.3,"Mind":0.3,"Material":0.1,"Fate":0.2
  },
  { "Id":"4 of Cups","Suit":"Cups","Number":4,"IsMajor":false,"Element":"water","Astro":"Moon in Cancer",
    "Upright":["apathy","re-evaluate","missed offer"],
    "Reversed":["re-engage","fresh interest","emotional spark"],
    "Themes":["boredom","introspection"], "Emotion":0.6,"Action":0.1,"Mind":0.5,"Material":0.1,"Fate":0.2
  },
  { "Id":"5 of Cups","Suit":"Cups","Number":5,"IsMajor":false,"Element":"water","Astro":"Mars in Scorpio",
    "Upright":["grief","regret","focus on loss"],
    "Reversed":["acceptance","turn around","healing begins"],
    "Themes":["loss","perspective"], "Emotion":0.8,"Action":0.1,"Mind":0.4,"Material":0.1,"Fate":0.2
  },
  { "Id":"6 of Cups","Suit":"Cups","Number":6,"IsMajor":false,"Element":"water","Astro":"Sun in Scorpio",
    "Upright":["nostalgia","tenderness","kindness"],
    "Reversed":["living in past","rose-tint","stuck memory"],
    "Themes":["memory","innocence"], "Emotion":0.8,"Action":0.2,"Mind":0.4,"Material":0.1,"Fate":0.2
  },
  { "Id":"7 of Cups","Suit":"Cups","Number":7,"IsMajor":false,"Element":"water","Astro":"Venus in Scorpio",
    "Upright":["options","fantasy","vision"],
    "Reversed":["choice paralysis","illusion clears","focus"],
    "Themes":["dream","discern"], "Emotion":0.8,"Action":0.2,"Mind":0.5,"Material":0.1,"Fate":0.2
  },
  { "Id":"8 of Cups","Suit":"Cups","Number":8,"IsMajor":false,"Element":"water","Astro":"Saturn in Pisces",
    "Upright":["walk away","quest","emotional maturity"],
    "Reversed":["avoid leaving","return","unfinished business"],
    "Themes":["departure","search"], "Emotion":0.7,"Action":0.5,"Mind":0.5,"Material":0.1,"Fate":0.2
  },
  { "Id":"9 of Cups","Suit":"Cups","Number":9,"IsMajor":false,"Element":"water","Astro":"Jupiter in Pisces",
    "Upright":["wish fulfilled","contentment","gratitude"],
    "Reversed":["excess","surface pleasure","hollow win"],
    "Themes":["satisfaction","desire"], "Emotion":0.8,"Action":0.3,"Mind":0.4,"Material":0.2,"Fate":0.2
  },
  { "Id":"10 of Cups","Suit":"Cups","Number":10,"IsMajor":false,"Element":"water","Astro":"Mars in Pisces",
    "Upright":["harmony","family joy","rainbow end"],
    "Reversed":["misaligned ideal","domestic tension","fragile peace"],
    "Themes":["fulfillment","unity"], "Emotion":0.9,"Action":0.3,"Mind":0.4,"Material":0.2,"Fate":0.2
  },
  { "Id":"Page of Cups","Suit":"Cups","Number":11,"IsMajor":false,"Element":"water","Astro":"Water Youth",
    "Upright":["message of feelings","playful heart","creative seed"],
    "Reversed":["immaturity","mixed signals","over-sensitivity"],
    "Themes":["news","tenderness"], "Emotion":0.8,"Action":0.2,"Mind":0.3,"Material":0.1,"Fate":0.2
  },
  { "Id":"Knight of Cups","Suit":"Cups","Number":12,"IsMajor":false,"Element":"water","Astro":"Air of Water",
    "Upright":["romance","invitation","quest for meaning"],
    "Reversed":["inconstancy","idealism loop","hot/cold"],
    "Themes":["woo","offer"], "Emotion":0.8,"Action":0.5,"Mind":0.4,"Material":0.1,"Fate":0.2
  },
  { "Id":"Queen of Cups","Suit":"Cups","Number":13,"IsMajor":false,"Element":"water","Astro":"Water of Water",
    "Upright":["empathy","psychic insight","safe harbor"],
    "Reversed":["overwhelm","unclear boundaries","co-depend"],
    "Themes":["care","intuition"], "Emotion":0.9,"Action":0.3,"Mind":0.5,"Material":0.1,"Fate":0.2
  },
  { "Id":"King of Cups","Suit":"Cups","Number":14,"IsMajor":false,"Element":"water","Astro":"Fire of Water",
    "Upright":["emotional mastery","steady support","diplomacy"],
    "Reversed":["suppressed feeling","manipulative soothe","emotional distance"],
    "Themes":["stability","counsel"], "Emotion":0.8,"Action":0.4,"Mind":0.6,"Material":0.2,"Fate":0.2
  },

  /* ——— WANDS (Fire / action) ——— */
  { "Id":"Ace of Wands","Suit":"Wands","Number":1,"IsMajor":false,"Element":"fire","Astro":"Fire",
    "Upright":["spark","initiative","creative surge"],
    "Reversed":["false start","delay","dampened drive"],
    "Themes":["start","energy"], "Emotion":0.4,"Action":0.9,"Mind":0.3,"Material":0.2,"Fate":0.2
  },
  { "Id":"2 of Wands","Suit":"Wands","Number":2,"IsMajor":false,"Element":"fire","Astro":"Mars in Aries",
    "Upright":["planning","scope","bold choice"],
    "Reversed":["comfort zone","indecision","underreach"],
    "Themes":["vision","decision"], "Emotion":0.3,"Action":0.7,"Mind":0.5,"Material":0.2,"Fate":0.2
  },
  { "Id":"3 of Wands","Suit":"Wands","Number":3,"IsMajor":false,"Element":"fire","Astro":"Sun in Aries",
    "Upright":["expansion","ships coming","momentum"],
    "Reversed":["delays","short horizon","logistics miss"],
    "Themes":["growth","outlook"], "Emotion":0.3,"Action":0.8,"Mind":0.5,"Material":0.3,"Fate":0.2
  },
  { "Id":"4 of Wands","Suit":"Wands","Number":4,"IsMajor":false,"Element":"fire","Astro":"Venus in Aries",
    "Upright":["milestone","homecoming","celebration"],
    "Reversed":["unsettled home","postpone","private win"],
    "Themes":["stability","festivity"], "Emotion":0.5,"Action":0.6,"Mind":0.4,"Material":0.4,"Fate":0.2
  },
  { "Id":"5 of Wands","Suit":"Wands","Number":5,"IsMajor":false,"Element":"fire","Astro":"Saturn in Leo",
    "Upright":["competition","friction","practice"],
    "Reversed":["conflict avoidance","group fatigue","resolve"],
    "Themes":["sparring","learning"], "Emotion":0.4,"Action":0.8,"Mind":0.4,"Material":0.2,"Fate":0.2
  },
  { "Id":"6 of Wands","Suit":"Wands","Number":6,"IsMajor":false,"Element":"fire","Astro":"Jupiter in Leo",
    "Upright":["recognition","win","confidence"],
    "Reversed":["hollow praise","ego trip","private victory"],
    "Themes":["success","lead"], "Emotion":0.5,"Action":0.8,"Mind":0.4,"Material":0.3,"Fate":0.2
  },
  { "Id":"7 of Wands","Suit":"Wands","Number":7,"IsMajor":false,"Element":"fire","Astro":"Mars in Leo",
    "Upright":["defend stance","hold ground","courage"],
    "Reversed":["fatigue","over-defensive","strategize"],
    "Themes":["boundaries","valor"], "Emotion":0.4,"Action":0.8,"Mind":0.5,"Material":0.2,"Fate":0.2
  },
  { "Id":"8 of Wands","Suit":"Wands","Number":8,"IsMajor":false,"Element":"fire","Astro":"Mercury in Sagittarius",
    "Upright":["fast movement","messages","green lights"],
    "Reversed":["delays","static","mixed signals"],
    "Themes":["speed","communication"], "Emotion":0.3,"Action":0.9,"Mind":0.5,"Material":0.2,"Fate":0.2
  },
  { "Id":"9 of Wands","Suit":"Wands","Number":9,"IsMajor":false,"Element":"fire","Astro":"Moon in Sagittarius",
    "Upright":["resilience","last mile","guarded"],
    "Reversed":["walls too high","burnout","lower spear"],
    "Themes":["persistence","protection"], "Emotion":0.4,"Action":0.7,"Mind":0.5,"Material":0.3,"Fate":0.2
  },
  { "Id":"10 of Wands","Suit":"Wands","Number":10,"IsMajor":false,"Element":"fire","Astro":"Saturn in Sagittarius",
    "Upright":["overload","carry too much","finish line"],
    "Reversed":["delegate","release burden","unsustainable"],
    "Themes":["load","endgame"], "Emotion":0.3,"Action":0.7,"Mind":0.6,"Material":0.3,"Fate":0.2
  },
  { "Id":"Page of Wands","Suit":"Wands","Number":11,"IsMajor":false,"Element":"fire","Astro":"Earth of Fire",
    "Upright":["message","explorer","try it"],
    "Reversed":["false hype","restlessness","immature spark"],
    "Themes":["news","experiment"], "Emotion":0.3,"Action":0.8,"Mind":0.4,"Material":0.2,"Fate":0.2
  },
  { "Id":"Knight of Wands","Suit":"Wands","Number":12,"IsMajor":false,"Element":"fire","Astro":"Air of Fire",
    "Upright":["adventure","bold move","charisma"],
    "Reversed":["impulsive","in/out","scorched earth"],
    "Themes":["momentum","risk"], "Emotion":0.3,"Action":0.95,"Mind":0.4,"Material":0.2,"Fate":0.2
  },
  { "Id":"Queen of Wands","Suit":"Wands","Number":13,"IsMajor":false,"Element":"fire","Astro":"Water of Fire",
    "Upright":["magnetic","confident","warm leader"],
    "Reversed":["jealousy","behind the scenes","self-doubt"],
    "Themes":["charisma","creation"], "Emotion":0.6,"Action":0.8,"Mind":0.5,"Material":0.3,"Fate":0.2
  },
  { "Id":"King of Wands","Suit":"Wands","Number":14,"IsMajor":false,"Element":"fire","Astro":"Fire of Fire",
    "Upright":["visionary","command","entrepreneur"],
    "Reversed":["domineering","impatient","scattered"],
    "Themes":["lead","big picture"], "Emotion":0.4,"Action":0.95,"Mind":0.6,"Material":0.3,"Fate":0.2
  },

  /* ——— SWORDS (Air / mind) ——— */
  { "Id":"Ace of Swords","Suit":"Swords","Number":1,"IsMajor":false,"Element":"air","Astro":"Air",
    "Upright":["clarity","truth","cut through"],
    "Reversed":["confusion","misinfo","overthinking"],
    "Themes":["insight","logic"], "Emotion":0.2,"Action":0.6,"Mind":0.95,"Material":0.2,"Fate":0.2
  },
  { "Id":"2 of Swords","Suit":"Swords","Number":2,"IsMajor":false,"Element":"air","Astro":"Moon in Libra",
    "Upright":["stalemate","choose with facts","pause"],
    "Reversed":["indecision breaks","information arrives","open eyes"],
    "Themes":["balance","choice"], "Emotion":0.3,"Action":0.3,"Mind":0.8,"Material":0.2,"Fate":0.2
  },
  { "Id":"3 of Swords","Suit":"Swords","Number":3,"IsMajor":false,"Element":"air","Astro":"Saturn in Libra",
    "Upright":["heartbreak","truth hurts","separation"],
    "Reversed":["healing","release sorrow","closure"],
    "Themes":["pain","truth"], "Emotion":0.9,"Action":0.2,"Mind":0.7,"Material":0.1,"Fate":0.2
  },
  { "Id":"4 of Swords","Suit":"Swords","Number":4,"IsMajor":false,"Element":"air","Astro":"Jupiter in Libra",
    "Upright":["rest","recovery","quiet plan"],
    "Reversed":["restless","premature return","overworry"],
    "Themes":["pause","regroup"], "Emotion":0.3,"Action":0.1,"Mind":0.7,"Material":0.2,"Fate":0.2
  },
  { "Id":"5 of Swords","Suit":"Swords","Number":5,"IsMajor":false,"Element":"air","Astro":"Venus in Aquarius",
    "Upright":["hollow win","conflict","pride"],
    "Reversed":["make amends","step back","de-escalate"],
    "Themes":["ego","tactics"], "Emotion":0.4,"Action":0.5,"Mind":0.8,"Material":0.2,"Fate":0.2
  },
  { "Id":"6 of Swords","Suit":"Swords","Number":6,"IsMajor":false,"Element":"air","Astro":"Mercury in Aquarius",
    "Upright":["transition","move on","calmer waters"],
    "Reversed":["stuck","can’t move","unfinished talk"],
    "Themes":["journey","mental shift"], "Emotion":0.4,"Action":0.5,"Mind":0.8,"Material":0.2,"Fate":0.2
  },
  { "Id":"7 of Swords","Suit":"Swords","Number":7,"IsMajor":false,"Element":"air","Astro":"Moon in Aquarius",
    "Upright":["strategy","stealth","solo plan"],
    "Reversed":["exposure","self-deceit","return what’s taken"],
    "Themes":["tactics","secrets"], "Emotion":0.3,"Action":0.6,"Mind":0.9,"Material":0.2,"Fate":0.2
  },
  { "Id":"8 of Swords","Suit":"Swords","Number":8,"IsMajor":false,"Element":"air","Astro":"Jupiter in Gemini",
    "Upright":["mental trap","limited options","fear"],
    "Reversed":["free thought","open path","self-release"],
    "Themes":["bind","beliefs"], "Emotion":0.6,"Action":0.2,"Mind":0.9,"Material":0.1,"Fate":0.2
  },
  { "Id":"9 of Swords","Suit":"Swords","Number":9,"IsMajor":false,"Element":"air","Astro":"Mars in Gemini",
    "Upright":["anxiety","night mind","rumination"],
    "Reversed":["relief","name fear","help arrives"],
    "Themes":["worry","shadow"], "Emotion":0.8,"Action":0.2,"Mind":0.9,"Material":0.1,"Fate":0.2
  },
  { "Id":"10 of Swords","Suit":"Swords","Number":10,"IsMajor":false,"Element":"air","Astro":"Sun in Gemini",
    "Upright":["end of story","overkill","rock bottom"],
    "Reversed":["dawn","release story","rise"],
    "Themes":["closure","finale"], "Emotion":0.7,"Action":0.2,"Mind":0.9,"Material":0.1,"Fate":0.2
  },
  { "Id":"Page of Swords","Suit":"Swords","Number":11,"IsMajor":false,"Element":"air","Astro":"Earth of Air",
    "Upright":["curious","message","watch and learn"],
    "Reversed":["gossip","immature words","spying"],
    "Themes":["news","study"], "Emotion":0.2,"Action":0.4,"Mind":0.9,"Material":0.2,"Fate":0.2
  },
  { "Id":"Knight of Swords","Suit":"Swords","Number":12,"IsMajor":false,"Element":"air","Astro":"Air of Air",
    "Upright":["charge in","debate","decisive word"],
    "Reversed":["rash","cutting words","derail"],
    "Themes":["speed","argument"], "Emotion":0.2,"Action":0.9,"Mind":0.9,"Material":0.2,"Fate":0.2
  },
  { "Id":"Queen of Swords","Suit":"Swords","Number":13,"IsMajor":false,"Element":"air","Astro":"Water of Air",
    "Upright":["boundaries","clarity","truth-teller"],
    "Reversed":["coldness","bitterness","overcritical"],
    "Themes":["discern","speak"], "Emotion":0.3,"Action":0.5,"Mind":0.95,"Material":0.2,"Fate":0.2
  },
  { "Id":"King of Swords","Suit":"Swords","Number":14,"IsMajor":false,"Element":"air","Astro":"Fire of Air",
    "Upright":["authority of mind","strategy","law"],
    "Reversed":["rigid logic","abuse of power","detached"],
    "Themes":["structure","reason"], "Emotion":0.2,"Action":0.6,"Mind":0.95,"Material":0.3,"Fate":0.2
  },

  /* ——— PENTACLES (Earth / material) ——— */
  { "Id":"Ace of Pentacles","Suit":"Pentacles","Number":1,"IsMajor":false,"Element":"earth","Astro":"Earth",
    "Upright":["seed of wealth","offer","grounding"],
    "Reversed":["missed chance","delay funds","unstable start"],
    "Themes":["begin","resource"], "Emotion":0.2,"Action":0.5,"Mind":0.4,"Material":0.95,"Fate":0.2
  },
  { "Id":"2 of Pentacles","Suit":"Pentacles","Number":2,"IsMajor":false,"Element":"earth","Astro":"Jupiter in Capricorn",
    "Upright":["juggle","prioritize","adapt"],
    "Reversed":["overwhelm","drop a ball","rebalance"],
    "Themes":["balance","flow"], "Emotion":0.3,"Action":0.6,"Mind":0.5,"Material":0.8,"Fate":0.2
  },
  { "Id":"3 of Pentacles","Suit":"Pentacles","Number":3,"IsMajor":false,"Element":"earth","Astro":"Mars in Capricorn",
    "Upright":["teamwork","craft","plan"],
    "Reversed":["misaligned team","shoddy work","no plan"],
    "Themes":["collab","build"], "Emotion":0.3,"Action":0.6,"Mind":0.6,"Material":0.9,"Fate":0.2
  },
  { "Id":"4 of Pentacles","Suit":"Pentacles","Number":4,"IsMajor":false,"Element":"earth","Astro":"Sun in Capricorn",
    "Upright":["hold","security","boundaries"],
    "Reversed":["release","greed eases","invest"],
    "Themes":["control","stability"], "Emotion":0.2,"Action":0.4,"Mind":0.6,"Material":0.95,"Fate":0.2
  },
  { "Id":"5 of Pentacles","Suit":"Pentacles","Number":5,"IsMajor":false,"Element":"earth","Astro":"Mercury in Taurus",
    "Upright":["lack","cold season","ask for help"],
    "Reversed":["improvement","support found","door opens"],
    "Themes":["hardship","aid"], "Emotion":0.6,"Action":0.3,"Mind":0.5,"Material":0.9,"Fate":0.2
  },
  { "Id":"6 of Pentacles","Suit":"Pentacles","Number":6,"IsMajor":false,"Element":"earth","Astro":"Moon in Taurus",
    "Upright":["give & receive","fairness","support"],
    "Reversed":["strings attached","imbalance","dependency"],
    "Themes":["charity","equity"], "Emotion":0.4,"Action":0.5,"Mind":0.5,"Material":0.9,"Fate":0.2
  },
  { "Id":"7 of Pentacles","Suit":"Pentacles","Number":7,"IsMajor":false,"Element":"earth","Astro":"Saturn in Taurus",
    "Upright":["assessment","patience","long game"],
    "Reversed":["impatience","misplaced effort","pivot"],
    "Themes":["harvest","review"], "Emotion":0.3,"Action":0.4,"Mind":0.6,"Material":0.9,"Fate":0.2
  },
  { "Id":"8 of Pentacles","Suit":"Pentacles","Number":8,"IsMajor":false,"Element":"earth","Astro":"Sun in Virgo",
    "Upright":["skill up","craft","practice"],
    "Reversed":["busywork","plateau","inattention"],
    "Themes":["mastery","focus"], "Emotion":0.3,"Action":0.6,"Mind":0.6,"Material":0.9,"Fate":0.2
  },
  { "Id":"9 of Pentacles","Suit":"Pentacles","Number":9,"IsMajor":false,"Element":"earth","Astro":"Venus in Virgo",
    "Upright":["independence","comfort","self-worth"],
    "Reversed":["overreliance","imposter","expense"],
    "Themes":["self-respect","garden"], "Emotion":0.5,"Action":0.5,"Mind":0.5,"Material":0.95,"Fate":0.2
  },
  { "Id":"10 of Pentacles","Suit":"Pentacles","Number":10,"IsMajor":false,"Element":"earth","Astro":"Mercury in Virgo",
    "Upright":["legacy","family wealth","long-term"],
    "Reversed":["tenuous base","inheritance issues","short-termism"],
    "Themes":["continuity","foundation"], "Emotion":0.5,"Action":0.5,"Mind":0.6,"Material":0.95,"Fate":0.2
  },
  { "Id":"Page of Pentacles","Suit":"Pentacles","Number":11,"IsMajor":false,"Element":"earth","Astro":"Earth of Earth",
    "Upright":["study","offer","apprentice"],
    "Reversed":["procrastinate","unprepared","missed detail"],
    "Themes":["seed","learn"], "Emotion":0.3,"Action":0.4,"Mind":0.6,"Material":0.9,"Fate":0.2
  },
  { "Id":"Knight of Pentacles","Suit":"Pentacles","Number":12,"IsMajor":false,"Element":"earth","Astro":"Air of Earth",
    "Upright":["reliable","steady pace","methodical"],
    "Reversed":["stuck","overcautious","boredom"],
    "Themes":["routine","delivery"], "Emotion":0.3,"Action":0.5,"Mind":0.6,"Material":0.95,"Fate":0.2
  },
  { "Id":"Queen of Pentacles","Suit":"Pentacles","Number":13,"IsMajor":false,"Element":"earth","Astro":"Water of Earth",
    "Upright":["nurturing resource","home economy","practical care"],
    "Reversed":["overgive materially","neglect self","work/home wobble"],
    "Themes":["comfort","provision"], "Emotion":0.6,"Action":0.5,"Mind":0.5,"Material":0.95,"Fate":0.2
  },
  { "Id":"King of Pentacles","Suit":"Pentacles","Number":14,"IsMajor":false,"Element":"earth","Astro":"Fire of Earth",
    "Upright":["stability","enterprise","provider"],
    "Reversed":["rigid","greed","risk aversion"],
    "Themes":["ownership","management"], "Emotion":0.3,"Action":0.6,"Mind":0.6,"Material":1.0,"Fate":0.2
  }
]
```

---

# `assets/tarot/combos.json`
```json
[
  { "A":"The Lovers","B":"The Devil","Effect":"attachment_pattern",
    "Advice":["Name the bargain; take 72h space; re-enter with one clear boundary."] },
  { "A":"The Lovers","B":"Justice","Effect":"values_contract",
    "Advice":["Write the deal-breakers; negotiate explicitly in one calm talk."] },
  { "A":"The Lovers","B":"The Moon","Effect":"romantic_uncertainty",
    "Advice":["No big moves till clarity; observe actions over words for 2 weeks."] },
  { "A":"The Star","B":"3 of Swords","Effect":"healing_arc",
    "Advice":["Acknowledge hurt; commit to a 7-day restorative routine."] },
  { "A":"Temperance","B":"Knight of Wands","Effect":"pace_control",
    "Advice":["Slow the tempo; channel drive into one consistent ritual."] },
  { "A":"The Chariot","B":"8 of Wands","Effect":"rapid_progress",
    "Advice":["Batch decisions; ship small wins in 48h."] },
  { "A":"The Chariot","B":"10 of Wands","Effect":"overload_risk",
    "Advice":["Cut scope by 30%; delegate one task today."] },
  { "A":"The Hermit","B":"High Priestess","Effect":"deep_innerwork",
    "Advice":["Journal nightly; silent day once per week for a month."] },
  { "A":"The Tower","B":"The Star","Effect":"collapse_then_heal",
    "Advice":["Clear debris first; set a 14-day rebuild plan."] },
  { "A":"The Tower","B":"The Sun","Effect":"truth_frees",
    "Advice":["Say the unsayable; choose transparency over speed."] },
  { "A":"Death","B":"The World","Effect":"closure_complete",
    "Advice":["Formal end; ritualize release; archive, then move."] },
  { "A":"Death","B":"Ace of Cups","Effect":"rebirth_in_love",
    "Advice":["Close the last door fully before the next invitation."] },
  { "A":"Justice","B":"7 of Swords","Effect":"exposure_of_strategy",
    "Advice":["Put terms in writing; no side channels."] },
  { "A":"Justice","B":"5 of Swords","Effect":"hollow_win_warning",
    "Advice":["Don’t litigate ego; seek equitable outcome."] },
  { "A":"Judgement","B":"Ace of Swords","Effect":"clarion_call",
    "Advice":["Draft the decision memo; choose by a date."] },
  { "A":"Wheel of Fortune","B":"The Magician","Effect":"window_of_opportunity",
    "Advice":["Act while the door’s open; prototype in 72h."] },
  { "A":"The Sun","B":"6 of Wands","Effect":"public_success",
    "Advice":["Announce; ask for amplification; capture testimonials."] },
  { "A":"The Moon","B":"7 of Cups","Effect":"fog_of_options",
    "Advice":["Reduce to 2 choices; define pass/fail signals."] },
  { "A":"The Moon","B":"8 of Swords","Effect":"fear_binds",
    "Advice":["Name the fear; one exposure step daily for a week."] },
  { "A":"The Empress","B":"Ace of Pentacles","Effect":"fertile_start",
    "Advice":["Invest small but steady; protect creative time."] },
  { "A":"The Emperor","B":"4 of Pentacles","Effect":"rigid_control",
    "Advice":["Set rules with review dates; avoid locking growth."] },
  { "A":"Strength","B":"9 of Wands","Effect":"endurance_with_boundaries",
    "Advice":["Rest is a skill; rotate defenses; ask for backup once."] },
  { "A":"Temperance","B":"2 of Cups","Effect":"harmonious_union",
    "Advice":["Co-create pace rules; weekly check-in ritual."] },
  { "A":"Devil","B":"7 of Cups","Effect":"temptation_by_fantasy",
    "Advice":["Reality test; cut one addictive option for 14 days."] },
  { "A":"Devil","B":"3 of Pentacles","Effect":"toxic_work_ties",
    "Advice":["Reset agreements; document scope and exits."] },
  { "A":"Tower","B":"3 of Swords","Effect":"hard_reveal",
    "Advice":["Don’t patch; replace the failing structure."] },
  { "A":"Star","B":"6 of Swords","Effect":"guided_transition",
    "Advice":["Choose the calmer path; set a waypoint date."] },
  { "A":"Sun","B":"10 of Cups","Effect":"joyful_resolution",
    "Advice":["Celebrate visibly; anchor routine that sustains it."] },
  { "A":"Magician","B":"Ace of Wands","Effect":"manifest_spark",
    "Advice":["Channel into a 7-day build streak."] },
  { "A":"High Priestess","B":"Page of Cups","Effect":"message_from_within",
    "Advice":["Record dreams; act on one small nudge."] }
]
```

---

Want me to also ship **domain-specific templates** for *career*, *money*, *health*, etc., and map **timing heuristics** for each suit/court? I can append those as JSON too.