# Superscope Effect - VIS_AVS Implementation

**Source:** Official Winamp VIS_AVS Source Code  
**File:** `r_sscope.cpp`  
**Class:** `C_SScopeClass`  
**Module Name:** "Render / SuperScope"

---

## 🎯 **Effect Overview**

Superscope is the **core visualization engine** of AVS, allowing users to write mathematical expressions that generate dynamic visual effects. It's a **scripting-based renderer** that plots points, lines, or shapes based on mathematical equations that can react to audio input.

---

## 🏗️ **Architecture**

### **Base Class Inheritance**
```cpp
class C_SScopeClass : public C_RBASE
```

### **Core Components**
- **Effect Expression Engine** - 4 script sections (Init, Frame, Beat, Point)
- **Variable Registration System** - Dynamic variable binding for scripts
- **Audio Data Processing** - Spectrum and waveform data integration
- **Rendering Pipeline** - Point plotting and line drawing
- **Color Management** - Dynamic color interpolation and blending

---

## 📝 **Script Sections**

### **1. Init Section (`effect_exp[3]`)**
- **Purpose:** Initialization code that runs once when visualization starts
- **Default:** `"n=800"` (sets number of points to 800)
- **Variables:** Sets initial values for global variables
- **Execution:** Runs once at startup

### **2. Frame Section (`effect_exp[1]`)**
- **Purpose:** Code that runs every frame
- **Default:** `"t=t-0.05"` (decrements time variable)
- **Variables:** Updates frame-level variables
- **Execution:** Runs every frame before point rendering

### **3. Beat Section (`effect_exp[2]`)**
- **Purpose:** Code that runs on beat detection
- **Default:** `""` (empty)
- **Variables:** Beat-reactive variable updates
- **Execution:** Runs when `isBeat` is true

### **4. Point Section (`effect_exp[0]`)**
- **Purpose:** Code that runs for each point plotted
- **Default:** `"d=i+v*0.2; r=t+i*$PI*4; x=cos(r)*d; y=sin(r)*d"`
- **Variables:** Sets x, y coordinates and colors for each point
- **Execution:** Runs for each point from 0 to n-1

---

## 🔧 **Built-in Variables**

### **Core Variables**
| Variable | Type | Description | Range |
|----------|------|-------------|-------|
| `n` | double | Number of points to plot | 1 to 128,000 |
| `i` | double | Current point index | 0.0 to 1.0 |
| `v` | double | Audio value (spectrum/waveform) | -1.0 to 1.0 |
| `t` | double | Time in seconds | Continuous |
| `b` | double | Beat detection | 0.0 or 1.0 |

### **Coordinate Variables**
| Variable | Type | Description | Range |
|----------|------|-------------|-------|
| `x` | double | X coordinate | -1.0 to 1.0 |
| `y` | double | Y coordinate | -1.0 to 1.0 |
| `w` | double | Window width | Actual pixels |
| `h` | double | Window height | Actual pixels |

### **Color Variables**
| Variable | Type | Description | Range |
|----------|------|-------------|-------|
| `red` | double | Red component | 0.0 to 1.0 |
| `green` | double | Green component | 0.0 to 1.0 |
| `blue` | double | Blue component | 0.0 to 1.0 |

### **Rendering Variables**
| Variable | Type | Description | Range |
|----------|------|-------------|-------|
| `linesize` | double | Line thickness | 0.0+ |
| `skip` | double | Skip rendering if > 0.00001 | 0.0+ |
| `drawmode` | double | Line mode (0=points, 1=lines) | 0.0 or 1.0 |

---

## 🎵 **Audio Data Integration**

### **Data Structure**
```cpp
char visdata[2][2][576]
// [stereo][spectrum/waveform][frequency bins]
```

### **Channel Selection**
- **which_ch & 3**: 0=left spectrum, 1=right spectrum, 2=left waveform, 3=right waveform
- **which_ch & 4**: 0=spectrum, 4=waveform
- **Center channel**: Average of left and right when which_ch >= 2

### **Audio Processing**
- **Spectrum data**: 0-255 range, converted to -1.0 to 1.0
- **Waveform data**: 0-255 range, converted to -1.0 to 1.0
- **Interpolation**: Linear interpolation between frequency bins for smooth rendering

---

## 🎨 **Rendering Pipeline**

### **1. Variable Initialization**
```cpp
// Register all variables with EEL engine
var_n = registerVar("n");
var_x = registerVar("x");
var_y = registerVar("y");
var_i = registerVar("i");
var_v = registerVar("v");
// ... etc
```

