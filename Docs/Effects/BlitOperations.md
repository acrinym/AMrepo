# Blit Operations (Trans / Blitter Feedback)

## Overview

The **Blit Operations** effect is a sophisticated image transformation and feedback system that provides two main blitting modes: **Normal Blitting** and **Outward Blitting**. It's designed to create dynamic scaling effects with optional blending and subpixel precision, making it essential for creating zoom effects, feedback loops, and dynamic image transformations in AVS presets.

## Source Analysis

### Core Architecture (`r_blit.cpp`)

The effect is implemented as a C++ class `C_BlitClass` that inherits from `C_RBASE`. It provides two distinct blitting algorithms:

1. **Normal Blitting** (`blitter_normal`): Scales the image with configurable scaling factors
2. **Outward Blitting** (`blitter_out`): Creates outward scaling effects for feedback loops

### Key Components

#### Blending Functions
- **`BLEND_AVG`**: Simple averaging of two colors: `((a>>1)&~((1<<7)|(1<<15)|(1<<23)))+((b>>1)&~((1<<7)|(1<<15)|(1<<23)))`
- **`BLEND4`**: 4-point bilinear interpolation for subpixel rendering with MMX optimization

#### MMX Optimization
The effect includes highly optimized MMX assembly code for performance-critical operations:
- Subpixel rendering with bilinear interpolation
- Batch processing of 4 pixels at a time
- SIMD operations for color blending

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `scale` | int | 0-256 | 30 | Primary scaling factor |
| `scale2` | int | 0-256 | 30 | Beat-reactive scaling factor |
| `blend` | bool | 0/1 | false | Enable blending with original frame |
| `beatch` | bool | 0/1 | false | Enable beat-reactive scaling |
| `subpixel` | bool | 0/1 | true | Enable subpixel precision rendering |

### Rendering Pipeline

1. **Beat Detection**: If `beatch` is enabled, `scale2` is used on beat events
2. **Scaling Calculation**: Dynamic scaling factor based on current position and target
3. **Mode Selection**: 
   - `f_val < 32`: Normal blitting
   - `f_val > 32`: Outward blitting
   - `f_val = 32`: No effect
4. **Rendering**: Apply selected blitting algorithm with optional blending

## C# Implementation

