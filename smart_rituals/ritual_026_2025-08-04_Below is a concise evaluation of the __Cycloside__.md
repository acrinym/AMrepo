# Consolidated Ritual 26

**Date**: 2025-08-04
**Conversation ID**: 42
**Parts Consolidated**: 1
**Content Hash**: 97f1b844018e3a4e199f014e1822db23

---

## COMPLETE CONSOLIDATED RITUAL INSTRUCTIONS

**NO SUMMARIZATION - ALL PARTS COMBINED BELOW**

Below is a concise evaluation of the **Cycloside** project along with guidance on its theming/skinning system.  I’ve inspected the code in the repository and relevant Avalonia documentation to ensure the application’s major components are working as intended.

## Overall Status

- **Core functionality** – Cycloside builds a tray‑resident Avalonia application with a **plugin system**, **workspace profiles**, **scripting support**, and an embedded **remote API**.  The core classes (`PluginManager`, `WorkspaceManager`, `SettingsManager`, etc.) are well‑structured, and built‑in plugins (clock, MP3 player, macros, text editor, Jezzball, etc.) are referenced in the `App.axaml.cs` startup.  There is also infrastructure for logging, volatile scripts, hotkeys and auto‑update.  Nothing appears fundamentally broken in code review; however, without running the compiled application it’s not possible to guarantee runtime behaviour.
- **User experience** – The README emphasises that Cycloside targets power users (programmers/hackers), so the UI assumes familiarity with customizing settings and scripting.  It contains helpful features like a plugin manager, macro scheduler and remote API, but there’s no hand‑holding for novices; this aligns with your stated intent.
- **Themes vs. skins** – The theme system is intentionally separate from skins:
  - **Themes** are global resource dictionaries that replace brushes, fonts and styles for the entire application.  They must be placed in `Cycloside/Themes/Global` and given a `.axaml` filename【31101087372415†L17-L34】.  `ThemeManager.LoadGlobalThemeFromSettings()` reads the chosen theme from `settings.json` and applies it at startup.  If no `.axaml` files exist, the drop‑down in the **Theme Settings** window will be empty【345187721066787†L34-L41】.
  - **Skins** are resource dictionaries that apply only to individual windows or controls.  They live in `Cycloside/Skins` and are applied via `SkinManager.ApplySkinTo(element, skinName)`【726233343585835†L17-L36】.  Skins overlay on top of the global theme to tweak a plugin’s appearance.
- **Missing theme/skin files** – The repository currently has **no `.axaml` theme or skin files**, which is why theming appears not to work; the combobox is empty and the default fallback (`MintGreen`) is used.  The docs in `docs/theming-skinning.md` and `theme-example.md` provide an example of how to create a theme file (e.g., define `ThemeBackgroundColor`, `ThemeForegroundColor`, etc.) and save it under `Cycloside/Themes/Global`【579889428145295†L0-L2】【453224110612063†L2-L11】.  Similarly, skins should be saved in `Cycloside/Skins` and referenced in `settings.json` or via the `SkinManager` API【212684984469793†L2-L17】.
- **Plugin integration** – Some plugin windows call `ThemeManager.ApplyComponentTheme` to apply plugin‑specific themes【31101087372415†L110-L137】, but others don’t.  If you want all plugins to respect the selected theme and optional skin, ensure each plugin’s window or UserControl invokes `ThemeManager.ApplyComponentTheme(this, pluginName)` and, if applicable, `SkinManager.ApplySkinTo(this, skinName)` on load.

## Recommendations

1. **Add actual theme and skin files**: Start by creating at least one Avalonia theme file (e.g., `Dark.axaml`) and place it in `Cycloside/Themes/Global`.  Follow Avalonia’s theming docs you linked: define resources like `ThemeBackgroundColor`, `ThemeForegroundColor`, `AccentColor`, and style selectors.  For skins, create `.axaml` files in `Cycloside/Skins` that override specific controls or plugin windows.  After adding these files, they will appear in the Theme Settings window and be selectable.
2. **Wire up plugins**: Audit each plugin’s UI to ensure it calls `ThemeManager.ApplyComponentTheme` and `SkinManager.ApplySkinTo`.  Without these calls, a plugin will not pick up component‑specific themes/skins even after you add them.
3. **Validate settings**: Verify that `settings.json` contains keys such as `"GlobalTheme"` and `"ComponentThemes"` pointing to valid file names.  If the keys are missing or incorrect, the theme manager will fall back to its default and log an error.
4. **Testing**: Build and run the application after adding theme/skin files.  Use the Theme Settings window to switch between themes and confirm that colors and styles update globally.  Apply a skin to a plugin (e.g., the text editor) using `SkinManager.ApplySkinTo` and check that only that control’s appearance changes.

By following these steps, you’ll get the theming/skinning system working as designed.  The underlying architecture of Cycloside appears solid, and once you provide the necessary `.axaml` resources and wire up plugin calls, you should have a fully functional, highly customisable hacker‑friendly tool.