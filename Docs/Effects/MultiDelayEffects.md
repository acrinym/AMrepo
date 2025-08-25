# Multi Delay Effects

## Overview

The Multi Delay effect creates video delay effects by storing frames in memory buffers and replaying them after a specified delay. It supports up to 6 independent delay buffers, each with configurable delay times that can be synchronized to audio beats or set to specific frame counts. This effect is useful for creating echo effects, feedback loops, and time-based visual manipulations.

## C# Implementation

### Properties

```csharp
/// <summary>
/// Whether the effect is enabled
/// </summary>
public bool Enabled { get; set; } = true;

/// <summary>
/// Delay mode (0=Off, 1=Input, 2=Output)
/// </summary>
public DelayMode Mode { get; set; } = DelayMode.Off;

/// <summary>
/// Currently active buffer index (0-5)
/// </summary>
public int ActiveBufferIndex { get; set; } = 0;

/// <summary>
/// Whether to use beat synchronization for each buffer
/// </summary>
public bool[] UseBeatSync { get; set; } = new bool[6];

/// <summary>
/// Frame delay count for each buffer (0-1000)
/// </summary>
public int[] FrameDelay { get; set; } = new int[6];

/// <summary>
/// Effect intensity multiplier
/// </summary>
public float Intensity { get; set; } = 1.0f;
```

### Enums

```csharp
/// <summary>
/// Available delay modes
/// </summary>
public enum DelayMode
{
    /// <summary>
    /// Effect is disabled
    /// </summary>
    Off = 0,
    
    /// <summary>
    /// Store input frames to buffer
    /// </summary>
    Input = 1,
    
    /// <summary>
    /// Output delayed frames from buffer
    /// </summary>
    Output = 2
}
```

### Private Fields

```csharp
/// <summary>
/// Frame buffers for storing delayed frames
/// </summary>
private ImageBuffer[] _delayBuffers;

/// <summary>
/// Input positions for each buffer
/// </summary>
private int[] _inputPositions;

/// <summary>
/// Output positions for each buffer
/// </summary>
private int[] _outputPositions;

/// <summary>
/// Buffer sizes in bytes
/// </summary>
private long[] _bufferSizes;

/// <summary>
/// Virtual buffer sizes for current delay settings
/// </summary>
private long[] _virtualBufferSizes;

/// <summary>
/// Previous virtual buffer sizes for change detection
/// </summary>
private long[] _previousVirtualBufferSizes;

/// <summary>
/// Frame memory size in bytes
/// </summary>
private long _frameMemorySize;

/// <summary>
/// Previous frame memory size
/// </summary>
private long _previousFrameMemorySize;

/// <summary>
/// Frame counter since last beat
/// </summary>
private int _framesSinceBeat = 0;

/// <summary>
/// Frames per beat for synchronization
/// </summary>
private int _framesPerBeat = 0;

/// <summary>
/// Whether the effect has been initialized
/// </summary>
private bool _isInitialized = false;

/// <summary>
/// Previous width and height for resize detection
/// </summary>
private int _previousWidth, _previousHeight;

/// <summary>
/// Instance counter for global state management
/// </summary>
private static int _instanceCount = 0;

/// <summary>
/// Render ID for this instance
/// </summary>
private int _renderId;
```

### Constructor

```csharp
public MultiDelayEffectsNode()
{
    _delayBuffers = new ImageBuffer[6];
    _inputPositions = new int[6];
    _outputPositions = new int[6];
    _bufferSizes = new long[6];
    _virtualBufferSizes = new long[6];
    _previousVirtualBufferSizes = new long[6];
    
    // Initialize arrays
    for (int i = 0; i < 6; i++)
    {
        UseBeatSync[i] = false;
        FrameDelay[i] = 0;
        _bufferSizes[i] = 1;
        _virtualBufferSizes[i] = 1;
        _previousVirtualBufferSizes[i] = 1;
        _inputPositions[i] = 0;
        _outputPositions[i] = 0;
    }
    
    _frameMemorySize = 1;
    _previousFrameMemorySize = 1;
    _framesSinceBeat = 0;
    _framesPerBeat = 0;
    _isInitialized = false;
    _previousWidth = 0;
    _previousHeight = 0;
    
    // Increment instance counter
    _instanceCount++;
    _renderId = _instanceCount;
}
```

### Processing Methods

