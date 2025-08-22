# Brightness Effects (Trans / Brightness)

## Overview

The **Brightness Effects** system is a sophisticated color and brightness manipulation engine that provides advanced control over image brightness, color channels, and blending operations. It implements comprehensive brightness adjustment with multi-threaded processing, color dissociation, and intelligent blending modes for creating complex color transformations. This effect provides the foundation for sophisticated brightness control, color manipulation, and advanced image processing in AVS presets.

## Source Analysis

### Core Architecture (`r_bright.cpp`)

The effect is implemented as a C++ class `C_BrightnessClass` that inherits from `C_RBASE2`. It provides a comprehensive brightness and color manipulation system with multi-threaded processing, color dissociation, and intelligent blending modes for creating complex color transformations.

### Key Components

#### Brightness Processing Engine
Advanced brightness control system:
- **Channel Control**: Independent control of red, green, and blue channels
- **Brightness Adjustment**: Precise brightness control with configurable ranges
- **Color Dissociation**: Advanced color dissociation and manipulation
- **Performance Optimization**: Multi-threaded processing for real-time operations

#### Color Management System
Sophisticated color processing:
- **Color Tables**: Pre-calculated color transformation tables
- **Channel Separation**: Independent processing of RGB channels
- **Color Exclusion**: Configurable color exclusion and filtering
- **Distance Control**: Intelligent color distance and similarity control

#### Blending System
Advanced blending capabilities:
- **Multiple Blend Modes**: Replace, additive, and average blending
- **Blend Control**: Configurable blend intensity and behavior
- **Visual Integration**: Seamless integration with existing visual content
- **Quality Control**: High-quality blending algorithms

#### Multi-Threading System
Performance optimization:
- **SMP Support**: Symmetric Multi-Processing support for performance
- **Thread Management**: Intelligent thread distribution and management
- **Performance Scaling**: Dynamic performance scaling based on CPU cores
- **Synchronization**: Advanced thread synchronization and data sharing

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `enabled` | bool | true/false | true | Enable/disable brightness effect |
| `redp` | int | -255-255 | 0 | Red channel brightness adjustment |
| `greenp` | int | -255-255 | 0 | Green channel brightness adjustment |
| `bluep` | int | -255-255 | 0 | Blue channel brightness adjustment |
| `blend` | int | 0-1 | 0 | Blend mode (0=Replace, 1=Additive) |
| `blendavg` | int | 0-1 | 1 | Average blending mode |
| `dissoc` | int | 0-1 | 0 | Color dissociation mode |
| `color` | int | 0x000000-0xFFFFFF | 0 | Color exclusion value |
| `exclude` | int | 0-1 | 0 | Enable color exclusion |
| `distance` | int | 0-255 | 16 | Color distance threshold |

### Blending Modes

| Mode | Value | Description | Behavior |
|------|-------|-------------|----------|
| **Replace** | 0 | Replace mode | Brightness effect replaces underlying content |
| **Additive** | 1 | Additive blending | Brightness effect adds to underlying content |
| **Average** | 1 | Average blending | Brightness effect averages with underlying content |

### Color Dissociation Modes

| Mode | Value | Description | Behavior |
|------|-------|-------------|----------|
| **Normal** | 0 | Standard processing | Standard brightness and color processing |
| **Dissociated** | 1 | Color dissociation | Advanced color dissociation and manipulation |

## C# Implementation

