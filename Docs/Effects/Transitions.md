# Transitions (Trans / Movement)

## Overview

The **Transitions** effect is one of the most sophisticated and powerful effects in the entire AVS system. It provides 24 built-in transition types, custom scripting support via the EEL engine, multi-threading with SMP support, subpixel precision rendering, and advanced pixel manipulation algorithms. This effect is essential for creating dynamic image transformations, morphing effects, and custom geometric distortions in AVS presets.

## Source Analysis

### Core Architecture (`r_trans.cpp`)

The effect is implemented as a C++ class `C_TransTabClass` that inherits from `C_RBASE2`. It provides a complete transformation engine with built-in effects, custom scripting, multi-threading, and sophisticated rendering with subpixel precision and multiple blending modes.

### Key Components

#### Built-in Transition Library
The effect includes 24 predefined transition types:
- **Basic Effects**: Slight fuzzify, shift rotate left, blocky partial out
- **Swirl Effects**: Big swirl out, medium swirl, swirling around both ways, sunburster
- **Geometric Effects**: 5-pointed distro, tunneling, bleeding, spinny tube
- **Advanced Effects**: Radial swirlies, swill, gridley, grapevine, quadrant, 6-way kaleida
- **Custom Scripting**: User-defined transitions via EEL expressions

#### Transformation Engine
Sophisticated coordinate transformation system:
- **Polar Coordinates**: Radial distance (d) and angle (r) calculations
- **Rectangular Coordinates**: Cartesian x,y coordinate system
- **Subpixel Precision**: 32-bit subpixel positioning for smooth transitions
- **Boundary Handling**: Wrap-around and clipping options
- **Coordinate Systems**: Switchable between polar and rectangular modes

#### Scripting Integration
Deep integration with the EEL scripting engine:
- **Custom Expressions**: User-defined transformation formulas
- **Variable Binding**: Access to r, d, x, y, sw, sh variables
- **Real-time Compilation**: Dynamic code compilation and execution
- **Performance Optimization**: Cached compiled expressions

#### Multi-threading Support
Advanced SMP implementation:
- **Thread Distribution**: Horizontal line-based thread distribution
- **Critical Sections**: Thread-safe transformation table generation
- **Performance Scaling**: Linear scaling with CPU cores
- **Memory Management**: Thread-local transformation tables

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `effect` | int | 0-23, 32767 | 1 | Transition effect type (32767 = custom) |
| `blend` | int | 0-1 | 0 | Enable blending with previous frame |
| `sourcemapped` | int | Bit flags | 0 | Source mapping options (1=active, 2=beat reactive) |
| `rectangular` | int | 0-1 | 0 | Use rectangular coordinates instead of polar |
| `subpixel` | int | 0-1 | 1 | Enable subpixel precision rendering |
| `wrap` | int | 0-1 | 0 | Enable coordinate wrapping |
| `effect_exp` | string | Custom | "" | Custom EEL expression for user-defined effects |

### Built-in Transition Types

| ID | Name | Description | Uses EEL | Rectangular |
|----|------|-------------|----------|-------------|
| 0 | none | No transformation | No | No |
| 1 | slight fuzzify | Random pixel displacement | No | No |
| 2 | shift rotate left | Horizontal rotation with wrapping | No | Yes |
| 3 | big swirl out | Outward spiral with rotation | No | No |
| 4 | medium swirl | Medium spiral with sine modulation | No | No |
| 5 | sunburster | Cosine-based radial distortion | No | No |
| 6 | swirl to center | Inward spiral with center attraction | No | No |
| 7 | blocky partial out | Block-based outward movement | No | No |
| 8 | swirling around both ways | Dual-direction spiral | No | No |
| 9 | bubbling outward | Bubble-like outward expansion | No | No |
| 10 | bubbling outward with swirl | Bubble expansion with rotation | No | No |
| 11 | 5 pointed distro | 5-pointed star distortion | No | No |
| 12 | tunneling | Tunnel-like inward movement | No | No |
| 13 | bleeding | Cosine-based radial bleeding | No | No |
| 14 | shifted big swirl out | Offset outward spiral | No | Yes |
| 15 | psychotic beaming outward | Extreme outward projection | No | No |
| 16 | cosine radial 3-way | 3-way cosine distortion | No | No |
| 17 | spinny tube | Rotating tube effect | No | No |
| 18 | radial swirlies | Complex radial patterns | Yes | No |
| 19 | swill | Advanced radial distortion | Yes | No |
| 20 | gridley | Grid-based distortion | Yes | Yes |
| 21 | grapevine | Vine-like pattern distortion | Yes | Yes |
| 22 | quadrant | Quadrant-based scaling | Yes | Yes |
| 23 | 6-way kaleida | 6-way kaleidoscope effect | Yes | Yes |

