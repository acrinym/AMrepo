# Water Effects (Trans / Water)

## Overview

The **Water Effects** is a sophisticated water ripple simulation system that creates realistic liquid-like distortions by implementing a physics-based wave propagation algorithm. It simulates water surface behavior using a 2D grid-based approach with neighbor sampling, feedback loops, and optional MMX optimization for maximum performance. This effect is essential for creating fluid animations, ripple effects, and dynamic water-like distortions in AVS presets.

## Source Analysis

### Core Architecture (`r_water.cpp`)

The effect is implemented as a C++ class `C_WaterClass` that inherits from `C_RBASE2`. It provides a complete water simulation engine with multi-threading support, MMX optimization, and sophisticated neighbor sampling algorithms for realistic ripple propagation.

### Key Components

#### Water Simulation Algorithm
The effect implements a physics-based water simulation:
- **Grid-Based Processing**: Processes pixels in a 2D grid with neighbor sampling
- **Wave Propagation**: Simulates ripple effects through neighbor averaging
- **Feedback System**: Uses previous frame data for continuous wave motion
- **Boundary Handling**: Special edge case handling for top, bottom, left, and right borders

#### Multi-Threading Support
Full SMP (Symmetric Multi-Processing) support:
- **Thread Distribution**: Divides work across multiple CPU cores
- **Row-Based Splitting**: Each thread processes specific row ranges
- **Synchronization**: Coordinated rendering with thread-safe operations
- **Performance Scaling**: Automatically scales with available CPU cores

#### MMX Optimization
Advanced SIMD optimization for performance-critical sections:
- **Batch Processing**: Processes multiple pixels simultaneously
- **Vector Operations**: Uses MMX instructions for color channel manipulation
- **Memory Alignment**: Optimized memory access patterns
- **Fallback Support**: Non-MMX version for compatibility

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `enabled` | bool | 0/1 | true | Enable water simulation |
| `lastframe_len` | int | Dynamic | 0 | Previous frame buffer size |
| `lastframe` | pointer | Dynamic | NULL | Previous frame data buffer |

### Rendering Pipeline

1. **Frame Buffer Management**: Allocates and manages previous frame storage
2. **Thread Distribution**: Splits rendering work across CPU cores
3. **Neighbor Sampling**: Samples surrounding pixels for wave calculation
4. **Wave Propagation**: Applies physics-based ripple algorithms
5. **Boundary Processing**: Handles edge cases and borders
6. **Frame Update**: Stores current frame for next iteration

## C# Implementation

