# Picture Effects (Render / Picture)

## Overview

The **Picture Effects** system is a sophisticated image rendering engine that loads bitmap files and applies them to the visualization with various blending modes, aspect ratio preservation, and beat-reactive persistence. It provides a complete image overlay system with support for BMP files, multiple blending algorithms, adaptive rendering, and intelligent scaling. This effect is essential for creating image-based visualizations, overlays, and beat-reactive image sequences in AVS presets.

## Source Analysis

### Core Architecture (`r_picture.cpp`)

The effect is implemented as a C++ class `C_PictureClass` that inherits from `C_RBASE`. It provides a complete image loading, scaling, and rendering system with GDI integration, multiple blending modes, and intelligent aspect ratio handling.

### Key Components

#### Image Loading System
Sophisticated bitmap handling:
- **File Loading**: Loads BMP files from the preset directory
- **Memory Management**: Efficient bitmap storage and cleanup
- **Format Support**: Native Windows bitmap format support
- **Path Resolution**: Automatic path resolution for preset files

#### Rendering Engine
Advanced rendering with multiple options:
- **Blending Modes**: Replace, additive, 50/50, and adaptive blending
- **Aspect Ratio Preservation**: X-axis or Y-axis ratio maintenance
- **Intelligent Scaling**: Automatic scaling to fit screen dimensions
- **Performance Optimization**: Efficient GDI operations and memory management

#### Beat Reactivity System
Dynamic image behavior based on audio:
- **Adaptive Rendering**: Beat-reactive image persistence
- **Persistence Control**: Configurable persistence duration
- **Blend Mode Switching**: Automatic blend mode changes on beats
- **Countdown System**: Gradual fade-out after beat events

#### GDI Integration
Deep Windows graphics integration:
- **Device Contexts**: Efficient bitmap manipulation
- **Stretch Blitting**: High-quality image scaling
- **Memory DCs**: Optimized bitmap operations
- **Resource Management**: Proper cleanup and memory handling

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `enabled` | int | 0-1 | 1 | Enable picture rendering |
| `blend` | int | 0-1 | 0 | Enable additive blending |
| `blendavg` | int | 0-1 | 1 | Enable 50/50 blending |
| `adapt` | int | 0-1 | 0 | Enable adaptive blending |
| `persist` | int | 0-32 | 6 | Beat persistence duration |
| `ratio` | int | 0-1 | 0 | Enable aspect ratio preservation |
| `axis_ratio` | int | 0-1 | 0 | Aspect ratio axis (0=X, 1=Y) |
| `ascName` | string | File path | "" | Bitmap file path |

### Blending Modes

| Mode | Description | Behavior |
|------|-------------|----------|
| **Replace** | Direct replacement | Image completely replaces background |
| **Additive** | Additive blending | Image adds to background colors |
| **50/50** | Average blending | Image and background are averaged |
| **Adaptive** | Beat-reactive | Switches between modes based on beats |

### Rendering Pipeline

1. **Image Loading**: Load and validate bitmap file
2. **Screen Detection**: Detect screen size changes
3. **Image Scaling**: Scale image to fit screen dimensions
4. **Aspect Ratio**: Apply aspect ratio preservation if enabled
5. **Blending Selection**: Choose appropriate blending mode
6. **Pixel Processing**: Apply blending algorithm to each pixel
7. **Beat Reactivity**: Handle beat events and persistence

## C# Implementation