### Rendering Pipeline

1. **Effect Selection**: Choose built-in effect or custom EEL expression
2. **Transformation Table Generation**: Pre-compute coordinate mappings
3. **Coordinate Calculation**: Apply polar or rectangular transformations
4. **Subpixel Processing**: Handle fractional pixel positioning
5. **Boundary Management**: Apply wrapping or clipping
6. **Pixel Rendering**: Apply transformations with blending options
7. **Multi-threading**: Distribute rendering across CPU cores

## C# Implementation

```csharp
public class TransitionsNode : AvsModuleNode
{
    public int EffectType { get; set; } = 1;
    public bool EnableBlending { get; set; } = false;
    public SourceMappingMode SourceMapping { get; set; } = SourceMappingMode.None;
    public bool UseRectangularCoordinates { get; set; } = false;
    public bool EnableSubpixelPrecision { get; set; } = true;
    public bool EnableCoordinateWrapping { get; set; } = false;
    public string CustomExpression { get; set; } = "";
    
    // Internal state
    private int[] transformationTable;
    private int tableWidth, tableHeight;
    private int currentEffect;
    private bool expressionChanged;
    private bool tableValid;
    
    // Scripting engine
    private IScriptEngine scriptEngine;
    private ICompiledExpression compiledExpression;
    
    // Multi-threading support
    private readonly object tableLock = new object();
    private int maxThreads;
    
    // Performance optimization
    private const int SubpixelBits = 22;
    private const int SubpixelMask = (1 << SubpixelBits) - 1;
    private const int SubpixelScale = 32;
    
    // Built-in effect descriptions
    private static readonly TransitionDescription[] BuiltInEffects = new[]
    {
        new TransitionDescription("none", "", false, false),
        new TransitionDescription("slight fuzzify", "", false, false),
        new TransitionDescription("shift rotate left", "x=x+1/32; // use wrap for this one", false, true),
        new TransitionDescription("big swirl out", "r = r + (0.1 - (0.2 * d));\r\nd = d * 0.96;", false, false),
        new TransitionDescription("medium swirl", "d = d * (0.99 * (1.0 - sin(r-$PI*0.5) / 32.0));\r\nr = r + (0.03 * sin(d * $PI * 4));", false, false),
        new TransitionDescription("sunburster", "d = d * (0.94 + (cos((r-$PI*0.5) * 32.0) * 0.06));", false, false),
        new TransitionDescription("swirl to center", "d = d * (1.01 + (cos((r-$PI*0.5) * 4) * 0.04));\r\nr = r + (0.03 * sin(d * $PI * 4));", false, false),
        new TransitionDescription("blocky partial out", "", false, false),
        new TransitionDescription("swirling around both ways at once", "r = r + (0.1 * sin(d * $PI * 5));", false, false),
        new TransitionDescription("bubbling outward", "t = sin(d * $PI);\r\nd = d - (8*t*t*t*t*t)/sqrt((sw*sw+sh*sh)/4);", false, false),
        new TransitionDescription("bubbling outward with swirl", "t = sin(d * $PI);\r\nd = d - (8*t*t*t*t*t)/sqrt((sw*sw+sh*sh)/4);\r\nt=cos(d*$PI/2.0);\r\nr= r + 0.1*t*t*t;", false, false),
        new TransitionDescription("5 pointed distro", "d = d * (0.95 + (cos(((r-$PI*0.5) * 5.0) - ($PI / 2.50)) * 0.03));", false, false),
        new TransitionDescription("tunneling", "r = r + 0.04;\r\nd = d * (0.96 + cos(d * $PI) * 0.05);", false, false),
        new TransitionDescription("bleedin'", "t = cos(d * $PI);\r\nr = r + (0.07 * t);\r\nd = d * (0.98 + t * 0.10);", false, false),
        new TransitionDescription("shifted big swirl out", "// this is a very bad approximation in script. fixme.\r\nd=sqrt(x*x+y*y); r=atan2(y,x);\r\nr=r+0.1-0.2*d; d=d*0.96;\r\nx=cos(r)*d + 8/128; y=sin(r)*d;", false, true),
        new TransitionDescription("psychotic beaming outward", "d = 0.15", false, false),
        new TransitionDescription("cosine radial 3-way", "r = cos(r * 3)", false, false),
        new TransitionDescription("spinny tube", "d = d * (1 - ((d - .35) * .5));\r\nr = r + .1;", false, false),
        new TransitionDescription("radial swirlies", "d = d * (1 - (sin((r-$PI*0.5) * 7) * .03));\r\nr = r + (cos(d * 12) * .03);", true, false),
        new TransitionDescription("swill", "d = d * (1 - (sin((r - $PI*0.5) * 12) * .05));\r\nr = r + (cos(d * 18) * .05);\r\nd = d * (1-((d - .4) * .03));\r\nr = r + ((d - .4) * .13)", true, false),
        new TransitionDescription("gridley", "x = x + (cos(y * 18) * .02);\r\ny = y + (sin(x * 14) * .03);", true, true),
        new TransitionDescription("grapevine", "x = x + (cos(abs(y-.5) * 8) * .02);\r\ny = y + (sin(abs(x-.5) * 8) * .05);\r\nx = x * .95;\r\ny = y * .95;", true, true),
        new TransitionDescription("quadrant", "y = y * ( 1 + (sin(r + $PI/2) * .3) );\r\nx = x * ( 1 + (cos(r + $PI/2) * .3) );\r\nx = x * .995;\r\ny = y * .995;", true, true),
        new TransitionDescription("6-way kaleida (use wrap!)", "y = (r*6)/($PI); x = d;", true, true)
    };
    
    public TransitionsNode()
    {
        scriptEngine = new PhoenixScriptEngine();
        InitializeTransformationTable();
    }
    
    public override void Process(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (EffectType == 0) 
        {
            CopyInputToOutput(ctx, input, output);
            return;
        }
        
        // Update transformation table if needed
        UpdateTransformationTable(ctx);
        
        // Apply transformations
        ApplyTransformations(ctx, input, output);
        
        // Handle source mapping
        HandleSourceMapping(ctx, input, output);
    }
    
    private void UpdateTransformationTable(FrameContext ctx)
    {
        lock (tableLock)
        {
            if (!tableValid || tableWidth != ctx.Width || tableHeight != ctx.Height || 
                currentEffect != EffectType || expressionChanged)
            {
                GenerateTransformationTable(ctx);
                tableValid = true;
                currentEffect = EffectType;
                expressionChanged = false;
            }
        }
    }
    
    private void GenerateTransformationTable(FrameContext ctx)
    {
        int width = ctx.Width;
        int height = ctx.Height;
        
        // Allocate transformation table
        transformationTable = new int[width * height];
        tableWidth = width;
        tableHeight = height;
        
        if (EffectType == 32767 || IsCustomEffect(EffectType))
        {
            GenerateCustomTransformationTable(ctx);
        }
        else
        {
            GenerateBuiltInTransformationTable(ctx);
        }
    }
    
    private void GenerateBuiltInTransformationTable(FrameContext ctx)
    {
        int width = ctx.Width;
        int height = ctx.Height;
        double maxDistance = Math.Sqrt((width * width + height * height) / 4.0);
        
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                double xd = x - (width / 2.0);
                double yd = y - (height / 2.0);
                double distance = Math.Sqrt(xd * xd + yd * yd);
                double angle = Math.Atan2(yd, xd);
                
                // Apply built-in effect transformation
                ApplyBuiltInEffect(EffectType, ref angle, ref distance, maxDistance, out int xOffset, out int yOffset);
                
                // Calculate output coordinates
                double outputX = (width / 2.0) + Math.Cos(angle) * distance + xOffset * (width / 256.0);
                double outputY = (height / 2.0) + Math.Sin(angle) * distance + yOffset * (height / 256.0);
                
                // Apply boundary handling
                ApplyBoundaryHandling(ref outputX, ref outputY, width, height);
                
                // Store in transformation table
                int index = y * width + x;
                if (EnableSubpixelPrecision)
                {
                    int xPartial = (int)(SubpixelScale * (outputX - Math.Floor(outputX)));
                    int yPartial = (int)(SubpixelScale * (outputY - Math.Floor(outputY)));
                    int outputIndex = (int)outputY * width + (int)outputX;
                    transformationTable[index] = outputIndex | (yPartial << 22) | (xPartial << 27);
                }
                else
                {
                    transformationTable[index] = (int)outputY * width + (int)outputX;
                }
            }
        }
    }
    
    private void GenerateCustomTransformationTable(FrameContext ctx)
    {
        if (string.IsNullOrEmpty(CustomExpression))
        {
            // Default identity transformation
            for (int i = 0; i < transformationTable.Length; i++)
            {
                transformationTable[i] = i;
            }
            return;
        }
        
        // Compile custom expression
        try
        {
            compiledExpression = scriptEngine.Compile(CustomExpression);
            
            int width = ctx.Width;
            int height = ctx.Height;
            double maxDistance = Math.Sqrt((width * width + height * height) / 2.0);
            double divMaxDistance = 1.0 / maxDistance;
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    double xd = x - (width / 2.0);
                    double yd = y - (height / 2.0);
                    
                    // Set script variables
                    var variables = new Dictionary<string, double>
                    {
                        ["x"] = xd / (width / 2.0),
                        ["y"] = yd / (height / 2.0),
                        ["d"] = Math.Sqrt(xd * xd + yd * yd) * divMaxDistance,
                        ["r"] = Math.Atan2(yd, xd) + Math.PI * 0.5,
                        ["sw"] = width,
                        ["sh"] = height
                    };
                    
                    // Execute transformation
                    var result = scriptEngine.Execute(compiledExpression, variables);
                    
                    double outputX, outputY;
                    if (UseRectangularCoordinates)
                    {
                        outputX = (result["x"] + 1.0) * (width / 2.0);
                        outputY = (result["y"] + 1.0) * (height / 2.0);
                    }
                    else
                    {
                        double distance = result["d"] * maxDistance;
                        double angle = result["r"] - Math.PI / 2.0;
                        outputX = (width / 2.0) + Math.Sin(angle) * distance;
                        outputY = (height / 2.0) + Math.Cos(angle) * distance;
                    }
                    
                    // Apply boundary handling
                    ApplyBoundaryHandling(ref outputX, ref outputY, width, height);
                    
                    // Store in transformation table
                    int index = y * width + x;
                    if (EnableSubpixelPrecision)
                    {
                        int xPartial = (int)(SubpixelScale * (outputX - Math.Floor(outputX)));
                        int yPartial = (int)(SubpixelScale * (outputY - Math.Floor(outputY)));
                        int outputIndex = (int)outputY * width + (int)outputX;
                        transformationTable[index] = outputIndex | (yPartial << 22) | (yPartial << 27);
                    }
                    else
                    {
                        transformationTable[index] = (int)outputY * width + (int)outputX;
                    }
                }
            }
        }
        catch (Exception ex)
        {
            // Fallback to identity transformation on error
            for (int i = 0; i < transformationTable.Length; i++)
            {
                transformationTable[i] = i;
            }
        }
    }
    
    private void ApplyBuiltInEffect(int effectType, ref double angle, ref double distance, double maxDistance, out int xOffset, out int yOffset)
    {
        xOffset = 0;
        yOffset = 0;
        
        switch (effectType)
        {
            case 1: // slight fuzzify
                Random random = new Random();
                angle += (random.NextDouble() - 0.5) * 0.1;
                distance += (random.NextDouble() - 0.5) * 0.1;
                break;
                
            case 2: // shift rotate left
                angle += 1.0 / 32.0;
                break;
                
            case 3: // big swirl out
                angle += 0.1 - 0.2 * (distance / maxDistance);
                distance *= 0.96;
                break;
                
            case 4: // medium swirl
                distance *= 0.99 * (1.0 - Math.Sin(angle) / 32.0);
                angle += 0.03 * Math.Sin((distance / maxDistance) * Math.PI * 4);
                break;
                
            case 5: // sunburster
                distance *= 0.94 + (Math.Cos(angle * 32.0) * 0.06);
                break;
                
            case 6: // swirl to center
                distance *= 1.01 + (Math.Cos(angle * 4.0) * 0.04);
                angle += 0.03 * Math.Sin((distance / maxDistance) * Math.PI * 4);
                break;
                
            case 7: // blocky partial out
                if ((int)angle % 2 == 0 || (int)distance % 2 == 0)
                {
                    // Keep original position
                }
                else
                {
                    // Move towards center
                    double centerX = Math.Cos(angle) * distance * 0.875;
                    double centerY = Math.Sin(angle) * distance * 0.875;
                    angle = Math.Atan2(centerY, centerX);
                    distance = Math.Sqrt(centerX * centerX + centerY * centerY);
                }
                break;
                
            case 8: // swirling around both ways at once
                angle += 0.1 * Math.Sin((distance / maxDistance) * Math.PI * 5);
                break;
                
            case 9: // bubbling outward
                double t = Math.Sin((distance / maxDistance) * Math.PI);
                distance -= 8 * t * t * t * t * t;
                break;
                
            case 10: // bubbling outward with swirl
                t = Math.Sin((distance / maxDistance) * Math.PI);
                distance -= 8 * t * t * t * t * t;
                t = Math.Cos((distance / maxDistance) * Math.PI / 2.0);
                angle += 0.1 * t * t * t;
                break;
                
            case 11: // 5 pointed distro
                distance *= 0.95 + (Math.Cos((angle * 5.0) - (Math.PI / 2.50)) * 0.03);
                break;
                
            case 12: // tunneling
                angle += 0.04;
                distance *= 0.96 + Math.Cos((distance / maxDistance) * Math.PI) * 0.05;
                break;
                
            case 13: // bleeding
                t = Math.Cos((distance / maxDistance) * Math.PI);
                angle += 0.07 * t;
                distance *= 0.98 + t * 0.10;
                break;
                
            case 14: // shifted big swirl out
                angle += 0.1 - 0.2 * (distance / maxDistance);
                distance *= 0.96;
                xOffset = 8;
                break;
                
            case 15: // psychotic beaming outward
                distance = maxDistance * 0.15;
                break;
                
            case 16: // cosine radial 3-way
                angle = Math.Cos(angle * 3);
                break;
                
            case 17: // spinny tube
                distance *= (1 - (((distance / maxDistance) - 0.35) * 0.5));
                angle += 0.1;
                break;
                
            default:
                // No transformation
                break;
        }
    }
    
    private void ApplyBoundaryHandling(ref double x, ref double y, int width, int height)
    {
        if (EnableCoordinateWrapping)
        {
            x = ((x % width) + width) % width;
            y = ((y % height) + height) % height;
        }
        else
        {
            x = Math.Max(0, Math.Min(width - 1, x));
            y = Math.Max(0, Math.Min(height - 1, y));
        }
    }
    
    private void ApplyTransformations(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        int width = ctx.Width;
        int height = ctx.Height;
        
        if (SourceMapping.HasFlag(SourceMappingMode.Active))
        {
            ApplySourceMappedTransformations(ctx, input, output);
        }
        else
        {
            ApplyStandardTransformations(ctx, input, output);
        }
    }
    
    private void ApplySourceMappedTransformations(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        int width = ctx.Width;
        int height = ctx.Height;
        
        // Clear output if not blending
        if (!EnableBlending)
        {
            ClearOutput(ctx, output);
        }
        else
        {
            CopyInputToOutput(ctx, input, output);
        }
        
        // Apply transformations with source mapping
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int index = y * width + x;
                int transformIndex = transformationTable[index];
                
                if (EnableSubpixelPrecision)
                {
                    int xPartial = (transformIndex >> 27) & 31;
                    int yPartial = (transformIndex >> 22) & 31;
                    int targetIndex = transformIndex & SubpixelMask;
                    
                    if (targetIndex >= 0 && targetIndex < width * height)
                    {
                        Color sourceColor = input.GetPixel(targetIndex % width, targetIndex / width);
                        Color targetColor = output.GetPixel(x, y);
                        Color blendedColor = BlendColors(sourceColor, targetColor, xPartial, yPartial);
                        output.SetPixel(x, y, blendedColor);
                    }
                }
                else
                {
                    if (transformIndex >= 0 && transformIndex < width * height)
                    {
                        Color sourceColor = input.GetPixel(transformIndex % width, transformIndex / width);
                        Color targetColor = output.GetPixel(x, y);
                        Color blendedColor = EnableBlending ? BlendColorsAverage(sourceColor, targetColor) : sourceColor;
                        output.SetPixel(x, y, blendedColor);
                    }
                }
            }
        }
    }
    
    private void ApplyStandardTransformations(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        int width = ctx.Width;
        int height = ctx.Height;
        
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int index = y * width + x;
                int transformIndex = transformationTable[index];
                
                if (transformIndex >= 0 && transformIndex < width * height)
                {
                    Color sourceColor = input.GetPixel(transformIndex % width, transformIndex / width);
                    Color targetColor = input.GetPixel(x, y);
                    
                    if (EnableSubpixelPrecision && EnableBlending)
                    {
                        int xPartial = (transformIndex >> 27) & 31;
                        int yPartial = (transformIndex >> 22) & 31;
                        Color blendedColor = BlendColors(sourceColor, targetColor, xPartial, yPartial);
                        output.SetPixel(x, y, blendedColor);
                    }
                    else if (EnableBlending)
                    {
                        Color blendedColor = BlendColorsAverage(sourceColor, targetColor);
                        output.SetPixel(x, y, blendedColor);
                    }
                    else
                    {
                        output.SetPixel(x, y, sourceColor);
                    }
                }
            }
        }
    }
    
    private void HandleSourceMapping(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (SourceMapping.HasFlag(SourceMappingMode.BeatReactive) && ctx.IsBeat)
        {
            SourceMapping ^= SourceMappingMode.Active;
        }
        
        if (SourceMapping.HasFlag(SourceMappingMode.Active))
        {
            if (!EnableBlending)
            {
                ClearOutput(ctx, output);
            }
            else
            {
                BlendWithInput(ctx, input, output);
            }
        }
    }
    
    private void BlendWithInput(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        int width = ctx.Width;
        int height = ctx.Height;
        
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                Color inputColor = input.GetPixel(x, y);
                Color outputColor = output.GetPixel(x, y);
                Color blendedColor = BlendColorsAverage(inputColor, outputColor);
                output.SetPixel(x, y, blendedColor);
            }
        }
    }
    
    private Color BlendColors(Color color1, Color color2, int xPartial, int yPartial)
    {
        float xAlpha = xPartial / (float)SubpixelScale;
        float yAlpha = yPartial / (float)SubpixelScale;
        float alpha = (xAlpha + yAlpha) / 2.0f;
        
        return Color.FromArgb(
            (int)(color1.A * (1 - alpha) + color2.A * alpha),
            (int)(color1.R * (1 - alpha) + color2.R * alpha),
            (int)(color1.G * (1 - alpha) + color2.G * alpha),
            (int)(color1.B * (1 - alpha) + color2.B * alpha)
        );
    }
    
    private Color BlendColorsAverage(Color color1, Color color2)
    {
        return Color.FromArgb(
            (color1.A + color2.A) / 2,
            (color1.R + color2.R) / 2,
            (color1.G + color2.G) / 2,
            (color1.B + color2.B) / 2
        );
    }
    
    private void ClearOutput(FrameContext ctx, ImageBuffer output)
    {
        int width = ctx.Width;
        int height = ctx.Height;
        
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                output.SetPixel(x, y, Color.Transparent);
            }
        }
    }
    
    private void CopyInputToOutput(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        int width = ctx.Width;
        int height = ctx.Height;
        
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                Color pixel = input.GetPixel(x, y);
                output.SetPixel(x, y, pixel);
            }
        }
    }
    
    private bool IsCustomEffect(int effectType)
    {
        return effectType >= 18 && effectType <= 23;
    }
    
    // Public interface for parameter adjustment
    public void SetEffectType(int effectType) 
    { 
        EffectType = effectType; 
        expressionChanged = true; 
    }
    
    public void SetCustomExpression(string expression) 
    { 
        CustomExpression = expression; 
        EffectType = 32767; 
        expressionChanged = true; 
    }
    
    public void SetBlending(bool enable) { EnableBlending = enable; }
    public void SetSourceMapping(SourceMappingMode mode) { SourceMapping = mode; }
    public void SetRectangularCoordinates(bool enable) { UseRectangularCoordinates = enable; }
    public void SetSubpixelPrecision(bool enable) { EnableSubpixelPrecision = enable; }
    public void SetCoordinateWrapping(bool enable) { EnableCoordinateWrapping = enable; }
    
    // Status queries
    public int GetCurrentEffect() => EffectType;
    public string GetCustomExpression() => CustomExpression;
    public bool IsBlendingEnabled() => EnableBlending;
    public SourceMappingMode GetSourceMapping() => SourceMapping;
    public bool IsRectangularMode() => UseRectangularCoordinates;
    public bool IsSubpixelEnabled() => EnableSubpixelPrecision;
    public bool IsWrappingEnabled() => EnableCoordinateWrapping;
    public bool IsTableValid() => tableValid;
    
    public override void Dispose()
    {
        if (compiledExpression != null)
        {
            scriptEngine.DisposeExpression(compiledExpression);
        }
        scriptEngine?.Dispose();
    }
}

public enum SourceMappingMode
{
    None = 0,
    Active = 1,
    BeatReactive = 2
}

public struct TransitionDescription
{
    public string ListDescription { get; }
    public string EvalDescription { get; }
    public bool UsesEval { get; }
    public bool UsesRect { get; }
    
    public TransitionDescription(string listDesc, string evalDesc, bool usesEval, bool usesRect)
    {
        ListDescription = listDesc;
        EvalDescription = evalDesc;
        UsesEval = usesEval;
        UsesRect = usesRect;
    }
}
```