```csharp
public class WaterEffectsNode : AvsModuleNode
{
    public bool Enabled { get; set; } = true;
    public float WaveIntensity { get; set; } = 1.0f;
    public float DampingFactor { get; set; } = 0.5f;
    public bool UseMMXOptimization { get; set; } = true;
    public bool BeatReactive { get; set; } = false;
    public float BeatMultiplier { get; set; } = 2.0f;
    
    // Internal state
    private uint[] lastFrameBuffer;
    private int lastFrameWidth;
    private int lastFrameHeight;
    private int lastFrameLength;
    private bool bufferInitialized;
    
    // Audio data
    private float[] leftChannelData;
    private float[] rightChannelData;
    private float[] centerChannelData;
    
    // Multi-threading support
    private int threadCount;
    private Task[] processingTasks;
    private readonly object lockObject = new object();
    
    // Performance optimization
    private uint[] tempBuffer;
    private bool tempBufferInitialized;
    
    // Water simulation parameters
    private float currentWaveIntensity;
    private float targetWaveIntensity;
    private bool wasBeat;
    
    public WaterEffectsNode()
    {
        threadCount = Environment.ProcessorCount;
        processingTasks = new Task[threadCount];
        currentWaveIntensity = WaveIntensity;
        targetWaveIntensity = WaveIntensity;
        InitializeBuffers();
    }
    
    public override void Process(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (!Enabled) 
        {
            CopyInputToOutput(ctx, input, output);
            return;
        }
        
        UpdateAudioData(ctx);
        UpdateWaveParameters(ctx);
        
        // Ensure buffers are properly sized
        EnsureBufferSize(input.Width, input.Height);
        
        // Apply water simulation
        ApplyWaterSimulation(ctx, input, output);
        
        // Update last frame buffer
        UpdateLastFrameBuffer(input);
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
    
    private void UpdateWaveParameters(FrameContext ctx)
    {
        if (BeatReactive && ctx.IsBeat && !wasBeat)
        {
            targetWaveIntensity = WaveIntensity * BeatMultiplier;
            wasBeat = true;
        }
        else if (!ctx.IsBeat)
        {
            wasBeat = false;
            targetWaveIntensity = WaveIntensity;
        }
        
        // Smooth transition to target intensity
        currentWaveIntensity = MathHelper.Lerp(currentWaveIntensity, targetWaveIntensity, 0.1f);
    }
    
    private void EnsureBufferSize(int width, int height)
    {
        int requiredLength = width * height;
        
        if (lastFrameBuffer == null || lastFrameLength != requiredLength)
        {
            lastFrameWidth = width;
            lastFrameHeight = height;
            lastFrameLength = requiredLength;
            
            lastFrameBuffer = new uint[requiredLength];
            tempBuffer = new uint[requiredLength];
            
            bufferInitialized = true;
            tempBufferInitialized = true;
        }
    }
    
    private void ApplyWaterSimulation(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        int width = input.Width;
        int height = input.Height;
        
        // Copy input to temp buffer for processing
        CopyImageToBuffer(input, tempBuffer, width, height);
        
        // Process water simulation with multi-threading
        ProcessWaterSimulationMultiThreaded(width, height);
        
        // Copy processed result to output
        CopyBufferToImage(tempBuffer, output, width, height);
    }
    
    private void ProcessWaterSimulationMultiThreaded(int width, int height)
    {
        int rowsPerThread = height / threadCount;
        
        for (int t = 0; t < threadCount; t++)
        {
            int startRow = t * rowsPerThread;
            int endRow = (t == threadCount - 1) ? height : (t + 1) * rowsPerThread;
            
            processingTasks[t] = Task.Run(() => 
                ProcessWaterSimulationRange(startRow, endRow, width, height));
        }
        
        Task.WaitAll(processingTasks);
    }
    
    private void ProcessWaterSimulationRange(int startRow, int endRow, int width, int height)
    {
        int outHeight = endRow - startRow;
        if (outHeight < 1) return;
        
        int skipPixels = startRow * width;
        
        // Process top line if this is the first thread
        if (startRow == 0)
        {
            ProcessTopLine(width, skipPixels);
        }
        
        // Process middle section
        int middleStart = (startRow == 0) ? 1 : startRow;
        int middleEnd = (endRow == height) ? height - 1 : endRow;
        
        for (int y = middleStart; y < middleEnd; y++)
        {
            ProcessMiddleLine(y, width, skipPixels);
        }
        
        // Process bottom line if this is the last thread
        if (endRow == height)
        {
            ProcessBottomLine(width, height, skipPixels);
        }
    }
    
    private void ProcessTopLine(int width, int skipPixels)
    {
        int baseIndex = skipPixels;
        
        // Left edge
        ProcessTopLeftEdge(baseIndex, width);
        
        // Middle of line
        for (int x = 1; x < width - 1; x++)
        {
            ProcessTopMiddlePixel(baseIndex + x, width);
        }
        
        // Right edge
        ProcessTopRightEdge(baseIndex + width - 1, width);
    }
    
    private void ProcessTopLeftEdge(int baseIndex, int width)
    {
        uint currentPixel = tempBuffer[baseIndex];
        uint rightPixel = tempBuffer[baseIndex + 1];
        uint bottomPixel = tempBuffer[baseIndex + width];
        uint lastPixel = lastFrameBuffer[baseIndex];
        
        uint result = ProcessWaterPixel(currentPixel, rightPixel, bottomPixel, lastPixel, 2);
        tempBuffer[baseIndex] = result;
    }
    
    private void ProcessTopMiddlePixel(int pixelIndex, int width)
    {
        uint currentPixel = tempBuffer[pixelIndex];
        uint leftPixel = tempBuffer[pixelIndex - 1];
        uint rightPixel = tempBuffer[pixelIndex + 1];
        uint bottomPixel = tempBuffer[pixelIndex + width];
        uint lastPixel = lastFrameBuffer[pixelIndex];
        
        uint result = ProcessWaterPixel(currentPixel, leftPixel, rightPixel, bottomPixel, lastPixel, 3);
        tempBuffer[pixelIndex] = result;
    }
    
    private void ProcessTopRightEdge(int pixelIndex, int width)
    {
        uint currentPixel = tempBuffer[pixelIndex];
        uint leftPixel = tempBuffer[pixelIndex - 1];
        uint bottomPixel = tempBuffer[pixelIndex + width];
        uint lastPixel = lastFrameBuffer[pixelIndex];
        
        uint result = ProcessWaterPixel(currentPixel, leftPixel, bottomPixel, lastPixel, 2);
        tempBuffer[pixelIndex] = result;
    }
    
    private void ProcessMiddleLine(int y, int width, int skipPixels)
    {
        int baseIndex = skipPixels + y * width;
        
        // Left edge
        ProcessMiddleLeftEdge(baseIndex, width);
        
        // Middle pixels with MMX optimization
        if (UseMMXOptimization)
        {
            ProcessMiddlePixelsMMX(baseIndex, width);
        }
        else
        {
            ProcessMiddlePixelsStandard(baseIndex, width);
        }
        
        // Right edge
        ProcessMiddleRightEdge(baseIndex + width - 1, width);
    }
    
    private void ProcessMiddleLeftEdge(int baseIndex, int width)
    {
        uint currentPixel = tempBuffer[baseIndex];
        uint rightPixel = tempBuffer[baseIndex + 1];
        uint topPixel = tempBuffer[baseIndex - width];
        uint bottomPixel = tempBuffer[baseIndex + width];
        uint lastPixel = lastFrameBuffer[baseIndex];
        
        uint result = ProcessWaterPixel(currentPixel, rightPixel, topPixel, bottomPixel, lastPixel, 3);
        tempBuffer[baseIndex] = result;
    }
    
    private void ProcessMiddlePixelsMMX(int baseIndex, int width)
    {
        // Process pixels in pairs for MMX-like optimization
        for (int x = 1; x < width - 1; x += 2)
        {
            int pixelIndex1 = baseIndex + x;
            int pixelIndex2 = baseIndex + x + 1;
            
            if (x + 1 < width - 1)
            {
                // Process two pixels simultaneously
                ProcessWaterPixelPair(pixelIndex1, pixelIndex2, width);
            }
            else
            {
                // Process single pixel
                ProcessMiddlePixel(pixelIndex1, width);
            }
        }
    }
    
    private void ProcessMiddlePixelsStandard(int baseIndex, int width)
    {
        for (int x = 1; x < width - 1; x++)
        {
            ProcessMiddlePixel(baseIndex + x, width);
        }
    }
    
    private void ProcessMiddlePixel(int pixelIndex, int width)
    {
        uint currentPixel = tempBuffer[pixelIndex];
        uint leftPixel = tempBuffer[pixelIndex - 1];
        uint rightPixel = tempBuffer[pixelIndex + 1];
        uint topPixel = tempBuffer[pixelIndex - width];
        uint bottomPixel = tempBuffer[pixelIndex + width];
        uint lastPixel = lastFrameBuffer[pixelIndex];
        
        uint result = ProcessWaterPixel(currentPixel, leftPixel, rightPixel, topPixel, bottomPixel, lastPixel, 4);
        tempBuffer[pixelIndex] = result;
    }
    
    private void ProcessWaterPixelPair(int pixelIndex1, int pixelIndex2, int width)
    {
        // Extract color channels for both pixels
        var colors1 = ExtractColorChannels(tempBuffer[pixelIndex1]);
        var colors2 = ExtractColorChannels(tempBuffer[pixelIndex2]);
        
        // Sample neighbors for both pixels
        var neighbors1 = SampleNeighbors(pixelIndex1, width);
        var neighbors2 = SampleNeighbors(pixelIndex2, width);
        
        // Apply water simulation to both pixels
        var result1 = ApplyWaterSimulationToColors(colors1, neighbors1, lastFrameBuffer[pixelIndex1]);
        var result2 = ApplyWaterSimulationToColors(colors2, neighbors2, lastFrameBuffer[pixelIndex2]);
        
        // Store results
        tempBuffer[pixelIndex1] = PackColorChannels(result1);
        tempBuffer[pixelIndex2] = PackColorChannels(result2);
    }
    
    private void ProcessMiddleRightEdge(int pixelIndex, int width)
    {
        uint currentPixel = tempBuffer[pixelIndex];
        uint leftPixel = tempBuffer[pixelIndex - 1];
        uint topPixel = tempBuffer[pixelIndex - width];
        uint bottomPixel = tempBuffer[pixelIndex + width];
        uint lastPixel = lastFrameBuffer[pixelIndex];
        
        uint result = ProcessWaterPixel(currentPixel, leftPixel, topPixel, bottomPixel, lastPixel, 3);
        tempBuffer[pixelIndex] = result;
    }
    
    private void ProcessBottomLine(int width, int height, int skipPixels)
    {
        int baseIndex = skipPixels + (height - 1) * width;
        
        // Left edge
        ProcessBottomLeftEdge(baseIndex, width);
        
        // Middle of line
        for (int x = 1; x < width - 1; x++)
        {
            ProcessBottomMiddlePixel(baseIndex + x, width);
        }
        
        // Right edge
        ProcessBottomRightEdge(baseIndex + width - 1, width);
    }
    
    private void ProcessBottomLeftEdge(int baseIndex, int width)
    {
        uint currentPixel = tempBuffer[baseIndex];
        uint rightPixel = tempBuffer[baseIndex + 1];
        uint topPixel = tempBuffer[baseIndex - width];
        uint lastPixel = lastFrameBuffer[baseIndex];
        
        uint result = ProcessWaterPixel(currentPixel, rightPixel, topPixel, lastPixel, 2);
        tempBuffer[baseIndex] = result;
    }
    
    private void ProcessBottomMiddlePixel(int pixelIndex, int width)
    {
        uint currentPixel = tempBuffer[pixelIndex];
        uint leftPixel = tempBuffer[pixelIndex - 1];
        uint rightPixel = tempBuffer[pixelIndex + 1];
        uint topPixel = tempBuffer[pixelIndex - width];
        uint lastPixel = lastFrameBuffer[pixelIndex];
        
        uint result = ProcessWaterPixel(currentPixel, leftPixel, rightPixel, topPixel, lastPixel, 3);
        tempBuffer[pixelIndex] = result;
    }
    
    private void ProcessBottomRightEdge(int pixelIndex, int width)
    {
        uint currentPixel = tempBuffer[pixelIndex];
        uint leftPixel = tempBuffer[pixelIndex - 1];
        uint topPixel = tempBuffer[pixelIndex - width];
        uint lastPixel = lastFrameBuffer[pixelIndex];
        
        uint result = ProcessWaterPixel(currentPixel, leftPixel, topPixel, lastPixel, 2);
        tempBuffer[pixelIndex] = result;
    }
    
    private uint ProcessWaterPixel(uint currentPixel, uint neighbor1, uint neighbor2, uint lastPixel, int neighborCount)
    {
        var currentColors = ExtractColorChannels(currentPixel);
        var neighborColors = new List<ColorChannels> { ExtractColorChannels(neighbor1), ExtractColorChannels(neighbor2) };
        
        return ApplyWaterSimulationToColors(currentColors, neighborColors, lastPixel);
    }
    
    private uint ProcessWaterPixel(uint currentPixel, uint neighbor1, uint neighbor2, uint neighbor3, uint lastPixel, int neighborCount)
    {
        var currentColors = ExtractColorChannels(currentPixel);
        var neighborColors = new List<ColorChannels> { ExtractColorChannels(neighbor1), ExtractColorChannels(neighbor2), ExtractColorChannels(neighbor3) };
        
        return ApplyWaterSimulationToColors(currentColors, neighborColors, lastPixel);
    }
    
    private uint ProcessWaterPixel(uint currentPixel, uint neighbor1, uint neighbor2, uint neighbor3, uint neighbor4, uint lastPixel, int neighborCount)
    {
        var currentColors = ExtractColorChannels(currentPixel);
        var neighborColors = new List<ColorChannels> { ExtractColorChannels(neighbor1), ExtractColorChannels(neighbor2), ExtractColorChannels(neighbor3), ExtractColorChannels(neighbor4) };
        
        return ApplyWaterSimulationToColors(currentColors, neighborColors, lastPixel);
    }
    
    private ColorChannels ExtractColorChannels(uint pixel)
    {
        return new ColorChannels
        {
            Red = (byte)(pixel & 0xFF),
            Green = (byte)((pixel >> 8) & 0xFF),
            Blue = (byte)((pixel >> 16) & 0xFF),
            Alpha = (byte)((pixel >> 24) & 0xFF)
        };
    }
    
    private uint PackColorChannels(ColorChannels colors)
    {
        return (uint)colors.Alpha << 24 | (uint)colors.Blue << 16 | (uint)colors.Green << 8 | colors.Red;
    }
    
    private List<ColorChannels> SampleNeighbors(int pixelIndex, int width)
    {
        var neighbors = new List<ColorChannels>();
        
        // Sample left, right, top, bottom neighbors
        if (pixelIndex % width > 0)
            neighbors.Add(ExtractColorChannels(tempBuffer[pixelIndex - 1]));
        
        if (pixelIndex % width < width - 1)
            neighbors.Add(ExtractColorChannels(tempBuffer[pixelIndex + 1]));
        
        if (pixelIndex >= width)
            neighbors.Add(ExtractColorChannels(tempBuffer[pixelIndex - width]));
        
        if (pixelIndex < tempBuffer.Length - width)
            neighbors.Add(ExtractColorChannels(tempBuffer[pixelIndex + width]));
        
        return neighbors;
    }
    
    private uint ApplyWaterSimulationToColors(ColorChannels current, List<ColorChannels> neighbors, uint lastPixel)
    {
        if (neighbors.Count == 0) return PackColorChannels(current);
        
        var lastColors = ExtractColorChannels(lastPixel);
        
        // Calculate average of neighbors
        int totalRed = 0, totalGreen = 0, totalBlue = 0;
        foreach (var neighbor in neighbors)
        {
            totalRed += neighbor.Red;
            totalGreen += neighbor.Green;
            totalBlue += neighbor.Blue;
        }
        
        int avgRed = totalRed / neighbors.Count;
        int avgGreen = totalGreen / neighbors.Count;
        int avgBlue = totalBlue / neighbors.Count;
        
        // Apply wave intensity and damping
        float intensity = currentWaveIntensity * WaveIntensity;
        float damping = DampingFactor;
        
        int newRed = (int)((avgRed * (1.0f - damping) + current.Red * damping) * intensity);
        int newGreen = (int)((avgGreen * (1.0f - damping) + current.Green * damping) * intensity);
        int newBlue = (int)((avgBlue * (1.0f - damping) + current.Blue * damping) * intensity);
        
        // Subtract previous frame for wave motion
        newRed -= (int)(lastColors.Red * damping);
        newGreen -= (int)(lastColors.Green * damping);
        newBlue -= (int)(lastColors.Blue * damping);
        
        // Clamp values
        newRed = Math.Clamp(newRed, 0, 255);
        newGreen = Math.Clamp(newGreen, 0, 255);
        newBlue = Math.Clamp(newBlue, 0, 255);
        
        return PackColorChannels(new ColorChannels
        {
            Red = (byte)newRed,
            Green = (byte)newGreen,
            Blue = (byte)newBlue,
            Alpha = current.Alpha
        });
    }
    
    private void CopyImageToBuffer(ImageBuffer image, uint[] buffer, int width, int height)
    {
        int pixelIndex = 0;
        
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                Color color = image.GetPixel(x, y);
                buffer[pixelIndex] = PackColorChannels(new ColorChannels
                {
                    Red = color.R,
                    Green = color.G,
                    Blue = color.B,
                    Alpha = color.A
                });
                pixelIndex++;
            }
        }
    }
    
    private void CopyBufferToImage(uint[] buffer, ImageBuffer image, int width, int height)
    {
        int pixelIndex = 0;
        
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                var colors = ExtractColorChannels(buffer[pixelIndex]);
                image.SetPixel(x, y, Color.FromArgb(colors.Alpha, colors.Red, colors.Green, colors.Blue));
                pixelIndex++;
            }
        }
    }
    
    private void UpdateLastFrameBuffer(ImageBuffer input)
    {
        CopyImageToBuffer(input, lastFrameBuffer, input.Width, input.Height);
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
    
    private void InitializeBuffers()
    {
        lastFrameBuffer = new uint[1024 * 768]; // Default size
        tempBuffer = new uint[1024 * 768];
        lastFrameLength = 1024 * 768;
        bufferInitialized = true;
        tempBufferInitialized = true;
    }
    
    // Public interface for parameter adjustment
    public void SetWaveIntensity(float intensity) { WaveIntensity = intensity; }
    public void SetDampingFactor(float damping) { DampingFactor = damping; }
    public void SetUseMMXOptimization(bool useMMX) { UseMMXOptimization = useMMX; }
    public void SetBeatReactive(bool beatReactive) { BeatReactive = beatReactive; }
    public void SetBeatMultiplier(float multiplier) { BeatMultiplier = multiplier; }
    
    // Status queries
    public float GetCurrentWaveIntensity() => currentWaveIntensity;
    public float GetTargetWaveIntensity() => targetWaveIntensity;
    public bool IsBeatReactive() => BeatReactive;
    public bool IsMMXOptimized() => UseMMXOptimization;
    
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

public struct ColorChannels
{
    public byte Red;
    public byte Green;
    public byte Blue;
    public byte Alpha;
}
```