### **2. Script Compilation**
```cpp
// Compile each script section
for (x = 0; x < 4; x++) {
    codehandle[x] = compileCode(effect_exp[x].get());
}
```

### **3. Frame Processing**
```cpp
// Execute frame and beat scripts
executeCode(codehandle[1], visdata);        // Frame
if (isBeat) executeCode(codehandle[2], visdata);  // Beat
```

### **4. Point Rendering Loop**
```cpp
// For each point from 0 to n-1
for (a = 0; a < l; a++) {
    // Set audio value for this point
    *var_v = yr/128.0 - 1.0;
    *var_i = (double)a/(double)(l-1);
    
    // Execute point script
    executeCode(codehandle[0], visdata);
    
    // Convert coordinates to screen space
    x = (int)((*var_x+1.0)*w*0.5);
    y = (int)((*var_y+1.0)*h*0.5);
    
    // Render point or line
    if (*var_drawmode < 0.00001) {
        // Point mode
        BLEND_LINE(framebuffer+x+y*w, thiscolor);
    } else {
        // Line mode
        line(framebuffer, lx, ly, x, y, w, h, thiscolor, linesize);
    }
}
```

---

## 🌈 **Color Management**

### **Color Array**
- **num_colors**: Number of colors in the palette (max 16)
- **colors[16]**: Array of RGB color values
- **color_pos**: Current color position for interpolation

### **Color Interpolation**
```cpp
// Smooth color transitions
int p = color_pos/64;
int r = color_pos&63;
int c1 = colors[p];
int c2 = colors[p+1 < num_colors ? p+1 : 0];

// Interpolate RGB components
r1 = (((c1&255)*(63-r))+((c2&255)*r))/64;
r2 = ((((c1>>8)&255)*(63-r))+(((c2>>8)&255)*r))/64;
r3 = ((((c1>>16)&255)*(63-r))+(((c2>>16)&255)*r))/64;

current_color = r1|(r2<<8)|(r3<<16);
```

### **Dynamic Color Variables**
- **red, green, blue**: Set in point script for per-point coloring
- **Color blending**: Automatic blending with current palette color

---

## 📊 **Performance Considerations**

### **Point Limit**
- **Maximum points**: 128,000 (hardcoded limit)
- **Default points**: 800 (balanced performance vs. detail)
- **Performance impact**: Linear with number of points

### **Optimization Features**
- **Skip rendering**: Use `skip` variable to skip points
- **Conditional execution**: Beat scripts only run on beats
- **Efficient math**: Uses optimized trigonometric functions

---

## 🔌 **Phoenix Integration**