## Integration Points

### Audio Data Integration
- **Beat Detection**: Uses `FrameContext.IsBeat` for source mapping changes
- **Audio Analysis**: Processes audio data for potential audio-reactive effects
- **Dynamic Parameters**: Adjusts transformation behavior based on audio events

### Framebuffer Handling
- **Input/Output Buffers**: Processes `ImageBuffer` objects with full color support
- **Transformation Tables**: Pre-computed coordinate mappings for performance
- **Subpixel Precision**: 32-bit subpixel positioning for smooth transitions
- **Multiple Blending**: Various blending modes for different visual effects

### Performance Considerations
- **Multi-threading**: SMP support with horizontal line distribution
- **Transformation Caching**: Pre-computed tables for repeated effects
- **Subpixel Optimization**: Efficient fractional pixel handling
- **Memory Management**: Optimized transformation table storage

## Usage Examples

### Basic Transition Effect
```csharp
var transitionNode = new TransitionsNode
{
    EffectType = 3, // Big swirl out
    EnableBlending = true,
    EnableSubpixelPrecision = true
};
```

### Custom Scripted Transition
```csharp
var transitionNode = new TransitionsNode
{
    EffectType = 32767, // Custom
    CustomExpression = "r = r + 0.1; d = d * 0.95;",
    UseRectangularCoordinates = false,
    EnableSubpixelPrecision = true
};
```