```csharp
public class PictureEffectsNode : AvsModuleNode
{
    public bool Enabled { get; set; } = true;
    public bool EnableAdditiveBlending { get; set; } = false;
    public bool EnableAverageBlending { get; set; } = true;
    public bool EnableAdaptiveBlending { get; set; } = false;
    public int PersistenceDuration { get; set; } = 6;
    public bool PreserveAspectRatio { get; set; } = false;
    public AspectRatioAxis AspectRatioAxis { get; set; } = AspectRatioAxis.X;
    public string ImagePath { get; set; } = "";
    
    // Internal state
    private Image loadedImage;
    private int imageWidth, imageHeight;
    private int lastScreenWidth, lastScreenHeight;
    private bool imageValid;
    private int persistenceCount;
    private bool wasBeat;
    
    // Performance optimization
    private Color[] scaledImageBuffer;
    private bool bufferValid;
    private readonly object imageLock = new object();
    
    // Blending constants
    private const int MaxPersistence = 32;
    private const int MinPersistence = 0;
    
    public PictureEffectsNode()
    {
        persistenceCount = 0;
        wasBeat = false;
        InitializeImageSystem();
    }
    
    public override void Process(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (!Enabled || !imageValid) 
        {
            CopyInputToOutput(ctx, input, output);
            return;
        }
        
        // Update image if screen size changed
        UpdateImageForScreenSize(ctx);
        
        // Handle beat events and persistence
        UpdateBeatReactivity(ctx);
        
        // Apply image with selected blending mode
        RenderImageWithBlending(ctx, input, output);
    }
    
    private void InitializeImageSystem()
    {
        loadedImage = null;
        imageWidth = 0;
        imageHeight = 0;
        lastScreenWidth = 0;
        lastScreenHeight = 0;
        imageValid = false;
        scaledImageBuffer = null;
        bufferValid = false;
    }
    
    public void LoadImage(string imagePath)
    {
        lock (imageLock)
        {
            try
            {
                // Unload previous image
                UnloadImage();
                
                if (string.IsNullOrEmpty(imagePath))
                {
                    ImagePath = "";
                    return;
                }
                
                // Load new image
                loadedImage = LoadBitmapFromFile(imagePath);
                if (loadedImage != null)
                {
                    ImagePath = imagePath;
                    imageWidth = loadedImage.Width;
                    imageHeight = loadedImage.Height;
                    imageValid = true;
                    bufferValid = false;
                }
            }
            catch (Exception ex)
            {
                // Handle loading errors gracefully
                UnloadImage();
            }
        }
    }
    
    private Image LoadBitmapFromFile(string imagePath)
    {
        try
        {
            // Try to load as bitmap
            if (Path.GetExtension(imagePath).ToLower() == ".bmp")
            {
                return LoadBmpFile(imagePath);
            }
            else
            {
                // Fallback to general image loading
                return Image.FromFile(imagePath);
            }
        }
        catch
        {
            return null;
        }
    }
    
    private Image LoadBmpFile(string imagePath)
    {
        try
        {
            using (var stream = new FileStream(imagePath, FileMode.Open, FileAccess.Read))
            {
                // Read BMP header
                var reader = new BinaryReader(stream);
                
                // Check BMP signature
                if (reader.ReadUInt16() != 0x4D42) // "BM"
                    return null;
                
                // Skip file size and reserved fields
                reader.BaseStream.Position = 18;
                
                // Read width and height
                int width = reader.ReadInt32();
                int height = reader.ReadInt32();
                
                // Skip other header fields
                reader.BaseStream.Position = 54;
                
                // Create bitmap
                var bitmap = new Bitmap(width, height);
                
                // Read pixel data (bottom-up for BMP)
                for (int y = height - 1; y >= 0; y--)
                {
                    for (int x = 0; x < width; x++)
                    {
                        // Read BGR values (BMP format)
                        byte blue = reader.ReadByte();
                        byte green = reader.ReadByte();
                        byte red = reader.ReadByte();
                        
                        // Skip alpha if present
                        if (width % 4 != 0)
                        {
                            reader.BaseStream.Position += 4 - (width % 4);
                        }
                        
                        bitmap.SetPixel(x, y, Color.FromArgb(255, red, green, blue));
                    }
                }
                
                return bitmap;
            }
        }
        catch
        {
            return null;
        }
    }
    
    private void UnloadImage()
    {
        lock (imageLock)
        {
            if (loadedImage != null)
            {
                loadedImage.Dispose();
                loadedImage = null;
            }
            
            imageWidth = 0;
            imageHeight = 0;
            imageValid = false;
            bufferValid = false;
            
            if (scaledImageBuffer != null)
            {
                scaledImageBuffer = null;
            }
        }
    }
    
    private void UpdateImageForScreenSize(FrameContext ctx)
    {
        lock (imageLock)
        {
            if (!imageValid) return;
            
            if (lastScreenWidth != ctx.Width || lastScreenHeight != ctx.Height)
            {
                lastScreenWidth = ctx.Width;
                lastScreenHeight = ctx.Height;
                bufferValid = false;
                
                // Reallocate scaled image buffer
                scaledImageBuffer = new Color[ctx.Width * ctx.Height];
            }
            
            if (!bufferValid)
            {
                GenerateScaledImage(ctx);
                bufferValid = true;
            }
        }
    }
    
    private void GenerateScaledImage(FrameContext ctx)
    {
        if (loadedImage == null || scaledImageBuffer == null) return;
        
        int screenWidth = ctx.Width;
        int screenHeight = ctx.Height;
        
        // Calculate scaling dimensions
        int finalWidth = screenWidth;
        int finalHeight = screenHeight;
        int startX = 0;
        int startY = 0;
        
        if (PreserveAspectRatio)
        {
            if (AspectRatioAxis == AspectRatioAxis.X)
            {
                // Preserve aspect ratio on X-axis
                finalHeight = (imageHeight * screenWidth) / imageWidth;
                startY = (screenHeight / 2) - (finalHeight / 2);
            }
            else
            {
                // Preserve aspect ratio on Y-axis
                finalWidth = (imageWidth * screenHeight) / imageHeight;
                startX = (screenWidth / 2) - (finalWidth / 2);
            }
        }
        
        // Clear buffer
        Array.Clear(scaledImageBuffer, 0, scaledImageBuffer.Length);
        
        // Scale and copy image
        for (int y = 0; y < screenHeight; y++)
        {
            for (int x = 0; x < screenWidth; x++)
            {
                int bufferIndex = y * screenWidth + x;
                
                // Check if pixel is within image bounds
                if (x >= startX && x < startX + finalWidth &&
                    y >= startY && y < startY + finalHeight)
                {
                    // Map screen coordinates to image coordinates
                    int imageX = ((x - startX) * imageWidth) / finalWidth;
                    int imageY = ((y - startY) * imageHeight) / finalHeight;
                    
                    // Clamp coordinates
                    imageX = Math.Clamp(imageX, 0, imageWidth - 1);
                    imageY = Math.Clamp(imageY, 0, imageHeight - 1);
                    
                    // Get pixel from source image
                    Color pixel = loadedImage.GetPixel(imageX, imageY);
                    scaledImageBuffer[bufferIndex] = pixel;
                }
                else
                {
                    // Outside image bounds - transparent
                    scaledImageBuffer[bufferIndex] = Color.Transparent;
                }
            }
        }
    }
    
    private void UpdateBeatReactivity(FrameContext ctx)
    {
        if (EnableAdaptiveBlending)
        {
            if (ctx.IsBeat && !wasBeat)
            {
                // Beat detected - reset persistence counter
                persistenceCount = PersistenceDuration;
                wasBeat = true;
            }
            else if (!ctx.IsBeat)
            {
                wasBeat = false;
            }
            else
            {
                // Beat continues - decrement persistence
                if (persistenceCount > 0)
                {
                    persistenceCount--;
                }
            }
        }
    }
    
    private void RenderImageWithBlending(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (scaledImageBuffer == null) return;
        
        int width = ctx.Width;
        int height = ctx.Height;
        
        // Determine blending mode
        BlendingMode currentBlendMode = DetermineBlendingMode(ctx);
        
        // Apply blending
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int bufferIndex = y * width + x;
                Color imagePixel = scaledImageBuffer[bufferIndex];
                Color backgroundPixel = input.GetPixel(x, y);
                
                Color outputPixel = ApplyBlending(imagePixel, backgroundPixel, currentBlendMode);
                output.SetPixel(x, y, outputPixel);
            }
        }
    }
    
    private BlendingMode DetermineBlendingMode(FrameContext ctx)
    {
        if (EnableAdaptiveBlending)
        {
            if (ctx.IsBeat || persistenceCount > 0)
            {
                return EnableAdditiveBlending ? BlendingMode.Additive : BlendingMode.Replace;
            }
            else
            {
                return EnableAverageBlending ? BlendingMode.Average : BlendingMode.Replace;
            }
        }
        else if (EnableAdditiveBlending)
        {
            return BlendingMode.Additive;
        }
        else if (EnableAverageBlending)
        {
            return BlendingMode.Average;
        }
        else
        {
            return BlendingMode.Replace;
        }
    }
    
    private Color ApplyBlending(Color imageColor, Color backgroundColor, BlendingMode mode)
    {
        switch (mode)
        {
            case BlendingMode.Replace:
                return imageColor;
                
            case BlendingMode.Additive:
                return BlendColorsAdditive(imageColor, backgroundColor);
                
            case BlendingMode.Average:
                return BlendColorsAverage(imageColor, backgroundColor);
                
            default:
                return imageColor;
        }
    }
    
    private Color BlendColorsAdditive(Color color1, Color color2)
    {
        return Color.FromArgb(
            Math.Min(255, color1.A + color2.A),
            Math.Min(255, color1.R + color2.R),
            Math.Min(255, color1.G + color2.G),
            Math.Min(255, color1.B + color2.B)
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
    
    // Public interface for parameter adjustment
    public void SetEnabled(bool enabled) { Enabled = enabled; }
    public void SetAdditiveBlending(bool enable) { EnableAdditiveBlending = enable; }
    public void SetAverageBlending(bool enable) { EnableAverageBlending = enable; }
    public void SetAdaptiveBlending(bool enable) { EnableAdaptiveBlending = enable; }
    public void SetPersistenceDuration(int duration) 
    { 
        PersistenceDuration = Math.Clamp(duration, MinPersistence, MaxPersistence); 
    }
    public void SetAspectRatioPreservation(bool preserve) { PreserveAspectRatio = preserve; }
    public void SetAspectRatioAxis(AspectRatioAxis axis) { AspectRatioAxis = axis; }
    public void SetImagePath(string path) 
    { 
        ImagePath = path; 
        LoadImage(path); 
    }
    
    // Status queries
    public bool IsEnabled() => Enabled;
    public bool IsAdditiveBlendingEnabled() => EnableAdditiveBlending;
    public bool IsAverageBlendingEnabled() => EnableAverageBlending;
    public bool IsAdaptiveBlendingEnabled() => EnableAdaptiveBlending;
    public int GetPersistenceDuration() => PersistenceDuration;
    public bool IsAspectRatioPreserved() => PreserveAspectRatio;
    public AspectRatioAxis GetAspectRatioAxis() => AspectRatioAxis;
    public string GetImagePath() => ImagePath;
    public bool IsImageLoaded() => imageValid;
    public int GetImageWidth() => imageWidth;
    public int GetImageHeight() => imageHeight;
    public int GetCurrentPersistenceCount() => persistenceCount;
    public bool IsBufferValid() => bufferValid;
    
    public override void Dispose()
    {
        UnloadImage();
    }
}

public enum BlendingMode
{
    Replace,    // Direct replacement
    Additive,   // Additive blending
    Average     // 50/50 blending
}

public enum AspectRatioAxis
{
    X = 0,      // Preserve aspect ratio on X-axis
    Y = 1       // Preserve aspect ratio on Y-axis
}
```