```csharp
public class BrightnessEffectsNode : AvsModuleNode
{
    public bool Enabled { get; set; } = true;
    public int RedAdjustment { get; set; } = 0;
    public int GreenAdjustment { get; set; } = 0;
    public int BlueAdjustment { get; set; } = 0;
    public int Blend { get; set; } = 0;
    public int BlendAvg { get; set; } = 1;
    public int Dissoc { get; set; } = 0;
    public int Color { get; set; } = 0;
    public int Exclude { get; set; } = 0;
    public int Distance { get; set; } = 16;
    
    // Internal state
    private int[] redTable;
    private int[] greenTable;
    private int[] blueTable;
    private bool tablesNeedInit;
    private int lastWidth, lastHeight;
    private readonly object renderLock = new object();
    
    // Performance optimization
    private const int MaxAdjustment = 255;
    private const int MinAdjustment = -255;
    private const int MaxDistance = 255;
    private const int MinDistance = 0;
    private const int MaxBlend = 1;
    private const int MinBlend = 0;
    private const int TableSize = 256;
    
    public BrightnessEffectsNode()
    {
        redTable = new int[TableSize];
        greenTable = new int[TableSize];
        blueTable = new int[TableSize];
        tablesNeedInit = true;
        lastWidth = lastHeight = 0;
        
        InitializeColorTables();
    }
    
    private void InitializeColorTables()
    {
        // Initialize color transformation tables
        for (int i = 0; i < TableSize; i++)
        {
            redTable[i] = i;
            greenTable[i] = i;
            blueTable[i] = i;
        }
        
        tablesNeedInit = false;
    }
    
    public override void Process(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (!Enabled || ctx.Width <= 0 || ctx.Height <= 0) return;
        
        lock (renderLock)
        {
            // Update buffers if dimensions changed
            UpdateBuffers(ctx);
            
            // Update color tables if needed
            UpdateColorTables();
            
            // Apply brightness effect
            ApplyBrightnessEffect(ctx, input, output);
        }
    }
    
    private void UpdateBuffers(FrameContext ctx)
    {
        if (lastWidth != ctx.Width || lastHeight != ctx.Height)
        {
            lastWidth = ctx.Width;
            lastHeight = ctx.Height;
        }
    }
    
    private void UpdateColorTables()
    {
        if (tablesNeedInit)
        {
            InitializeColorTables();
        }
        
        // Update red channel table
        for (int i = 0; i < TableSize; i++)
        {
            int adjusted = i + RedAdjustment;
            redTable[i] = Math.Clamp(adjusted, 0, 255);
        }
        
        // Update green channel table
        for (int i = 0; i < TableSize; i++)
        {
            int adjusted = i + GreenAdjustment;
            greenTable[i] = Math.Clamp(adjusted, 0, 255);
        }
        
        // Update blue channel table
        for (int i = 0; i < TableSize; i++)
        {
            int adjusted = i + BlueAdjustment;
            blueTable[i] = Math.Clamp(adjusted, 0, 255);
        }
    }
    
    private void ApplyBrightnessEffect(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        // Use multi-threading for performance
        int threadCount = Environment.ProcessorCount;
        
        if (threadCount > 1)
        {
            ApplyBrightnessEffectMultiThreaded(ctx, input, output, threadCount);
        }
        else
        {
            ApplyBrightnessEffectSingleThreaded(ctx, input, output);
        }
    }
    
    private void ApplyBrightnessEffectMultiThreaded(FrameContext ctx, ImageBuffer input, ImageBuffer output, int threadCount)
    {
        var tasks = new Task[threadCount];
        
        for (int t = 0; t < threadCount; t++)
        {
            int threadId = t;
            tasks[t] = Task.Run(() => ApplyBrightnessEffectThread(ctx, input, output, threadId, threadCount));
        }
        
        Task.WaitAll(tasks);
    }
    
    private void ApplyBrightnessEffectThread(FrameContext ctx, ImageBuffer input, ImageBuffer output, int threadId, int threadCount)
    {
        // Calculate thread boundaries
        int startY = (threadId * ctx.Height) / threadCount;
        int endY = ((threadId + 1) * ctx.Height) / threadCount;
        
        for (int y = startY; y < endY; y++)
        {
            for (int x = 0; x < ctx.Width; x++)
            {
                ProcessPixel(x, y, input, output);
            }
        }
    }
    
    private void ApplyBrightnessEffectSingleThreaded(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        for (int y = 0; y < ctx.Height; y++)
        {
            for (int x = 0; x < ctx.Width; x++)
            {
                ProcessPixel(x, y, input, output);
            }
        }
    }
    
    private void ProcessPixel(int x, int y, ImageBuffer input, ImageBuffer output)
    {
        Color inputPixel = input.GetPixel(x, y);
        
        // Check color exclusion
        if (Exclude == 1 && ShouldExcludeColor(inputPixel))
        {
            output.SetPixel(x, y, inputPixel);
            return;
        }
        
        // Apply brightness adjustments
        Color adjustedPixel = ApplyBrightnessAdjustments(inputPixel);
        
        // Apply blending
        Color finalPixel = ApplyBlendingMode(inputPixel, adjustedPixel);
        
        output.SetPixel(x, y, finalPixel);
    }
    
    private bool ShouldExcludeColor(Color pixel)
    {
        if (Exclude == 0) return false;
        
        // Calculate color distance
        int targetR = (Color >> 16) & 0xFF;
        int targetG = (Color >> 8) & 0xFF;
        int targetB = Color & 0xFF;
        
        int distance = CalculateColorDistance(
            pixel.R, pixel.G, pixel.B,
            targetR, targetG, targetB
        );
        
        return distance <= Distance;
    }
    
    private int CalculateColorDistance(int r1, int g1, int b1, int r2, int g2, int b2)
    {
        // Calculate Euclidean distance in RGB space
        int dr = r1 - r2;
        int dg = g1 - g2;
        int db = b1 - b2;
        
        return (int)Math.Sqrt(dr * dr + dg * dg + db * db);
    }
    
    private Color ApplyBrightnessAdjustments(Color pixel)
    {
        if (Dissoc == 1)
        {
            // Apply color dissociation
            return ApplyColorDissociation(pixel);
        }
        else
        {
            // Apply standard brightness adjustments
            return ApplyStandardBrightnessAdjustments(pixel);
        }
    }
    
    private Color ApplyStandardBrightnessAdjustments(Color pixel)
    {
        int r = redTable[pixel.R];
        int g = greenTable[pixel.G];
        int b = blueTable[pixel.B];
        
        return Color.FromRgb((byte)r, (byte)g, (byte)b);
    }
    
    private Color ApplyColorDissociation(Color pixel)
    {
        // Advanced color dissociation algorithm
        float luminance = (pixel.R * 0.299f + pixel.G * 0.587f + pixel.B * 0.114f);
        
        int r = (int)(luminance + RedAdjustment);
        int g = (int)(luminance + GreenAdjustment);
        int b = (int)(luminance + BlueAdjustment);
        
        // Clamp values
        r = Math.Clamp(r, 0, 255);
        g = Math.Clamp(g, 0, 255);
        b = Math.Clamp(b, 0, 255);
        
        return Color.FromRgb((byte)r, (byte)g, (byte)b);
    }
    
    private Color ApplyBlendingMode(Color originalColor, Color adjustedColor)
    {
        switch (Blend)
        {
            case 0: // Replace
                return adjustedColor;
                
            case 1: // Additive
                return Color.FromRgb(
                    (byte)Math.Min(255, originalColor.R + adjustedColor.R),
                    (byte)Math.Min(255, originalColor.G + adjustedColor.G),
                    (byte)Math.Min(255, originalColor.B + adjustedColor.B)
                );
                
            default:
                return adjustedColor;
        }
    }
    
    // Public interface for parameter adjustment
    public void SetEnabled(bool enable) { Enabled = enable; }
    
    public void SetRedAdjustment(int adjustment) 
    { 
        RedAdjustment = Math.Clamp(adjustment, MinAdjustment, MaxAdjustment); 
        tablesNeedInit = true;
    }
    
    public void SetGreenAdjustment(int adjustment) 
    { 
        GreenAdjustment = Math.Clamp(adjustment, MinAdjustment, MaxAdjustment); 
        tablesNeedInit = true;
    }
    
    public void SetBlueAdjustment(int adjustment) 
    { 
        BlueAdjustment = Math.Clamp(adjustment, MinAdjustment, MaxAdjustment); 
        tablesNeedInit = true;
    }
    
    public void SetBlend(int blend) 
    { 
        Blend = Math.Clamp(blend, MinBlend, MaxBlend); 
    }
    
    public void SetBlendAvg(int blendAvg) 
    { 
        BlendAvg = Math.Clamp(blendAvg, MinBlend, MaxBlend); 
    }
    
    public void SetDissoc(int dissoc) 
    { 
        Dissoc = Math.Clamp(dissoc, 0, 1); 
    }
    
    public void SetColor(int color) { Color = color; }
    
    public void SetExclude(int exclude) 
    { 
        Exclude = Math.Clamp(exclude, 0, 1); 
    }
    
    public void SetDistance(int distance) 
    { 
        Distance = Math.Clamp(distance, MinDistance, MaxDistance); 
    }
    
    // Status queries
    public bool IsEnabled() => Enabled;
    public int GetRedAdjustment() => RedAdjustment;
    public int GetGreenAdjustment() => GreenAdjustment;
    public int GetBlueAdjustment() => BlueAdjustment;
    public int GetBlend() => Blend;
    public int GetBlendAvg() => BlendAvg;
    public int GetDissoc() => Dissoc;
    public int GetColor() => Color;
    public int GetExclude() => Exclude;
    public int GetDistance() => Distance;
    public bool AreTablesInitialized() => !tablesNeedInit;
    
    // Advanced brightness control
    public void SetAllChannelAdjustments(int adjustment)
    {
        SetRedAdjustment(adjustment);
        SetGreenAdjustment(adjustment);
        SetBlueAdjustment(adjustment);
    }
    
    public void SetRGBAdjustments(int red, int green, int blue)
    {
        SetRedAdjustment(red);
        SetGreenAdjustment(green);
        SetBlueAdjustment(blue);
    }
    
    public void SetBrightness(int brightness)
    {
        // Convert brightness to channel adjustments
        int adjustment = brightness - 128;
        SetAllChannelAdjustments(adjustment);
    }
    
    public void SetContrast(float contrast)
    {
        // Apply contrast adjustment to all channels
        for (int i = 0; i < TableSize; i++)
        {
            int adjusted = (int)((i - 128) * contrast + 128);
            redTable[i] = Math.Clamp(adjusted, 0, 255);
            greenTable[i] = Math.Clamp(adjusted, 0, 255);
            blueTable[i] = Math.Clamp(adjusted, 0, 255);
        }
    }
    
    // Color exclusion presets
    public void SetExcludeRed()
    {
        SetColor(0xFF0000);
        SetExclude(1);
        SetDistance(50);
    }
    
    public void SetExcludeGreen()
    {
        SetColor(0x00FF00);
        SetExclude(1);
        SetDistance(50);
    }
    
    public void SetExcludeBlue()
    {
        SetColor(0x0000FF);
        SetExclude(1);
        SetDistance(50);
    }
    
    public void SetExcludeWhite()
    {
        SetColor(0xFFFFFF);
        SetExclude(1);
        SetDistance(100);
    }
    
    public void SetExcludeBlack()
    {
        SetColor(0x000000);
        SetExclude(1);
        SetDistance(100);
    }
    
    // Brightness presets
    public void SetBright()
    {
        SetAllChannelAdjustments(50);
        SetBlend(0);
    }
    
    public void SetDark()
    {
        SetAllChannelAdjustments(-50);
        SetBlend(0);
    }
    
    public void SetHighContrast()
    {
        SetContrast(1.5f);
        SetBlend(0);
    }
    
    public void SetLowContrast()
    {
        SetContrast(0.7f);
        SetBlend(0);
    }
    
    public void SetSepia()
    {
        SetRedAdjustment(30);
        SetGreenAdjustment(-20);
        SetBlueAdjustment(-50);
        SetBlend(0);
    }
    
    public void SetGrayscale()
    {
        SetDissoc(1);
        SetAllChannelAdjustments(0);
        SetBlend(0);
    }
    
    // Performance optimization
    public void SetRenderQuality(int quality)
    {
        // Quality could affect processing detail or optimization level
        // For now, we maintain full quality
    }
    
    public void EnableOptimizations(bool enable)
    {
        // Various optimization flags could be implemented here
    }
    
    public override void Dispose()
    {
        lock (renderLock)
        {
            // Clean up resources if needed
            redTable = null;
            greenTable = null;
            blueTable = null;
        }
    }
}
```