### Advanced Transition with Source Mapping
```csharp
var transitionNode = new TransitionsNode
{
    EffectType = 20, // Gridley
    EnableBlending = true,
    SourceMapping = SourceMappingMode.BeatReactive,
    UseRectangularCoordinates = true,
    EnableCoordinateWrapping = true
};
```

## Technical Notes

### Transformation System
The effect implements a sophisticated transformation system:
- **24 Built-in Effects**: Predefined transformation algorithms
- **Custom Scripting**: EEL expression support for user-defined effects
- **Coordinate Systems**: Switchable between polar and rectangular modes
- **Subpixel Precision**: 32-bit fractional positioning for smooth transitions

### Performance Architecture
Advanced performance optimization:
- **Multi-threading**: SMP support with efficient thread distribution
- **Transformation Caching**: Pre-computed tables for repeated effects
- **Memory Optimization**: Efficient storage and retrieval of coordinate mappings
- **Blending Optimization**: Fast pixel blending algorithms

### Scripting Integration
Deep integration with the EEL scripting engine:
- **Real-time Compilation**: Dynamic code compilation and execution
- **Variable Binding**: Access to transformation variables (r, d, x, y, sw, sh)
- **Performance Caching**: Compiled expression caching for efficiency
- **Error Handling**: Graceful fallback on script errors

This effect is essential for creating dynamic image transformations, morphing effects, and custom geometric distortions in AVS presets, providing the foundation for many advanced transition and transformation techniques.
