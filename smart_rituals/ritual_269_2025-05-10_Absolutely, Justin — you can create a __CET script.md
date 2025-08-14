# Consolidated Ritual 269

**Date**: 2025-05-10
**Conversation ID**: 386
**Parts Consolidated**: 1
**Content Hash**: d091e96ae6f48a7f784bfae09cbaaa78

---

## COMPLETE CONSOLIDATED RITUAL INSTRUCTIONS

**NO SUMMARIZATION - ALL PARTS COMBINED BELOW**

Absolutely, Justin — you can create a **CET script mod** that hooks into the grenade detonation event and applies a *secondary effect*, like bleeding from the Cutting Grenade, when a **Frag Grenade** explodes. This is very doable with **Cyber Engine Tweaks’ Lua scripting** system.

Here’s a starter **CET Lua script** you can build on:

---

### 🔥 CET Script: Frag Grenades That Also Cut

```lua
registerForEvent("onInit", function()
    print("[FragCutter] Mod Initialized")
end)

registerForEvent("onUpdate", function()
    local player = Game.GetPlayer()
    local weapon = player:GetActiveWeapon()

    -- Monitor thrown grenades (simplified check)
    if weapon and weapon:ToString():find("GrenadeFragRegular") then
        -- Get recently spawned grenades
        local entities = Game.GetTargetingSystem():GetThreats(player, "Grenade", 20)
        for _, grenade in ipairs(entities) do
            local grenadePos = grenade:GetWorldPosition()

            -- Add bleeding effect to NPCs near explosion
            local nearbyNPCs = Game.GetTargetingSystem():GetThreats(grenade, "NPC", 10)
            for _, npc in ipairs(nearbyNPCs) do
                local target = npc:GetObjectToTrack()
                if target then
                    local effect = Game['gameStatusEffectSystem']:ApplyStatusEffect(target, player, "Bleeding", 1.0, 10.0)
                end
            end
        end
    end
end)
```

---

### 🧠 What This Does:

- Checks if the player has a **Frag Grenade** equipped.
- When a frag is thrown and explodes, it:
  - Finds nearby NPCs.
  - Applies the **Bleeding** effect (like the Cutting Grenade would) to each one.

---

### 🛠️ How to Use:

1. **Install Cyber Engine Tweaks**: Make sure it's working and the console is accessible.
2. **Create the Script**:
   - Place the above code in a `.lua` file.
   - Save it to:  
     `Cyberpunk 2077\bin\x64\plugins\cyber_engine_tweaks\mods\FragCutter\init.lua`
3. **Launch the Game** and check your console for `[FragCutter] Mod Initialized`.

---

### ⚠️ Caveats:

- This is a *proof-of-concept*. For exact behavior (like syncing with explosion radius or grenade timers), you’d need to hook into more specific events.
- The “Bleeding” status effect may need fine-tuning or replacement depending on your desired behavior.
- For more dramatic results, you could stack multiple effects (e.g., DoT, knockdown, slow).

---

Would you like me to evolve this into a Nexus-ready CET mod with icons, config, and upgrade path for other grenades (e.g. EMP + Poison hybrids)?