## Integration Points

### Color Processing Integration
- **Channel Control**: Independent control of RGB color channels
- **Brightness Adjustment**: Precise brightness control and manipulation
- **Color Dissociation**: Advanced color dissociation and processing
- **Quality Control**: High-quality color transformation algorithms

### Performance Integration
- **Multi-Threading**: Symmetric Multi-Processing support for performance
- **Thread Management**: Intelligent thread distribution and management
- **Performance Scaling**: Dynamic performance scaling based on CPU cores
- **Synchronization**: Advanced thread synchronization and data sharing

### Image Processing Integration
- **Brightness Control**: Advanced brightness and contrast manipulation
- **Color Filtering**: Intelligent color exclusion and filtering
- **Blending Modes**: Multiple blending modes for visual integration
- **Visual Quality**: High-quality image processing and transformation

## Usage Examples

### Basic Brightness Adjustment
```csharp
var brightnessNode = new BrightnessEffectsNode
{
    Enabled = true,                       // Enable effect
    RedAdjustment = 20,                   // Increase red channel
    GreenAdjustment = 10,                 // Slight green increase
    BlueAdjustment = -5,                  // Decrease blue channel
    Blend = 0,                            // Replace mode
    BlendAvg = 1,                         // Enable average blending
    Dissoc = 0,                           // Standard processing
    Exclude = 0,                          // No color exclusion
    Distance = 16                         // Default distance threshold
};
```

