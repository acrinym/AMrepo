# Consolidated Ritual 169

**Date**: 2025-06-13
**Conversation ID**: 246
**Parts Consolidated**: 2
**Content Hash**: 366d28520d7f6e878918955232f8b239

---

## COMPLETE CONSOLIDATED RITUAL INSTRUCTIONS

**NO SUMMARIZATION - ALL PARTS COMBINED BELOW**

Oh, hell yes—**that’s the spirit of Compiz**! The "Explode" effect, where a window shatters into fragments and flies apart, is iconic. Doing this in Avalonia is possible, but it’ll take some creative rendering. Here’s exactly **how you’d prototype it** as a plugin or effect in Cycloside, step by step (plus some sample code to get you started):

---

# **How the Explode Effect Works (Concept)**

1. **Capture the window as a bitmap** (texture).
2. **Divide it into fragments** (rectangular or polygonal pieces).
3. **Animate each piece outward** along randomized (or physics-driven) paths—rotation, translation, maybe even scaling.
4. **Render these fragments** over the old window position, while hiding the original window.
5. **Optionally, add sound, particles, or fading.**
6. **When done, close the window for real** (or restore it if canceled).

---

# **Avalonia Feasibility**
- **You CAN** capture visuals of a window/widget via [RenderTargetBitmap](https://docs.avaloniaui.net/docs/controls/bitmap).
- **You CAN** animate custom-drawn fragments in an overlay window or canvas.
- **You MAY need** a “topmost” overlay control layered above the actual window, to show the effect as it closes.

---

# **Minimal Example: Exploding Window Effect in Avalonia**

Below is a skeleton of how you’d do it. This assumes you have a trigger (say, the window is being closed or a “projectile” hits it).

## **Step 1: Capture the Window as a Bitmap**

```csharp
public async Task<RenderTargetBitmap> CaptureWindowAsync(Window window)
{
    var pixelSize = new PixelSize((int)window.Width, (int)window.Height);
    var dpi = window.PlatformImpl?.DesktopScaling ?? 1;
    var bmp = new RenderTargetBitmap(pixelSize);
    await bmp.RenderAsync(window);
    return bmp;
}
```

## **Step 2: Split Into Pieces**

For simplicity, split into rectangles:

```csharp
public List<Rect> GetFragments(int rows, int cols, double width, double height)
{
    var fragments = new List<Rect>();
    double w = width / cols, h = height / rows;
    for (int x = 0; x < cols; x++)
        for (int y = 0; y < rows; y++)
            fragments.Add(new Rect(x * w, y * h, w, h));
    return fragments;
}
```

## **Step 3: Animate Pieces**

You’ll need a container (e.g., a transparent `Window` or `Canvas`) that renders each fragment as a `CroppedBitmap` and animates its position/rotation.

```csharp
public class ExplodeFragment
{
    public CroppedBitmap FragmentBitmap { get; set; }
    public Point Start { get; set; }
    public Vector Velocity { get; set; }
    public double Rotation { get; set; }
    public double RotationSpeed { get; set; }
    public double Time { get; set; }
}
```

- On each frame (e.g., via a timer), update position:  
  `fragment.Start += fragment.Velocity * deltaTime;`
  `fragment.Rotation += fragment.RotationSpeed * deltaTime;`

## **Step 4: Show Overlay & Hide Window**

- Make the original window invisible.
- Show an always-on-top borderless transparent window above it, rendering fragments.
- Animate fragments for 0.5–2 seconds.

## **Step 5: Sample Rendering Loop**

Use a `DrawingContext` or override a `Control`'s `OnRender`:

```csharp
public override void Render(DrawingContext context)
{
    foreach (var frag in Fragments)
    {
        using (context.PushPostTransform(Matrix.CreateRotationAt(frag.Rotation, frag.Center)))
        {
            context.DrawImage(frag.FragmentBitmap, 1, frag.DestRect, frag.SourceRect);
        }
    }
}
```

---

# **Wiring Up: Triggering the Effect**

- Hook the window close event, or a custom "hit" event (from your projectile logic).
- Call `CaptureWindowAsync`, set up your overlay window and fragments, hide the real window.
- After animation, call `Close()` on the original window.

---

## **Sample Usage in a Plugin**

Here’s a very rough sketch (not full code, just the sequence):

```csharp
// On projectile hit or close request:
var bmp = await CaptureWindowAsync(myWindow);
var pieces = GetFragments(8, 8, myWindow.Width, myWindow.Height); // 8x8 grid
var fragments = CreateExplodeFragments(bmp, pieces); // setup velocities, etc.
ShowExplodeOverlay(fragments); // starts animation
myWindow.Hide();
await AnimateFragmentsAsync(fragments); // async loop 1s
myWindow.Close();
```

---

# **For Next-Level Polish**

- Use physics (gravity, random velocities, friction).
- Vary piece sizes and shapes (triangles, polygons).
- Add sound (glass breaking).
- Add particle effects (dust, sparkles).
- Allow the effect to be triggered by “external events”—e.g., if you ever want to build “shoot your desktop” fun!

---

# **Want a Drop-in Prototype?**

If you want, I can generate a plug-and-play Avalonia UserControl or Window that does this “explosion” animation, ready to trigger. Let me know if you want:
- Full C# sample class?
- Avalonia XAML with code-behind for easy use?
- Or a full Cycloside plugin template?

---

**This is the kind of thing that makes Cycloside cooler than Rainmeter. Let’s make windows explode! Want a full working code drop for this?**

---

You’re right, it’s the **exact same merge conflict pattern** as before—just with a different branch (looks like you were working on “modify-previewwindow-to-load-xaml-string” this time). This happens *constantly* if:

- You have multiple branches or PRs that each touch the `.csproj` dependencies,
- You merge or rebase frequently,
- Or you’re doing changes on two machines and not rebasing/pulling before new work.

---

## **Why Does This Keep Happening?**

`.csproj` files are super merge-conflict-prone because:
- NuGet dependency lists are long and any line change can make Git see a “diff”.
- Most merge tools are dumb about XML (so duplicate lines appear after merges).
- When multiple people (or you, on two branches) add/modify packages, Git can’t always figure out what you want.

---

## **How To Fix This (Again, But Fast):**

**You must:**  
1. Delete all the `<<<<<<<`, `=======`, `>>>>>>>` lines,
2. Manually combine the dependencies you actually need (keep *all* unique ones, pick package versions as desired),
3. Save, build, and commit.

---

## **Your Cleaned Up/Combined `.csproj` (unique packages from both sides):**

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <BuiltInComInteropSupport>true</BuiltInComInteropSupport>
    <ApplicationManifest>app.manifest</ApplicationManifest>
    <AvaloniaUseCompiledBindingsByDefault>true</AvaloniaUseCompiledBindingsByDefault>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Avalonia" Version="11.3.1" />
    <PackageReference Include="Avalonia.Desktop" Version="11.3.1" />
    <PackageReference Include="Avalonia.Themes.Fluent" Version="11.3.1" />
    <PackageReference Include="Avalonia.Fonts.Inter" Version="11.3.1" />
    <PackageReference Include="NAudio" Version="2.2.1" />
    <PackageReference Include="MoonSharp" Version="2.0.0" />
    <PackageReference Include="Microsoft.CodeAnalysis.CSharp" Version="4.9.2" />
    <!-- Use the latest needed for AvaloniaEdit -->
    <PackageReference Include="AvaloniaEdit" Version="1.1.0" />
    <PackageReference Include="Avalonia.Controls.DataGrid" Version="11.3.1" />
    <PackageReference Include="Avalonia.Controls.HotKeys" Version="1.0.0" />
    <PackageReference Include="CliWrap" Version="3.7.0" /> <!-- prefer latest -->
    <PackageReference Include="System.CommandLine" Version="2.0.0-beta4.22272.1" />
    <PackageReference Include="Avalonia.Controls.Notifications" Version="11.3.0" />
    <PackageReference Include="Avalonia.Diagnostics" Version="11.3.1">
      <IncludeAssets Condition="'$(Configuration)' != 'Debug'">None</IncludeAssets>
      <PrivateAssets Condition="'$(Configuration)' != 'Debug'">All</PrivateAssets>
    </PackageReference>
    <PackageReference Include="SharpHook" Version="5.0.0" />
    <PackageReference Include="CommunityToolkit.Mvvm" Version="8.2.0" />
  </ItemGroup>

  <!-- Exclude built-in plugins to simplify build in this environment -->
  <!--
  <ItemGroup>
    <Compile Remove="Plugins/BuiltIn/**" />
  </ItemGroup>
  -->

</Project>
```

**Key points:**
- Combined all *unique* dependencies.
- Picked the newest version where there was a difference (e.g., `AvaloniaEdit` 1.1.0 and `CliWrap` 3.7.0).
- All plugin exclusion is still commented out.

---

## **How To Avoid This in the Future**

- **Pull and rebase** your feature branches before starting new package changes.
- **Centralize package additions**: add NuGet packages only in `main` (or only in a dev branch), then rebase feature branches on top of that.
- **Use [dotnet-outdated](https://github.com/dotnet-outdated/dotnet-outdated) or Dependabot** to keep deps fresh and prevent old packages from lingering.

---

**TL;DR:**  
This keeps happening because of parallel edits to dependencies in branches—totally normal in active projects!  
Just keep cleaning up the `.csproj`, and maybe coordinate package additions in one place.

---

Want this as a file or need a quick script to auto-clean future merge conflicts? Just ask!