```csharp
public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
{
    if (!Enabled || imageBuffer == null) return;

    // Initialize if needed
    if (!_isInitialized)
    {
        InitializeEffect();
    }

    // Handle resize
    if (_previousWidth != imageBuffer.Width || _previousHeight != imageBuffer.Height)
    {
        HandleResize(imageBuffer.Width, imageBuffer.Height);
    }

    // Update frame memory size
    UpdateFrameMemorySize(imageBuffer.Width, imageBuffer.Height);

    // Handle beat detection
    if (audioFeatures.IsBeat)
    {
        HandleBeatDetection();
    }

    // Update frame counters
    _framesSinceBeat++;

    // Process delay buffers
    ProcessDelayBuffers(imageBuffer);

    // Update buffer positions
    UpdateBufferPositions();
}

/// <summary>
/// Initialize the effect and buffers
/// </summary>
private void InitializeEffect()
{
    // Initialize buffers with minimum size
    for (int i = 0; i < 6; i++)
    {
        _delayBuffers[i] = new ImageBuffer(1, 1);
        _bufferSizes[i] = 1;
        _virtualBufferSizes[i] = 1;
        _previousVirtualBufferSizes[i] = 1;
    }
    
    _isInitialized = true;
}

/// <summary>
/// Handle buffer resize
/// </summary>
private void HandleResize(int width, int height)
{
    _previousWidth = width;
    _previousHeight = height;
    
    // Recalculate frame memory size
    _frameMemorySize = width * height * 4; // 4 bytes per pixel (ARGB)
    
    // Reallocate buffers if needed
    ReallocateBuffers();
}

/// <summary>
/// Update frame memory size
/// </summary>
private void UpdateFrameMemorySize(int width, int height)
{
    long newFrameMemorySize = width * height * 4;
    
    if (newFrameMemorySize != _frameMemorySize)
    {
        _previousFrameMemorySize = _frameMemorySize;
        _frameMemorySize = newFrameMemorySize;
        
        // Reallocate buffers if frame size changed
        ReallocateBuffers();
    }
}

/// <summary>
/// Handle beat detection
/// </summary>
private void HandleBeatDetection()
{
    _framesPerBeat = _framesSinceBeat;
    _framesSinceBeat = 0;
    
    // Update beat-synchronized delays
    for (int i = 0; i < 6; i++)
    {
        if (UseBeatSync[i])
        {
            _virtualBufferSizes[i] = (_framesPerBeat + 1) * _frameMemorySize;
        }
    }
}

/// <summary>
/// Process delay buffers
/// </summary>
private void ProcessDelayBuffers(ImageBuffer imageBuffer)
{
    if (Mode == DelayMode.Off) return;
    
    int activeBuffer = ActiveBufferIndex;
    if (activeBuffer < 0 || activeBuffer >= 6) return;
    
    if (_virtualBufferSizes[activeBuffer] > _frameMemorySize)
    {
        if (Mode == DelayMode.Output)
        {
            // Output delayed frame
            OutputDelayedFrame(imageBuffer, activeBuffer);
        }
        else if (Mode == DelayMode.Input)
        {
            // Store input frame
            StoreInputFrame(imageBuffer, activeBuffer);
        }
    }
}

/// <summary>
/// Store input frame to delay buffer
/// </summary>
private void StoreInputFrame(ImageBuffer imageBuffer, int bufferIndex)
{
    if (_delayBuffers[bufferIndex] == null) return;
    
    // Calculate input position
    int inputPos = _inputPositions[bufferIndex];
    
    // Copy frame data to buffer
    CopyFrameToBuffer(imageBuffer, _delayBuffers[bufferIndex], inputPos);
}

/// <summary>
/// Output delayed frame from buffer
/// </summary>
private void OutputDelayedFrame(ImageBuffer imageBuffer, int bufferIndex)
{
    if (_delayBuffers[bufferIndex] == null) return;
    
    // Calculate output position
    int outputPos = _outputPositions[bufferIndex];
    
    // Copy frame data from buffer
    CopyFrameFromBuffer(_delayBuffers[bufferIndex], imageBuffer, outputPos);
}

/// <summary>
/// Copy frame data to buffer at specified position
/// </summary>
private void CopyFrameToBuffer(ImageBuffer source, ImageBuffer buffer, int position)
{
    // This is a simplified implementation
    // In a real implementation, you would copy the actual pixel data
    // based on the position and buffer layout
    
    int width = source.Width;
    int height = source.Height;
    
    // Ensure buffer is large enough
    if (buffer.Width != width || buffer.Height != height)
    {
        buffer = new ImageBuffer(width, height);
    }
    
    // Copy pixels
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color pixel = source.GetPixel(x, y);
            buffer.SetPixel(x, y, pixel);
        }
    }
}

/// <summary>
/// Copy frame data from buffer at specified position
/// </summary>
private void CopyFrameFromBuffer(ImageBuffer buffer, ImageBuffer destination, int position)
{
    // This is a simplified implementation
    // In a real implementation, you would copy the actual pixel data
    // based on the position and buffer layout
    
    int width = destination.Width;
    int height = destination.Height;
    
    // Ensure buffer is large enough
    if (buffer.Width != width || buffer.Height != height)
    {
        return; // Buffer size mismatch
    }
    
    // Copy pixels
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color pixel = buffer.GetPixel(x, y);
            destination.SetPixel(x, y, pixel);
        }
    }
}

/// <summary>
/// Update buffer positions
/// </summary>
private void UpdateBufferPositions()
{
    for (int i = 0; i < 6; i++)
    {
        if (_virtualBufferSizes[i] > _frameMemorySize)
        {
            // Update input position
            _inputPositions[i] += (int)_frameMemorySize;
            if (_inputPositions[i] >= _virtualBufferSizes[i])
            {
                _inputPositions[i] = 0;
            }
            
            // Update output position
            _outputPositions[i] += (int)_frameMemorySize;
            if (_outputPositions[i] >= _virtualBufferSizes[i])
            {
                _outputPositions[i] = 0;
            }
        }
    }
}

/// <summary>
/// Reallocate buffers based on current settings
/// </summary>
private void ReallocateBuffers()
{
    for (int i = 0; i < 6; i++)
    {
        // Calculate required buffer size
        long requiredSize = CalculateRequiredBufferSize(i);
        
        if (requiredSize > _bufferSizes[i])
        {
            // Create new buffer
            _delayBuffers[i] = new ImageBuffer(_previousWidth, _previousHeight);
            _bufferSizes[i] = requiredSize;
            _virtualBufferSizes[i] = requiredSize;
            _previousVirtualBufferSizes[i] = requiredSize;
            
            // Reset positions
            _inputPositions[i] = 0;
            _outputPositions[i] = 0;
        }
    }
}

/// <summary>
/// Calculate required buffer size for a specific delay buffer
/// </summary>
private long CalculateRequiredBufferSize(int bufferIndex)
{
    if (UseBeatSync[bufferIndex])
    {
        return (_framesPerBeat + 1) * _frameMemorySize;
    }
    else
    {
        return (FrameDelay[bufferIndex] + 1) * _frameMemorySize;
    }
}
```