### High Contrast Effect
```csharp
var brightnessNode = new BrightnessEffectsNode
{
    Enabled = true,
    RedAdjustment = 50,                   // High red adjustment
    GreenAdjustment = 50,                 // High green adjustment
    BlueAdjustment = 50,                  // High blue adjustment
    Blend = 0,                            // Replace mode
    Dissoc = 0,                           // Standard processing
    Exclude = 0                           // No color exclusion
};

// Apply high contrast preset
brightnessNode.SetHighContrast();
```

### Color Exclusion Effect
```csharp
var brightnessNode = new BrightnessEffectsNode
{
    Enabled = true,
    RedAdjustment = 30,                   // Moderate red increase
    GreenAdjustment = 0,                  // No green change
    BlueAdjustment = 0,                   // No blue change
    Blend = 1,                            // Additive blending
    Dissoc = 0,                           // Standard processing
    Exclude = 1,                          // Enable color exclusion
    Color = 0xFF0000,                     // Exclude red colors
    Distance = 50                         // Color distance threshold
};

// Apply red exclusion preset
brightnessNode.SetExcludeRed();
```

### Advanced Color Manipulation
```csharp
var brightnessNode = new BrightnessEffectsNode
{
    Enabled = true,
    RedAdjustment = 0,                    // No red change
    GreenAdjustment = 0,                  // No green change
    BlueAdjustment = 0,                   // No blue change
    Blend = 0,                            // Replace mode
    Dissoc = 1,                           // Enable color dissociation
    Exclude = 0,                          // No color exclusion
    Distance = 16                         // Default distance threshold
};

// Apply various presets
brightnessNode.SetSepia();                // Sepia tone effect
brightnessNode.SetGrayscale();            // Grayscale conversion
brightnessNode.SetBright();               // Brightness increase
```

## Technical Notes

### Color Architecture
The effect implements sophisticated color processing:
- **Channel Management**: Independent RGB channel control and manipulation
- **Color Tables**: Pre-calculated color transformation tables for performance
- **Dissociation Processing**: Advanced color dissociation algorithms
- **Quality Optimization**: High-quality color transformation and processing

### Performance Architecture
Advanced performance processing system:
- **Multi-Threading**: Symmetric Multi-Processing for performance optimization
- **Thread Management**: Intelligent thread distribution and management
- **Performance Scaling**: Dynamic performance scaling based on CPU cores
- **Synchronization**: Advanced thread synchronization and data sharing

### Integration System
Sophisticated system integration:
- **Color Processing**: Deep integration with color management system
- **Multi-Threading**: Seamless integration with threading system
- **Effect Management**: Advanced effect management and optimization
- **Performance Optimization**: Optimized operations for color processing

This effect provides the foundation for sophisticated brightness and color manipulation, creating advanced color transformations with multi-threaded processing, color dissociation, and intelligent blending modes for sophisticated AVS visualization systems.