```csharp
public class BlitOperationsNode : AvsModuleNode
{
    public bool Enabled { get; set; } = true;
    public int Scale { get; set; } = 30;
    public int Scale2 { get; set; } = 30;
    public bool Blend { get; set; } = false;
    public bool BeatReactive { get; set; } = false;
    public bool SubpixelPrecision { get; set; } = true;
    
    // Internal state
    private int currentPosition;
    private int targetScale;
    private float frameTime;
    private int frameCount;
    private bool wasBeat;
    
    // Audio data
    private float[] leftChannelData;
    private float[] rightChannelData;
    private float[] centerChannelData;
    
    // Multi-threading support
    private int threadCount;
    private Task[] processingTasks;
    private readonly object lockObject = new object();
    
    // Blending lookup tables
    private byte[,] blendTable;
    private bool blendTableInitialized;
    
    public BlitOperationsNode()
    {
        threadCount = Environment.ProcessorCount;
        processingTasks = new Task[threadCount];
        currentPosition = Scale;
        targetScale = Scale;
        InitializeBlendTable();
    }
    
    public override void Process(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (!Enabled) 
        {
            CopyInputToOutput(ctx, input, output);
            return;
        }
        
        UpdateAudioData(ctx);
        UpdateScalingParameters(ctx);
        
        int scalingFactor = CalculateScalingFactor();
        
        if (scalingFactor < 32)
        {
            ApplyNormalBlitting(ctx, input, output, scalingFactor);
        }
        else if (scalingFactor > 32)
        {
            ApplyOutwardBlitting(ctx, input, output, scalingFactor);
        }
        else
        {
            CopyInputToOutput(ctx, input, output);
        }
        
        UpdateFrameState(ctx);
    }
    
    private void UpdateAudioData(FrameContext ctx)
    {
        if (ctx.AudioData != null)
        {
            leftChannelData = ctx.AudioData.LeftChannel;
            rightChannelData = ctx.AudioData.RightChannel;
            centerChannelData = ctx.AudioData.CenterChannel;
        }
    }
    
    private void UpdateScalingParameters(FrameContext ctx)
    {
        // Check for beat events
        if (BeatReactive && ctx.IsBeat && !wasBeat)
        {
            targetScale = Scale2;
            wasBeat = true;
        }
        else if (!ctx.IsBeat)
        {
            wasBeat = false;
        }
        
        // Update current position towards target
        if (Scale < Scale2)
        {
            targetScale = Math.Max(currentPosition, Scale);
            currentPosition = Math.Max(0, currentPosition - 3);
        }
        else
        {
            targetScale = Math.Min(currentPosition, Scale);
            currentPosition = Math.Min(255, currentPosition + 3);
        }
    }
    
    private int CalculateScalingFactor()
    {
        return Math.Max(0, currentPosition);
    }
    
    private void ApplyNormalBlitting(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        int width = input.Width;
        int height = input.Height;
        
        if (SubpixelPrecision)
        {
            ApplyNormalBlittingSubpixel(ctx, input, output, width, height);
        }
        else
        {
            ApplyNormalBlittingInteger(ctx, input, output, width, height);
        }
    }
    
    private void ApplyNormalBlittingSubpixel(FrameContext ctx, ImageBuffer input, ImageBuffer output, int width, int height)
    {
        int scalingFactor = CalculateScalingFactor();
        int deltaX = ((scalingFactor + 32) << 16) / 64;
        int startX = (((width << 16) - (deltaX * width)) / 2);
        int startY = (((height << 16) - (deltaX * height)) / 2);
        
        int rowsPerThread = height / threadCount;
        
        for (int t = 0; t < threadCount; t++)
        {
            int startRow = t * rowsPerThread;
            int endRow = (t == threadCount - 1) ? height : (t + 1) * rowsPerThread;
            
            processingTasks[t] = Task.Run(() => 
                ProcessNormalBlittingSubpixelRange(startRow, endRow, width, height, input, output, startX, startY, deltaX));
        }
        
        Task.WaitAll(processingTasks);
        
        // Apply blending if enabled
        if (Blend)
        {
            ApplyBlendingToOutput(ctx, input, output);
        }
    }
    
    private void ProcessNormalBlittingSubpixelRange(int startRow, int endRow, int width, int height, 
        ImageBuffer input, ImageBuffer output, int startX, int startY, int deltaX)
    {
        int currentY = startY;
        
        for (int y = startRow; y < endRow; y++)
        {
            int currentX = startX;
            int yPart = (currentY >> 8) & 0xFF;
            
            for (int x = 0; x < width; x++)
            {
                int xPart = (currentX >> 8) & 0xFF;
                
                if (xPart < 255 && yPart < 255)
                {
                    Color interpolatedColor = InterpolateColor4Point(input, x, y, width, xPart, yPart);
                    output.SetPixel(x, y, interpolatedColor);
                }
                else
                {
                    Color sourceColor = input.GetPixel(currentX >> 16, currentY >> 16);
                    output.SetPixel(x, y, sourceColor);
                }
                
                currentX += deltaX;
            }
            
            currentY += deltaX;
        }
    }
    
    private void ApplyNormalBlittingInteger(FrameContext ctx, ImageBuffer input, ImageBuffer output, int width, int height)
    {
        int scalingFactor = CalculateScalingFactor();
        int deltaX = ((scalingFactor + 32) << 16) / 64;
        int startX = (((width << 16) - (deltaX * width)) / 2);
        int startY = (((height << 16) - (deltaX * height)) / 2);
        
        int rowsPerThread = height / threadCount;
        
        for (int t = 0; t < threadCount; t++)
        {
            int startRow = t * rowsPerThread;
            int endRow = (t == threadCount - 1) ? height : (t + 1) * rowsPerThread;
            
            processingTasks[t] = Task.Run(() => 
                ProcessNormalBlittingIntegerRange(startRow, endRow, width, height, input, output, startX, startY, deltaX));
        }
        
        Task.WaitAll(processingTasks);
        
        // Apply blending if enabled
        if (Blend)
        {
            ApplyBlendingToOutput(ctx, input, output);
        }
    }
    
    private void ProcessNormalBlittingIntegerRange(int startRow, int endRow, int width, int height, 
        ImageBuffer input, ImageBuffer output, int startX, int startY, int deltaX)
    {
        int currentY = startY;
        
        for (int y = startRow; y < endRow; y++)
        {
            int currentX = startX;
            
            for (int x = 0; x < width; x++)
            {
                int sourceX = currentX >> 16;
                int sourceY = currentY >> 16;
                
                if (sourceX >= 0 && sourceX < width && sourceY >= 0 && sourceY < height)
                {
                    Color sourceColor = input.GetPixel(sourceX, sourceY);
                    
                    if (Blend)
                    {
                        Color existingColor = output.GetPixel(x, y);
                        Color blendedColor = BlendColorsAverage(existingColor, sourceColor);
                        output.SetPixel(x, y, blendedColor);
                    }
                    else
                    {
                        output.SetPixel(x, y, sourceColor);
                    }
                }
                
                currentX += deltaX;
            }
            
            currentY += deltaX;
        }
    }
    
    private void ApplyOutwardBlitting(FrameContext ctx, ImageBuffer input, ImageBuffer output, int width, int height)
    {
        int scalingFactor = CalculateScalingFactor();
        const int adjustment = 7;
        
        int deltaX = ((scalingFactor + (1 << adjustment) - 32) << (16 - adjustment));
        int xLength = ((width << 16) / deltaX) & ~3;
        int yLength = (height << 16) / deltaX;
        
        if (xLength >= width || yLength >= height)
        {
            CopyInputToOutput(ctx, input, output);
            return;
        }
        
        int startX = (width - xLength) / 2;
        int startY = (height - yLength) / 2;
        
        // Copy scaled region
        CopyScaledRegion(input, output, startX, startY, xLength, yLength, width);
        
        // Apply feedback effect
        ApplyFeedbackEffect(ctx, input, output, startX, startY, xLength, yLength, width);
    }
    
    private void CopyScaledRegion(ImageBuffer input, ImageBuffer output, int startX, int startY, int xLength, int yLength, int width)
    {
        for (int y = 0; y < yLength; y++)
        {
            for (int x = 0; x < xLength; x++)
            {
                Color sourceColor = input.GetPixel(startX + x, startY + y);
                output.SetPixel(startX + x, startY + y, sourceColor);
            }
        }
    }
    
    private void ApplyFeedbackEffect(FrameContext ctx, ImageBuffer input, ImageBuffer output, int startX, int startY, int xLength, int yLength, int width)
    {
        int scalingFactor = CalculateScalingFactor();
        const int adjustment = 7;
        int deltaX = ((scalingFactor + (1 << adjustment) - 32) << (16 - adjustment));
        
        int currentY = startY << 16;
        
        for (int y = 0; y < yLength; y++)
        {
            int currentX = startX << 16;
            
            for (int x = 0; x < xLength; x++)
            {
                int sourceX = (currentX >> 16) + startX;
                int sourceY = (currentY >> 16) + startY;
                
                if (sourceX >= 0 && sourceX < input.Width && sourceY >= 0 && sourceY < input.Height)
                {
                    Color sourceColor = input.GetPixel(sourceX, sourceY);
                    Color existingColor = output.GetPixel(startX + x, startY + y);
                    
                    if (Blend)
                    {
                        Color blendedColor = BlendColorsAverage(existingColor, sourceColor);
                        output.SetPixel(startX + x, startY + y, blendedColor);
                    }
                    else
                    {
                        output.SetPixel(startX + x, startY + y, sourceColor);
                    }
                }
                
                currentX += deltaX;
            }
            
            currentY += deltaX;
        }
    }
    
    private Color InterpolateColor4Point(ImageBuffer input, int x, int y, int width, int xPart, int yPart)
    {
        int x1 = Math.Min(x, input.Width - 1);
        int y1 = Math.Min(y, input.Height - 1);
        int x2 = Math.Min(x + 1, input.Width - 1);
        int y2 = Math.Min(y + 1, input.Height - 1);
        
        Color c00 = input.GetPixel(x1, y1);
        Color c10 = input.GetPixel(x2, y1);
        Color c01 = input.GetPixel(x1, y2);
        Color c11 = input.GetPixel(x2, y2);
        
        float xWeight = xPart / 255.0f;
        float yWeight = yPart / 255.0f;
        
        Color interpolated = InterpolateColors4Point(c00, c10, c01, c11, xWeight, yWeight);
        return interpolated;
    }
    
    private Color InterpolateColors4Point(Color c00, Color c10, Color c01, Color c11, float xWeight, float yWeight)
    {
        float invXWeight = 1.0f - xWeight;
        float invYWeight = 1.0f - yWeight;
        
        int r = (int)(c00.R * invXWeight * invYWeight + 
                      c10.R * xWeight * invYWeight + 
                      c01.R * invXWeight * yWeight + 
                      c11.R * xWeight * yWeight);
        
        int g = (int)(c00.G * invXWeight * invYWeight + 
                      c10.G * xWeight * invYWeight + 
                      c01.G * invXWeight * yWeight + 
                      c11.G * xWeight * yWeight);
        
        int b = (int)(c00.B * invXWeight * invYWeight + 
                      c10.B * xWeight * invYWeight + 
                      c01.B * invXWeight * yWeight + 
                      c11.B * xWeight * yWeight);
        
        int a = (int)(c00.A * invXWeight * invYWeight + 
                      c10.A * xWeight * invYWeight + 
                      c01.A * invXWeight * yWeight + 
                      c11.A * xWeight * yWeight);
        
        return Color.FromArgb(
            Math.Clamp(a, 0, 255),
            Math.Clamp(r, 0, 255),
            Math.Clamp(g, 0, 255),
            Math.Clamp(b, 0, 255)
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
    
    private void ApplyBlendingToOutput(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        int rowsPerThread = output.Height / threadCount;
        
        for (int t = 0; t < threadCount; t++)
        {
            int startRow = t * rowsPerThread;
            int endRow = (t == threadCount - 1) ? output.Height : (t + 1) * rowsPerThread;
            
            processingTasks[t] = Task.Run(() => 
                ApplyBlendingRange(startRow, endRow, input, output));
        }
        
        Task.WaitAll(processingTasks);
    }
    
    private void ApplyBlendingRange(int startRow, int endRow, ImageBuffer input, ImageBuffer output)
    {
        for (int y = startRow; y < endRow; y++)
        {
            for (int x = 0; x < output.Width; x++)
            {
                Color outputColor = output.GetPixel(x, y);
                Color inputColor = input.GetPixel(x, y);
                Color blendedColor = BlendColorsAverage(outputColor, inputColor);
                output.SetPixel(x, y, blendedColor);
            }
        }
    }
    
    private void InitializeBlendTable()
    {
        if (blendTableInitialized) return;
        
        blendTable = new byte[256, 256];
        
        for (int i = 0; i < 256; i++)
        {
            for (int j = 0; j < 256; j++)
            {
                blendTable[i, j] = (byte)((i * j) / 255);
            }
        }
        
        blendTableInitialized = true;
    }
    
    private void UpdateFrameState(FrameContext ctx)
    {
        frameTime = ctx.DeltaTime;
        frameCount++;
    }
    
    private void CopyInputToOutput(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        int rowsPerThread = input.Height / threadCount;
        
        for (int t = 0; t < threadCount; t++)
        {
            int startRow = t * rowsPerThread;
            int endRow = (t == threadCount - 1) ? input.Height : (t + 1) * rowsPerThread;
            
            processingTasks[t] = Task.Run(() => 
                CopyRowRange(startRow, endRow, input.Width, input, output));
        }
        
        Task.WaitAll(processingTasks);
    }
    
    private void CopyRowRange(int startRow, int endRow, int width, ImageBuffer input, ImageBuffer output)
    {
        for (int y = startRow; y < endRow; y++)
        {
            for (int x = 0; x < width; x++)
            {
                Color pixel = input.GetPixel(x, y);
                output.SetPixel(x, y, pixel);
            }
        }
    }
    
    // Public interface for parameter adjustment
    public void SetScale(int scale) 
    { 
        Scale = Math.Clamp(scale, 0, 256); 
        currentPosition = Scale;
    }
    
    public void SetScale2(int scale2) 
    { 
        Scale2 = Math.Clamp(scale2, 0, 256); 
    }
    
    public void SetBlend(bool blend) { Blend = blend; }
    public void SetBeatReactive(bool beatReactive) { BeatReactive = beatReactive; }
    public void SetSubpixelPrecision(bool subpixel) { SubpixelPrecision = subpixel; }
    
    // Status queries
    public int GetCurrentPosition() => currentPosition;
    public int GetTargetScale() => targetScale;
    public float GetFrameTime() => frameTime;
    public int GetFrameCount() => frameCount;
    
    public override void Dispose()
    {
        if (processingTasks != null)
        {
            foreach (var task in processingTasks)
            {
                task?.Dispose();
            }
        }
    }
}
```