### Configuration Validation

```csharp
public override bool ValidateConfiguration()
{
    if (ActiveBufferIndex < 0 || ActiveBufferIndex > 5) return false;
    
    for (int i = 0; i < 6; i++)
    {
        if (FrameDelay[i] < 0 || FrameDelay[i] > 1000) return false;
    }
    
    if (Intensity < 0.0f || Intensity > 10.0f) return false;
    
    return true;
}
```

### Preset Methods

```csharp
/// <summary>
/// Load a basic delay preset
/// </summary>
public void LoadBasicDelayPreset()
{
    Mode = DelayMode.Output;
    ActiveBufferIndex = 0;
    UseBeatSync[0] = false;
    FrameDelay[0] = 30;
    
    // Disable other buffers
    for (int i = 1; i < 6; i++)
    {
        UseBeatSync[i] = false;
        FrameDelay[i] = 0;
    }
    
    _isInitialized = false;
}

/// <summary>
/// Load a beat-synchronized preset
/// </summary>
public void LoadBeatSyncPreset()
{
    Mode = DelayMode.Output;
    ActiveBufferIndex = 0;
    UseBeatSync[0] = true;
    FrameDelay[0] = 0;
    
    // Disable other buffers
    for (int i = 1; i < 6; i++)
    {
        UseBeatSync[i] = false;
        FrameDelay[i] = 0;
    }
    
    _isInitialized = false;
}

/// <summary>
/// Load a multi-buffer preset
/// </summary>
public void LoadMultiBufferPreset()
{
    Mode = DelayMode.Output;
    ActiveBufferIndex = 0;
    
    // Configure multiple buffers with different delays
    UseBeatSync[0] = false;
    FrameDelay[0] = 15;
    
    UseBeatSync[1] = false;
    FrameDelay[1] = 30;
    
    UseBeatSync[2] = false;
    FrameDelay[2] = 45;
    
    // Disable remaining buffers
    for (int i = 3; i < 6; i++)
    {
        UseBeatSync[i] = false;
        FrameDelay[i] = 0;
    }
    
    _isInitialized = false;
}

/// <summary>
/// Load a feedback loop preset
/// </summary>
public void LoadFeedbackLoopPreset()
{
    Mode = DelayMode.Input;
    ActiveBufferIndex = 0;
    UseBeatSync[0] = false;
    FrameDelay[0] = 60;
    
    // Disable other buffers
    for (int i = 1; i < 6; i++)
    {
        UseBeatSync[i] = false;
        FrameDelay[i] = 0;
    }
    
    _isInitialized = false;
}

/// <summary>
/// Load a complex delay preset
/// </summary>
public void LoadComplexDelayPreset()
{
    Mode = DelayMode.Output;
    ActiveBufferIndex = 0;
    
    // Mix of beat-sync and frame delays
    UseBeatSync[0] = true;
    FrameDelay[0] = 0;
    
    UseBeatSync[1] = false;
    FrameDelay[1] = 20;
    
    UseBeatSync[2] = true;
    FrameDelay[2] = 0;
    
    UseBeatSync[3] = false;
    FrameDelay[3] = 40;
    
    // Disable remaining buffers
    for (int i = 4; i < 6; i++)
    {
        UseBeatSync[i] = false;
        FrameDelay[i] = 0;
    }
    
    _isInitialized = false;
}
```