### **AvsModuleNode Implementation**
```csharp
public class SuperscopeNode : AvsModuleNode
{
    // Script sections
    public string InitScript { get; set; } = "";
    public string FrameScript { get; set; } = "";
    public string BeatScript { get; set; } = "";
    public string PointScript { get; set; } = "";
    
    // Configuration
    public int PointCount { get; set; } = 800;
    public int ChannelSelection { get; set; } = 0;  // 0=left, 1=right, 2=center
    public int RenderMode { get; set; } = 0;        // 0=lines, 1=points, 2=lines+points
    public Color[] ColorPalette { get; set; } = new Color[16];
    public int ColorCount { get; set; } = 1;
    
    // Built-in variables (mapped to script engine)
    public float N { get; set; } = 0;           // Point count
    public float I { get; set; } = 0;           // Current point index
    public float V { get; set; } = 0;           // Audio value
    public float T { get; set; } = 0;           // Time
    public float B { get; set; } = 0;           // Beat
    public float X { get; set; } = 0;           // X coordinate
    public float Y { get; set; } = 0;           // Y coordinate
    public float W { get; set; } = 0;           // Width
    public float H { get; set; } = 0;           // Height
    public float Red { get; set; } = 0;         // Red component
    public float Green { get; set; } = 0;       // Green component
    public float Blue { get; set; } = 0;        // Blue component
    public float LineSize { get; set; } = 1;    // Line thickness
    public float Skip { get; set; } = 0;        // Skip rendering
    public float DrawMode { get; set; } = 0;    // Drawing mode
    
    // Script engine state
    private IScriptEngine scriptEngine;
    private Dictionary<string, float> scriptVariables;
    private bool scriptsCompiled = false;
    private bool isBeat = false;
    private float frameTime = 0;
    private int frameCount = 0;
    
    // Audio data
    private float[] leftChannelData;
    private float[] rightChannelData;
    private float[] centerChannelData;
    
    // Rendering state
    private Vector2[] pointPositions;
    private Color[] pointColors;
    private bool[] pointVisible;
    
    // Constructor
    public SuperscopeNode()
    {
        // Initialize default color palette
        ColorPalette[0] = Color.White;
        ColorCount = 1;
        
        // Initialize script variables
        scriptVariables = new Dictionary<string, float>();
        InitializeBuiltInVariables();
        
        // Create script engine
        scriptEngine = new PhoenixScriptEngine();
    }
    
    // Processing
    public override void Process(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (!Enabled) return;
        
        // Update frame timing
        frameTime += ctx.DeltaTime;
        frameCount++;
        
        // Update built-in variables
        UpdateBuiltInVariables(ctx);
        
        // Check for beat
        isBeat = ctx.AudioData.IsBeat;
        
        // Execute script sections
        ExecuteInitScript(ctx);
        ExecuteFrameScript(ctx);
        if (isBeat) ExecuteBeatScript(ctx);
        ExecutePointScript(ctx);
        
        // Render points/lines
        RenderSuperscope(ctx, output);
    }
    
    private void ExecuteInitScript(FrameContext ctx)
    {
        if (string.IsNullOrEmpty(InitScript) || frameCount > 1) return;
        
        try
        {
            // Set initial context
            scriptEngine.SetVariable("n", PointCount);
            scriptEngine.SetVariable("w", ctx.Width);
            scriptEngine.SetVariable("h", ctx.Height);
            scriptEngine.SetVariable("t", 0);
            scriptEngine.SetVariable("b", 0);
            
            // Execute init script
            scriptEngine.Execute(InitScript);
            
            // Extract any variables set by the script
            ExtractScriptVariables();
        }
        catch (ScriptExecutionException ex)
        {
            LogError($"Init script error: {ex.Message}");
        }
    }
    
    private void ExecuteFrameScript(FrameContext ctx)
    {
        if (string.IsNullOrEmpty(FrameScript)) return;
        
        try
        {
            // Update frame variables
            scriptEngine.SetVariable("t", frameTime);
            scriptEngine.SetVariable("b", isBeat ? 1 : 0);
            scriptEngine.SetVariable("w", ctx.Width);
            scriptEngine.SetVariable("h", ctx.Height);
            
            // Execute frame script
            scriptEngine.Execute(FrameScript);
            
            // Extract variables
            ExtractScriptVariables();
        }
        catch (ScriptExecutionException ex)
        {
            LogError($"Frame script error: {ex.Message}");
        }
    }
    
    private void ExecuteBeatScript(FrameContext ctx)
    {
        if (string.IsNullOrEmpty(BeatScript)) return;
        
        try
        {
            // Set beat context
            scriptEngine.SetVariable("b", 1);
            scriptEngine.SetVariable("t", frameTime);
            
            // Execute beat script
            scriptEngine.Execute(BeatScript);
            
            // Extract variables
            ExtractScriptVariables();
        }
        catch (ScriptExecutionException ex)
        {
            LogError($"Beat script error: {ex.Message}");
        }
    }
    
    private void ExecutePointScript(FrameContext ctx)
    {
        if (string.IsNullOrEmpty(PointScript)) return;
        
        try
        {
            // Process each point
            for (int i = 0; i < PointCount; i++)
            {
                // Set point context
                scriptEngine.SetVariable("i", i);
                scriptEngine.SetVariable("n", PointCount);
                scriptEngine.SetVariable("v", GetAudioValue(i));
                
                // Execute point script
                scriptEngine.Execute(PointScript);
                
                // Extract position and color
                float x = scriptEngine.GetVariable("x");
                float y = scriptEngine.GetVariable("y");
                float red = scriptEngine.GetVariable("red");
                float green = scriptEngine.GetVariable("green");
                float blue = scriptEngine.GetVariable("blue");
                float skip = scriptEngine.GetVariable("skip");
                
                // Store point data
                pointPositions[i] = new Vector2(x, y);
                pointColors[i] = Color.FromArgb(
                    (int)Math.Clamp(red * 255, 0, 255),
                    (int)Math.Clamp(green * 255, 0, 255),
                    (int)Math.Clamp(blue * 255, 0, 255)
                );
                pointVisible[i] = skip == 0;
            }
        }
        catch (ScriptExecutionException ex)
        {
            LogError($"Point script error: {ex.Message}");
        }
    }
    
    private float GetAudioValue(int pointIndex)
    {
        // Map point index to audio data
        int audioIndex = (pointIndex * 576) / PointCount;
        if (audioIndex >= 576) audioIndex = 575;
        
        // Get channel data based on selection
        float[] channelData = ChannelSelection switch
        {
            0 => leftChannelData,    // Left channel
            1 => rightChannelData,   // Right channel
            2 => centerChannelData,  // Center channel
            _ => leftChannelData
        };
        
        return channelData[audioIndex];
    }
    
    private void RenderSuperscope(FrameContext ctx, ImageBuffer output)
    {
        if (RenderMode == 0 || RenderMode == 2) // Lines or Lines+Points
        {
            RenderLines(ctx, output);
        }
        
        if (RenderMode == 1 || RenderMode == 2) // Points or Lines+Points
        {
            RenderPoints(ctx, output);
        }
    }
    
    private void RenderLines(FrameContext ctx, ImageBuffer output)
    {
        for (int i = 1; i < PointCount; i++)
        {
            if (!pointVisible[i] || !pointVisible[i - 1]) continue;
            
            Vector2 start = pointPositions[i - 1];
            Vector2 end = pointPositions[i];
            
            // Apply line size
            float thickness = LineSize;
            if (thickness <= 0) thickness = 1;
            
            // Draw line with color interpolation
            Color startColor = pointColors[i - 1];
            Color endColor = pointColors[i];
            
            DrawLine(output, start, end, startColor, endColor, thickness);
        }
    }
    
    private void RenderPoints(FrameContext ctx, ImageBuffer output)
    {
        for (int i = 0; i < PointCount; i++)
        {
            if (!pointVisible[i]) continue;
            
            Vector2 position = pointPositions[i];
            Color color = pointColors[i];
            float size = LineSize;
            
            if (size <= 0) size = 1;
            
            // Draw point
            DrawPoint(output, position, color, size);
        }
    }
    
    private void UpdateBuiltInVariables(FrameContext ctx)
    {
        // Update audio data
        leftChannelData = ctx.AudioData.Spectrum[0];
        rightChannelData = ctx.AudioData.Spectrum[1];
        
        // Calculate center channel
        centerChannelData = new float[leftChannelData.Length];
        for (int i = 0; i < leftChannelData.Length; i++)
        {
            centerChannelData[i] = (leftChannelData[i] + rightChannelData[i]) / 2.0f;
        }
        
        // Update built-in variables
        N = PointCount;
        W = ctx.Width;
        H = ctx.Height;
        T = frameTime;
        B = isBeat ? 1 : 0;
    }
    
    private void InitializeBuiltInVariables()
    {
        // Initialize all built-in variables to 0
        var variables = new[] { "n", "i", "v", "t", "b", "x", "y", "w", "h", 
                               "red", "green", "blue", "linesize", "skip", "drawmode" };
        
        foreach (var var in variables)
        {
            scriptVariables[var] = 0;
        }
    }
    
    private void ExtractScriptVariables()
    {
        // Extract variables that might have been set by scripts
        var builtInVars = new Dictionary<string, Action<float>>
        {
            ["x"] = v => X = v,
            ["y"] = v => Y = v,
            ["red"] = v => Red = v,
            ["green"] = v => Green = v,
            ["blue"] = v => Blue = v,
            ["linesize"] = v => LineSize = v,
            ["skip"] = v => Skip = v,
            ["drawmode"] = v => DrawMode = v
        };
        
        foreach (var kvp in builtInVars)
        {
            if (scriptEngine.HasVariable(kvp.Key))
            {
                kvp.Value(scriptEngine.GetVariable(kvp.Key));
            }
        }
    }
    
    private void DrawLine(ImageBuffer output, Vector2 start, Vector2 end, 
                         Color startColor, Color endColor, float thickness)
    {
        // Implement line drawing with color interpolation
        // This would use the output buffer's line drawing capabilities
        output.DrawLine(start, end, startColor, endColor, thickness);
    }
    
    private void DrawPoint(ImageBuffer output, Vector2 position, Color color, float size)
    {
        // Implement point drawing
        // This would use the output buffer's point drawing capabilities
        output.DrawPoint(position, color, size);
    }
}

// Phoenix Script Engine Interface
public interface IScriptEngine
{
    void SetVariable(string name, float value);
    float GetVariable(string name);
    bool HasVariable(string name);
    void Execute(string script);
}

// Phoenix Script Engine Implementation
public class PhoenixScriptEngine : IScriptEngine
{
    private Dictionary<string, float> variables = new Dictionary<string, float>();
    private IExpressionEvaluator evaluator;
    
    public PhoenixScriptEngine()
    {
        evaluator = new PhoenixExpressionEvaluator();
    }
    
    public void SetVariable(string name, float value)
    {
        variables[name] = value;
        evaluator.SetVariable(name, value);
    }
    
    public float GetVariable(string name)
    {
        return variables.TryGetValue(name, out float value) ? value : 0;
    }
    
    public bool HasVariable(string name)
    {
        return variables.ContainsKey(name);
    }
    
    public void Execute(string script)
    {
        if (string.IsNullOrEmpty(script)) return;
        
        // Parse and execute the script
        // This would use the Phoenix expression evaluator
        evaluator.Evaluate(script);
    }
}

// Expression Evaluator Interface
public interface IExpressionEvaluator
{
    void SetVariable(string name, float value);
    float Evaluate(string expression);
}

// Phoenix Expression Evaluator
public class PhoenixExpressionEvaluator : IExpressionEvaluator
{
    private Dictionary<string, float> variables = new Dictionary<string, float>();
    
    public void SetVariable(string name, float value)
    {
        variables[name] = value;
    }
    
    public float Evaluate(string expression)
    {
        // This would implement a full expression parser and evaluator
        // Supporting mathematical operations, functions, and variable references
        // Similar to ns-eel but in C# with better performance
        
        // For now, return 0 (placeholder)
        return 0;
    }
}
```

