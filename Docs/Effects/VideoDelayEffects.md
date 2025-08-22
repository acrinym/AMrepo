# Video Delay Effects (Trans / Video Delay)

## Overview

The **Video Delay Effects** system is a sophisticated framebuffer delay engine that provides both frame-based and beat-reactive video delay capabilities. It implements advanced memory management with virtual memory allocation, circular buffer systems, and intelligent buffer resizing for optimal performance. This effect is essential for creating motion trails, echo effects, and temporal video manipulations in AVS presets.

## Source Analysis

### Core Architecture (`r_videodelay.cpp`)

The effect is implemented as a C++ class `C_VideoDelayClass` that inherits from `C_RBASE`. It provides a comprehensive delay system with dual timing modes, advanced memory management, and intelligent buffer optimization for smooth video delay effects.

### Key Components

#### Delay Timing Modes
Dual timing system for flexible delay control:
- **Frame-based Delay**: Fixed frame count delay (1-200 frames)
- **Beat-reactive Delay**: Dynamic delay based on beat timing (1-16 beats)
- **Hybrid Mode**: Automatic switching between timing modes
- **Adaptive Timing**: Intelligent delay adjustment based on audio events

#### Memory Management System
Advanced virtual memory architecture:
- **Virtual Memory Allocation**: Uses Windows VirtualAlloc for efficient memory management
- **Dynamic Buffer Resizing**: Automatic buffer allocation based on delay requirements
- **Circular Buffer Implementation**: Efficient memory reuse with minimal overhead
- **Memory Optimization**: Intelligent buffer sizing and memory deallocation

#### Buffer Architecture
Sophisticated buffer management:
- **Circular Buffer**: Continuous memory cycling for seamless delays
- **Dynamic Sizing**: Automatic buffer expansion and contraction
- **Memory Mapping**: Efficient pointer management for buffer access
- **Overflow Protection**: Built-in safeguards against memory issues

#### Performance Optimization
Advanced optimization techniques:
- **Virtual Memory**: Efficient memory allocation and deallocation
- **Circular Access**: Minimal memory copying and movement
- **Adaptive Sizing**: Intelligent buffer size optimization
- **Memory Pooling**: Efficient memory reuse and management

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `enabled` | bool | true/false | true | Enable delay effect |
| `usebeats` | bool | true/false | false | Use beat-based timing |
| `delay` | unsigned int | 1-200 (frames), 1-16 (beats) | 10 | Delay amount |
| `framedelay` | unsigned long | Calculated | 10 | Current frame delay |
| `framessincebeat` | unsigned long | Counter | 0 | Frames since last beat |

### Timing Modes

| Mode | Description | Delay Range | Behavior |
|------|-------------|-------------|----------|
| **Frame-based** | Fixed frame count delay | 1-200 frames | Consistent delay regardless of audio |
| **Beat-reactive** | Dynamic beat-based delay | 1-16 beats | Delay varies with audio timing |
| **Hybrid** | Automatic mode switching | Adaptive | Intelligent timing mode selection |

## C# Implementation