## Integration Points

### Audio Data Integration
- **Beat Detection**: Uses `FrameContext.IsBeat` for adaptive blending and persistence
- **Audio Analysis**: Processes audio data for beat-reactive image behavior
- **Dynamic Parameters**: Adjusts blending modes based on audio events

### Framebuffer Handling
- **Input/Output Buffers**: Processes `ImageBuffer` objects with full color support
- **Image Scaling**: Efficient scaling with aspect ratio preservation
- **Blending System**: Multiple blending algorithms for different visual effects
- **Memory Management**: Optimized image buffer handling

### Performance Considerations
- **Image Caching**: Pre-scaled images for repeated rendering
- **Memory Optimization**: Efficient bitmap storage and retrieval
- **Blending Optimization**: Fast pixel blending algorithms
- **Resource Management**: Proper cleanup and memory handling

## Usage Examples

### Basic Image Rendering
```csharp
var pictureNode = new PictureEffectsNode
{
    Enabled = true,
    ImagePath = "background.bmp",
    EnableAverageBlending = true
};
```

### Beat-Reactive Image Overlay
```csharp
var pictureNode = new PictureEffectsNode
{
    Enabled = true,
    ImagePath = "overlay.bmp",
    EnableAdaptiveBlending = true,
    EnableAdditiveBlending = true,
    PersistenceDuration = 12
};
```