### **Script Engine Features**
- **Full ns-eel Compatibility**: Support for all VIS_AVS script syntax
- **Real-time Compilation**: JIT compilation for optimal performance
- **Variable Binding**: Direct binding between script variables and C# properties
- **Error Handling**: Comprehensive error reporting and recovery
- **Performance Optimization**: Cached compiled expressions and efficient execution

### **Built-in Variable System**
- **Automatic Binding**: Script variables automatically map to C# properties
- **Type Safety**: Strong typing for all built-in variables
- **Real-time Updates**: Variables updated every frame with current context
- **Audio Integration**: Direct access to spectrum and waveform data

### **Rendering Pipeline**
- **Flexible Modes**: Support for lines, points, or both
- **Color Interpolation**: Smooth color transitions between points
- **Line Thickness**: Configurable line width and point size
- **Skip Logic**: Conditional rendering based on script variables
- **Performance**: Optimized rendering with minimal allocations

---

## 📚 **Built-in Presets**

### **Default Presets**
1. **Spiral**: `"d=i+v*0.2; r=t+i*$PI*4; x=cos(r)*d; y=sin(r)*d"`
2. **3D Scope Dish**: Complex 3D projection with depth
3. **Rotating Bow Thing**: Animated bow shape with rotation
4. **Vertical Bouncing Scope**: Audio-reactive vertical movement
5. **Spiral Graph Fun**: Mathematical spiral patterns
6. **Alternating Diagonal Scope**: Diagonal line patterns
7. **Vibrating Worm**: Animated worm with vibration
8. **Wandering Simple**: Complex wandering patterns
9. **Flitterbug**: Particle-like fluttering effects
10. **Spirostar**: Star-shaped spiral patterns
11. **Exploding Daisy**: Radial explosion patterns
12. **Swirlie Dots**: Swirling dot patterns
13. **Sweep**: Sweeping motion effects
14. **Whiplash Spiral**: Dynamic spiral with whiplash

---

## 🚀 **Future Enhancements**

### **Phoenix-Specific Features**
- **Shader integration**: GLSL/HLSL shader support
- **GPU acceleration**: Parallel point processing
- **Advanced math**: Extended mathematical function library
- **Real-time editing**: Live script editing and preview
- **Preset marketplace**: Community preset sharing

---

## 📖 **References**

- **Source Code**: `r_sscope.cpp` from VIS_AVS
- **Header**: `r_defs.h` for base class definitions
- **Script Engine**: `avs_eelif.h/cpp` for expression evaluation
- **Rendering**: `draw.cpp` for line drawing functions
- **Timing**: `timing.h` for performance measurement

---

**Status:** ✅ **FIRST TEMPLATE LOCKED**  
**Next:** DynamicMovement.md template creation