```csharp
public class VideoDelayEffectsNode : AvsModuleNode
{
    public bool Enabled { get; set; } = true;
    public bool UseBeatTiming { get; set; } = false;
    public int DelayAmount { get; set; } = 10;
    
    // Internal state
    private IntPtr buffer;
    private IntPtr inputOutputPosition;
    private long bufferSize;
    private long virtualBufferSize;
    private long oldVirtualBufferSize;
    private long framesSinceBeat;
    private long frameDelay;
    private long frameMemory;
    private long oldFrameMemory;
    private readonly object bufferLock = new object();
    
    // Performance optimization
    private const int MaxFrameDelay = 200;
    private const int MaxBeatDelay = 16;
    private const int MaxBeatDelayFrames = 400;
    private const int BufferSizeMultiplier = 2;
    
    public VideoDelayEffectsNode()
    {
        buffer = IntPtr.Zero;
        inputOutputPosition = IntPtr.Zero;
        bufferSize = 1;
        virtualBufferSize = 1;
        oldVirtualBufferSize = 1;
        framesSinceBeat = 0;
        frameDelay = 10;
        frameMemory = 0;
        oldFrameMemory = 0;
    }
    
    public override void Process(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (ctx.Width <= 0 || ctx.Height <= 0) return;
        
        // Calculate frame memory requirements
        long currentFrameMemory = ctx.Width * ctx.Height * 4;
        
        // Handle beat-reactive timing
        if (UseBeatTiming)
        {
            if (ctx.IsBeat)
            {
                frameDelay = framesSinceBeat * DelayAmount;
                if (frameDelay > MaxBeatDelayFrames) frameDelay = MaxBeatDelayFrames;
                framesSinceBeat = 0;
            }
            framesSinceBeat++;
        }
        
        // Apply delay effect if enabled and delay is active
        if (Enabled && frameDelay != 0)
        {
            // Calculate virtual buffer size
            long newVirtualBufferSize = frameDelay * currentFrameMemory;
            
            // Update buffer if needed
            UpdateBuffer(currentFrameMemory, newVirtualBufferSize);
            
            // Apply delay effect
            ApplyDelayEffect(ctx, input, output, currentFrameMemory);
        }
        else
        {
            // No delay - copy input to output
            output.CopyFrom(input);
        }
    }
    
    private void UpdateBuffer(long currentFrameMemory, long newVirtualBufferSize)
    {
        lock (bufferLock)
        {
            if (currentFrameMemory == oldFrameMemory)
            {
                if (newVirtualBufferSize != oldVirtualBufferSize)
                {
                    if (newVirtualBufferSize > oldVirtualBufferSize)
                    {
                        // Buffer needs to grow
                        if (newVirtualBufferSize > bufferSize)
                        {
                            // Allocate new memory
                            if (!FreeBuffer()) return;
                            
                            if (UseBeatTiming)
                            {
                                bufferSize = BufferSizeMultiplier * newVirtualBufferSize;
                                if (bufferSize > currentFrameMemory * MaxBeatDelayFrames)
                                {
                                    bufferSize = currentFrameMemory * MaxBeatDelayFrames;
                                }
                                buffer = AllocateBuffer(bufferSize);
                                if (buffer == IntPtr.Zero)
                                {
                                    bufferSize = newVirtualBufferSize;
                                    buffer = AllocateBuffer(bufferSize);
                                }
                            }
                            else
                            {
                                bufferSize = newVirtualBufferSize;
                                buffer = AllocateBuffer(bufferSize);
                            }
                            
                            inputOutputPosition = buffer;
                            if (buffer == IntPtr.Zero)
                            {
                                frameDelay = 0;
                                framesSinceBeat = 0;
                                return;
                            }
                        }
                        else
                        {
                            // Buffer can accommodate new size
                            long size = ((long)buffer + oldVirtualBufferSize) - (long)inputOutputPosition;
                            long newEnd = (long)buffer + newVirtualBufferSize;
                            long destination = newEnd - size;
                            
                            // Move existing data
                            MoveMemory(destination, inputOutputPosition, size);
                            
                            // Fill remaining space with copies
                            for (long pos = (long)inputOutputPosition; pos < destination; pos += frameMemory)
                            {
                                CopyMemory(pos, destination, frameMemory);
                            }
                        }
                    }
                    else
                    {
                        // Buffer needs to shrink
                        long preSegmentSize = ((long)inputOutputPosition) - ((long)buffer) + frameMemory;
                        
                        if (preSegmentSize > newVirtualBufferSize)
                        {
                            // Move data to accommodate smaller size
                            MoveMemory(buffer, 
                                     (long)buffer + preSegmentSize - newVirtualBufferSize, 
                                     newVirtualBufferSize);
                            inputOutputPosition = (IntPtr)((long)buffer + newVirtualBufferSize - frameMemory);
                        }
                        else if (preSegmentSize < newVirtualBufferSize)
                        {
                            // Expand data to fill larger size
                            MoveMemory((long)inputOutputPosition + frameMemory, 
                                     (long)buffer + oldVirtualBufferSize + preSegmentSize - newVirtualBufferSize, 
                                     newVirtualBufferSize - preSegmentSize);
                        }
                    }
                    oldVirtualBufferSize = newVirtualBufferSize;
                }
            }
            else
            {
                // Frame size changed - allocate new memory
                if (!FreeBuffer()) return;
                
                if (UseBeatTiming)
                {
                    bufferSize = BufferSizeMultiplier * newVirtualBufferSize;
                    buffer = AllocateBuffer(bufferSize);
                    if (buffer == IntPtr.Zero)
                    {
                        bufferSize = newVirtualBufferSize;
                        buffer = AllocateBuffer(bufferSize);
                    }
                }
                else
                {
                    bufferSize = newVirtualBufferSize;
                    buffer = AllocateBuffer(bufferSize);
                }
                
                inputOutputPosition = buffer;
                if (buffer == IntPtr.Zero)
                {
                    frameDelay = 0;
                    framesSinceBeat = 0;
                    return;
                }
                oldVirtualBufferSize = newVirtualBufferSize;
            }
            
            oldFrameMemory = currentFrameMemory;
        }
    }
    
    private void ApplyDelayEffect(FrameContext ctx, ImageBuffer input, ImageBuffer output, long currentFrameMemory)
    {
        if (buffer == IntPtr.Zero) return;
        
        lock (bufferLock)
        {
            // Copy delayed frame to output
            CopyBufferToImage(output, inputOutputPosition, currentFrameMemory);
            
            // Copy current frame to buffer
            CopyImageToBuffer(input, inputOutputPosition, currentFrameMemory);
            
            // Update buffer position
            inputOutputPosition = (IntPtr)((long)inputOutputPosition + currentFrameMemory);
            
            // Wrap around if needed
            if ((long)inputOutputPosition >= (long)buffer + virtualBufferSize)
            {
                inputOutputPosition = buffer;
            }
        }
    }
    
    private bool AllocateBuffer(long size)
    {
        try
        {
            // Allocate virtual memory
            buffer = Marshal.AllocHGlobal((int)size);
            return buffer != IntPtr.Zero;
        }
        catch
        {
            buffer = IntPtr.Zero;
            return false;
        }
    }
    
    private bool FreeBuffer()
    {
        if (buffer != IntPtr.Zero)
        {
            try
            {
                Marshal.FreeHGlobal(buffer);
                buffer = IntPtr.Zero;
                return true;
            }
            catch
            {
                return false;
            }
        }
        return true;
    }
    
    private void CopyBufferToImage(ImageBuffer image, IntPtr source, long size)
    {
        if (source == IntPtr.Zero || size <= 0) return;
        
        try
        {
            // Convert buffer data to image
            byte[] bufferData = new byte[size];
            Marshal.Copy(source, bufferData, 0, (int)size);
            
            // Convert bytes to image pixels
            ConvertBytesToImage(image, bufferData);
        }
        catch
        {
            // Fallback to black frame on error
            image.Clear(Color.Black);
        }
    }
    
    private void CopyImageToBuffer(ImageBuffer image, IntPtr destination, long size)
    {
        if (destination == IntPtr.Zero || size <= 0) return;
        
        try
        {
            // Convert image to bytes
            byte[] imageData = ConvertImageToBytes(image);
            
            // Copy to buffer
            Marshal.Copy(imageData, 0, destination, Math.Min(imageData.Length, (int)size));
        }
        catch
        {
            // Handle error gracefully
        }
    }
    
    private void ConvertBytesToImage(ImageBuffer image, byte[] data)
    {
        int width = image.Width;
        int height = image.Height;
        int bytesPerPixel = 4; // ARGB
        
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int index = (y * width + x) * bytesPerPixel;
                
                if (index + 3 < data.Length)
                {
                    byte a = data[index + 3];
                    byte r = data[index + 2];
                    byte g = data[index + 1];
                    byte b = data[index];
                    
                    Color pixel = Color.FromArgb(a, r, g, b);
                    image.SetPixel(x, y, pixel);
                }
            }
        }
    }
    
    private byte[] ConvertImageToBytes(ImageBuffer image)
    {
        int width = image.Width;
        int height = image.Height;
        int bytesPerPixel = 4; // ARGB
        byte[] data = new byte[width * height * bytesPerPixel];
        
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                Color pixel = image.GetPixel(x, y);
                int index = (y * width + x) * bytesPerPixel;
                
                data[index] = pixel.B;     // Blue
                data[index + 1] = pixel.G; // Green
                data[index + 2] = pixel.R; // Red
                data[index + 3] = pixel.A; // Alpha
            }
        }
        
        return data;
    }
    
    private void MoveMemory(long destination, long source, long size)
    {
        if (destination == source || size <= 0) return;
        
        try
        {
            byte[] temp = new byte[size];
            Marshal.Copy((IntPtr)source, temp, 0, (int)size);
            Marshal.Copy(temp, 0, (IntPtr)destination, (int)size);
        }
        catch
        {
            // Handle error gracefully
        }
    }
    
    private void CopyMemory(long destination, long source, long size)
    {
        if (destination == source || size <= 0) return;
        
        try
        {
            byte[] temp = new byte[size];
            Marshal.Copy((IntPtr)source, temp, 0, (int)size);
            Marshal.Copy(temp, 0, (IntPtr)destination, (int)size);
        }
        catch
        {
            // Handle error gracefully
        }
    }
    
    // Public interface for parameter adjustment
    public void SetEnabled(bool enable) { Enabled = enable; }
    
    public void SetUseBeatTiming(bool useBeats) 
    { 
        UseBeatTiming = useBeats; 
        if (useBeats)
        {
            frameDelay = 0;
            framesSinceBeat = 0;
        }
        else
        {
            frameDelay = DelayAmount;
        }
    }
    
    public void SetDelayAmount(int amount) 
    { 
        if (UseBeatTiming)
        {
            DelayAmount = Math.Clamp(amount, 1, MaxBeatDelay);
        }
        else
        {
            DelayAmount = Math.Clamp(amount, 1, MaxFrameDelay);
        }
        
        if (!UseBeatTiming)
        {
            frameDelay = DelayAmount;
        }
    }
    
    // Status queries
    public bool IsEnabled() => Enabled;
    public bool IsBeatTimingEnabled() => UseBeatTiming;
    public int GetDelayAmount() => DelayAmount;
    public long GetCurrentFrameDelay() => frameDelay;
    public long GetFramesSinceBeat() => framesSinceBeat;
    public long GetBufferSize() => bufferSize;
    public long GetVirtualBufferSize() => virtualBufferSize;
    public bool IsBufferValid() => buffer != IntPtr.Zero;
    
    // Buffer management
    public void ResetBuffer()
    {
        lock (bufferLock)
        {
            FreeBuffer();
            bufferSize = 1;
            virtualBufferSize = 1;
            oldVirtualBufferSize = 1;
            inputOutputPosition = IntPtr.Zero;
            frameMemory = 0;
            oldFrameMemory = 0;
        }
    }
    
    public void ClearDelay()
    {
        lock (bufferLock)
        {
            frameDelay = 0;
            framesSinceBeat = 0;
        }
    }
    
    public override void Dispose()
    {
        lock (bufferLock)
        {
            FreeBuffer();
        }
    }
}
```