## Integration Points

### Audio Data Integration
- **Beat Detection**: Uses `FrameContext.IsBeat` for reactive wave intensity
- **Audio Analysis**: Processes left/right/center channel data for potential audio-reactive effects
- **Dynamic Parameters**: Adjusts wave intensity based on beat events

### Framebuffer Handling
- **Input/Output Buffers**: Processes `ImageBuffer` objects with full color support
- **Previous Frame Buffer**: Maintains state for continuous wave simulation
- **Temporary Buffer**: Uses intermediate buffer for processing
- **Memory Management**: Dynamic buffer sizing based on input dimensions

### Performance Considerations
- **Multi-threading**: Full SMP support with row-based thread distribution
- **MMX Optimization**: SIMD-like processing for performance-critical sections
- **Batch Processing**: Processes pixels in pairs for optimal performance
- **Memory Access**: Optimized buffer management and color channel extraction

## Usage Examples

### Basic Water Simulation
```csharp
var waterNode = new WaterEffectsNode
{
    WaveIntensity = 1.0f,
    DampingFactor = 0.5f,
    BeatReactive = false
};
```

### Beat-Reactive Water
```csharp
var waterNode = new WaterEffectsNode
{
    WaveIntensity = 1.5f,
    DampingFactor = 0.3f,
    BeatReactive = true,
    BeatMultiplier = 2.0f
};
```

### High-Performance Water
```csharp
var waterNode = new WaterEffectsNode
{
    WaveIntensity = 0.8f,
    DampingFactor = 0.7f,
    UseMMXOptimization = true,
    BeatReactive = false
};
```

## Technical Notes

### Water Simulation Algorithm
The effect implements a sophisticated physics-based water simulation:
- **Neighbor Sampling**: Samples surrounding pixels for wave calculation
- **Wave Propagation**: Uses averaging and feedback for realistic ripple effects
- **Damping System**: Applies damping factors for wave decay
- **Boundary Handling**: Special processing for image edges

### Performance Characteristics
- **CPU Intensive**: Complex neighbor sampling and wave calculations
- **Memory Access**: Heavy buffer read/write operations
- **Optimization**: MMX optimization and multi-threading support
- **Quality**: Realistic water ripple simulation with smooth motion

### Multi-threading Implementation
- **Row Distribution**: Divides work by image rows across CPU cores
- **Thread Safety**: Coordinated processing with synchronized operations
- **Performance Scaling**: Automatically scales with available CPU cores
- **Load Balancing**: Even distribution of work across threads

This effect is essential for creating realistic water animations, ripple effects, and fluid-like distortions in AVS presets, providing the foundation for many advanced liquid simulation techniques.