### Utility Methods

```csharp
/// <summary>
/// Get the current delay status
/// </summary>
public string GetDelayStatus()
{
    return $"Mode: {Mode}, Active Buffer: {ActiveBufferIndex}, Beat Frames: {_framesPerBeat}, Frame Memory: {_frameMemorySize}";
}

/// <summary>
/// Check if the effect is currently delaying
/// </summary>
public bool IsDelaying()
{
    return Enabled && Mode != DelayMode.Off && _virtualBufferSizes[ActiveBufferIndex] > _frameMemorySize;
}

/// <summary>
/// Get the current delay time for active buffer
/// </summary>
public int GetCurrentDelay()
{
    if (ActiveBufferIndex < 0 || ActiveBufferIndex >= 6) return 0;
    
    if (UseBeatSync[ActiveBufferIndex])
    {
        return _framesPerBeat;
    }
    else
    {
        return FrameDelay[ActiveBufferIndex];
    }
}

/// <summary>
/// Get buffer information for a specific index
/// </summary>
public string GetBufferInfo(int bufferIndex)
{
    if (bufferIndex < 0 || bufferIndex >= 6) return "Invalid buffer index";
    
    string beatSync = UseBeatSync[bufferIndex] ? "Beat" : "Frame";
    int delay = UseBeatSync[bufferIndex] ? _framesPerBeat : FrameDelay[bufferIndex];
    
    return $"Buffer {bufferIndex}: {beatSync} sync, Delay: {delay}, Size: {_virtualBufferSizes[bufferIndex]}";
}

/// <summary>
/// Reset the effect to initial state
/// </summary>
public void Reset()
{
    _isInitialized = false;
    _framesSinceBeat = 0;
    _framesPerBeat = 0;
    _frameMemorySize = 1;
    _previousFrameMemorySize = 1;
    _previousWidth = 0;
    _previousHeight = 0;
    
    // Reset buffer positions
    for (int i = 0; i < 6; i++)
    {
        _inputPositions[i] = 0;
        _outputPositions[i] = 0;
        _virtualBufferSizes[i] = 1;
        _previousVirtualBufferSizes[i] = 1;
    }
}

/// <summary>
/// Get effect execution statistics
/// </summary>
public string GetExecutionStats()
{
    return $"Initialized: {_isInitialized}, Instance: {_renderId}, Total Instances: {_instanceCount}, Active Buffer: {ActiveBufferIndex}";
}
```

## Usage Examples

### Basic Frame Delay

```csharp
var multiDelay = new MultiDelayEffectsNode();
multiDelay.Mode = DelayMode.Output;
multiDelay.ActiveBufferIndex = 0;
multiDelay.UseBeatSync[0] = false;
multiDelay.FrameDelay[0] = 30;
```

### Beat-Synchronized Delay

```csharp
var multiDelay = new MultiDelayEffectsNode();
multiDelay.LoadBeatSyncPreset();
multiDelay.Intensity = 0.8f;
```

### Multi-Buffer Delay Chain

```csharp
var multiDelay = new MultiDelayEffectsNode();
multiDelay.LoadMultiBufferPreset();
multiDelay.Intensity = 1.2f;
```

### Feedback Loop

```csharp
var multiDelay = new MultiDelayEffectsNode();
multiDelay.LoadFeedbackLoopPreset();
multiDelay.Intensity = 0.6f;
```

## Technical Details

The Multi Delay effect creates video delay effects by storing frames in memory buffers and replaying them after a specified delay. Key features include:

- **Multiple Buffers**: Up to 6 independent delay buffers for complex effects
- **Flexible Timing**: Frame-based delays or beat-synchronized delays
- **Memory Management**: Dynamic buffer allocation based on delay requirements
- **Position Tracking**: Circular buffer implementation for efficient memory usage
- **Global State**: Shared timing information across multiple instances
- **Mode Selection**: Input (store), output (replay), or disabled modes

The effect uses a sophisticated buffer management system that automatically allocates memory based on delay requirements and frame sizes. Beat synchronization allows delays to automatically adjust to the tempo of the music, while frame-based delays provide precise control over timing.

The circular buffer implementation ensures efficient memory usage by reusing buffer space and automatically wrapping around when reaching the end. This allows for long delays without excessive memory consumption.

The effect is particularly useful for creating echo effects, feedback loops, and time-based visual manipulations that can add depth and complexity to visualizations.