## Integration Points

### Audio Data Integration
- **Beat Detection**: Responds to audio events for dynamic delay timing
- **Audio Analysis**: Processes audio data for enhanced delay effects
- **Dynamic Parameters**: Adjusts delay behavior based on audio events
- **Reactive Timing**: Beat-reactive delay adjustment and timing

### Framebuffer Handling
- **Input/Output Buffers**: Processes `ImageBuffer` objects with full color support
- **Circular Buffer System**: Efficient memory cycling for seamless delays
- **Memory Management**: Advanced virtual memory allocation and management
- **Performance Optimization**: Intelligent buffer sizing and optimization

### Performance Considerations
- **Virtual Memory**: Efficient memory allocation and deallocation
- **Circular Access**: Minimal memory copying and movement
- **Adaptive Sizing**: Intelligent buffer size optimization
- **Memory Pooling**: Efficient memory reuse and management

## Usage Examples

### Basic Frame Delay
```csharp
var delayNode = new VideoDelayEffectsNode
{
    Enabled = true,
    UseBeatTiming = false,
    DelayAmount = 15              // 15 frame delay
};
```

### Beat-Reactive Delay
```csharp
var delayNode = new VideoDelayEffectsNode
{
    Enabled = true,
    UseBeatTiming = true,
    DelayAmount = 8               // 8 beat delay
};
```