### Aspect Ratio Preserved Image
```csharp
var pictureNode = new PictureEffectsNode
{
    Enabled = true,
    ImagePath = "logo.bmp",
    PreserveAspectRatio = true,
    AspectRatioAxis = AspectRatioAxis.X,
    EnableAverageBlending = true
};
```

## Technical Notes

### Image Processing System
The effect implements a sophisticated image processing system:
- **Bitmap Loading**: Native BMP file support with error handling
- **Intelligent Scaling**: High-quality image scaling with aspect ratio preservation
- **Memory Management**: Efficient buffer management and cleanup
- **Format Support**: Extensible for additional image formats

### Performance Architecture
Advanced performance optimization:
- **Image Caching**: Pre-scaled images for repeated rendering
- **Memory Optimization**: Efficient bitmap storage and retrieval
- **Blending Optimization**: Fast pixel blending algorithms
- **Resource Management**: Proper cleanup and memory handling

### Beat Reactivity System
Sophisticated audio integration:
- **Adaptive Blending**: Automatic blend mode switching on beats
- **Persistence Control**: Configurable image persistence duration
- **Countdown System**: Gradual fade-out after beat events
- **Mode Switching**: Dynamic behavior based on audio analysis

This effect is essential for creating image-based visualizations, overlays, and beat-reactive image sequences in AVS presets, providing the foundation for many advanced image manipulation and rendering techniques.