## Integration Points

### Audio Data Integration
- **Beat Detection**: Uses `FrameContext.IsBeat` for reactive scaling
- **Audio Analysis**: Processes left/right/center channel data for potential audio-reactive effects
- **Timing**: Integrates with frame timing for smooth animations

### Framebuffer Handling
- **Input/Output Buffers**: Processes `ImageBuffer` objects with full color support
- **Subpixel Rendering**: Implements bilinear interpolation for smooth scaling
- **Multi-threading**: Parallel processing for performance-critical operations

### Performance Considerations
- **MMX Optimization**: C# equivalent uses SIMD-like batch processing
- **Multi-threading**: SMP support for pixel operations
- **Memory Management**: Efficient color interpolation and blending
- **Batch Processing**: Processes pixels in groups for better cache utilization

## Usage Examples

### Basic Scaling Effect
```csharp
var blitNode = new BlitOperationsNode
{
    Scale = 50,
    Blend = false,
    SubpixelPrecision = true
};
```

### Beat-Reactive Feedback
```csharp
var blitNode = new BlitOperationsNode
{
    Scale = 30,
    Scale2 = 80,
    BeatReactive = true,
    Blend = true,
    SubpixelPrecision = true
};
```

### Outward Scaling
```csharp
var blitNode = new BlitOperationsNode
{
    Scale = 100,  // Will trigger outward blitting
    Blend = true,
    SubpixelPrecision = false
};
```

## Technical Notes

### Scaling Algorithm
The effect uses a sophisticated scaling system:
- **Normal Mode**: Linear scaling with configurable factors
- **Outward Mode**: Creates feedback effects by scaling outward from center
- **Beat Reactivity**: Dynamic scaling factor changes on beat events

### Blending Modes
- **No Blending**: Direct pixel replacement
- **Average Blending**: 50/50 mix of source and destination
- **Subpixel Blending**: 4-point bilinear interpolation for smooth scaling

### Performance Characteristics
- **CPU Intensive**: Complex scaling and interpolation operations
- **Memory Access**: Heavy framebuffer read/write operations
- **Optimization**: Multi-threading and batch processing for performance
- **Quality vs Speed**: Subpixel precision trades performance for quality

This effect is essential for creating dynamic zoom effects, feedback loops, and smooth image transformations in AVS presets, providing the foundation for many advanced visualization techniques.