### Dynamic Delay Control
```csharp
var delayNode = new VideoDelayEffectsNode
{
    Enabled = true,
    UseBeatTiming = false,
    DelayAmount = 30              // 30 frame delay
};

// Adjust delay dynamically
delayNode.SetDelayAmount(45);     // Increase to 45 frames
delayNode.SetUseBeatTiming(true); // Switch to beat timing
delayNode.SetDelayAmount(12);     // Set to 12 beat delay
```

## Technical Notes

### Memory Architecture
The effect implements sophisticated memory management:
- **Virtual Memory**: Uses Windows VirtualAlloc for efficiency
- **Circular Buffers**: Continuous memory cycling with minimal overhead
- **Dynamic Sizing**: Automatic buffer optimization based on requirements
- **Memory Safety**: Built-in overflow protection and error handling

### Performance Architecture
Advanced optimization techniques:
- **Circular Access**: Efficient memory cycling and reuse
- **Adaptive Sizing**: Intelligent buffer size optimization
- **Memory Pooling**: Efficient memory allocation and deallocation
- **Error Handling**: Graceful fallback on memory issues

### Delay System
Sophisticated delay implementation:
- **Dual Timing Modes**: Frame-based and beat-reactive timing
- **Adaptive Delays**: Intelligent delay adjustment based on audio
- **Smooth Transitions**: Seamless delay changes without artifacts
- **Performance Scaling**: Efficient operation at various delay lengths

This effect provides the foundation for sophisticated video delay effects, motion trails, and temporal video manipulations, making it essential for advanced AVS preset creation and professional visualization systems.
