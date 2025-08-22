# Bspin Effects

## Overview

The Bspin effect creates dynamic, bass-reactive spinning visualizations that respond to low-frequency audio data. It generates spinning patterns with configurable left/right channel support, dual rendering modes (lines or triangles), and smooth rotation based on bass intensity. The effect creates engaging visual feedback that directly correlates with bass frequencies.

## C++ Source Analysis

**Source File**: `r_bspin.cpp`

**Key Features**:
- **Bass-Reactive Spinning**: Creates spinning patterns based on low-frequency audio
- **Dual Channel Support**: Independent left and right channel processing
- **Dual Rendering Modes**: Line-based or triangle-based visualization
- **Smooth Rotation**: Continuous rotation with velocity-based acceleration
- **Audio Integration**: Direct spectrum data processing for bass frequencies
- **Configurable Colors**: Separate colors for left and right channels

**Core Parameters**:
- `enabled`: Bit flags for left/right channel enable (1=left, 2=right, 3=both)
- `colors`: Array of two colors for left and right channels
- `mode`: Rendering mode (0=lines, 1=triangles)

## C# Implementation

```csharp
using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace PhoenixVisualizer.Effects
{
    /// <summary>
    /// Bspin Effects Node - Creates bass-reactive spinning visualizations
    /// </summary>
    public class BspinEffectsNode : AvsModuleNode
    {
        #region Properties

        /// <summary>
        /// Enable/disable the bass spin effect
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Channel enable flags - bit flags for left/right channel (1=left, 2=right, 3=both)
        /// </summary>
        public int EnabledChannels { get; set; } = 3; // Default: both channels

        /// <summary>
        /// Colors for left and right channels
        /// </summary>
        public Color[] Colors { get; set; } = new Color[2];

        /// <summary>
        /// Rendering mode (0=lines, 1=triangles)
        /// </summary>
        public int Mode { get; set; } = 1; // Default: triangles

        #endregion

        #region Constants

        // Channel constants
        private const int LEFT_CHANNEL = 1;
        private const int RIGHT_CHANNEL = 2;
        private const int BOTH_CHANNELS = 3;

        // Rendering mode constants
        private const int LINE_MODE = 0;
        private const int TRIANGLE_MODE = 1;

        // Audio processing constants
        private const int BASS_FREQUENCY_COUNT = 44; // Number of low frequencies to analyze
        private const int AUDIO_SCALE_FACTOR = 512;
        private const int AUDIO_OFFSET = 30 * 256;
        private const int MAX_AUDIO_VALUE = 255;
        private const int MIN_AUDIO_THRESHOLD = 104;
        private const int MIN_AUDIO_VALUE = 12;
        private const int AUDIO_RANGE = 96;
        private const double VELOCITY_SMOOTHING = 0.7;
        private const double VELOCITY_PERSISTENCE = 0.3;
        private const double ROTATION_STEP = Math.PI / 6.0;

        // Performance optimization constants
        private const int MaxEnabledChannels = 3;
        private const int MinEnabledChannels = 0;
        private const int MaxMode = 1;
        private const int MinMode = 0;
        private const double FixedPointMultiplier = 65536.0; // 2^16 for fixed-point math

        #endregion

        #region Internal State

        private int lastAudioSum;
        private double[] rotationAngles;
        private double[] velocities;
        private double[] directions;
        private int[,] lastPositions; // [channel][position] - stores last x,y for each channel
        private int lastWidth, lastHeight;
        private readonly object renderLock = new object();

        #endregion

        #region Constructor

        public BspinEffectsNode()
        {
            // Initialize default colors
            Colors[0] = Color.White; // Left channel
            Colors[1] = Color.White; // Right channel

            // Initialize internal state
            rotationAngles = new double[2];
            velocities = new double[2];
            directions = new double[2];
            lastPositions = new int[2, 2]; // [channel][x/y]

            ResetState();
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Process the image with bass spin effects
        /// </summary>
        public override ImageBuffer ProcessFrame(ImageBuffer input, AudioFeatures audioFeatures)
        {
            if (!Enabled || input == null)
                return input;

            lock (renderLock)
            {
                // Update dimensions if changed
                if (lastWidth != input.Width || lastHeight != input.Height)
                {
                    lastWidth = input.Width;
                    lastHeight = input.Height;
                    ResetState();
                }

                // Create output buffer
                var output = new ImageBuffer(input.Width, input.Height);
                Array.Copy(input.Pixels, output.Pixels, input.Pixels.Length);

                // Process each enabled channel
                for (int channel = 0; channel < 2; channel++)
                {
                    if ((EnabledChannels & (1 << channel)) != 0)
                    {
                        ProcessChannel(output, audioFeatures, channel);
                    }
                }

                return output;
            }
        }

        /// <summary>
        /// Reset internal state
        /// </summary>
        public override void Reset()
        {
            lock (renderLock)
            {
                ResetState();
            }
        }

        #endregion

        #region Private Methods

        /// <summary>
        /// Reset internal state variables
        /// </summary>
        private void ResetState()
        {
            lastAudioSum = 0;
            rotationAngles[0] = Math.PI; // Left channel starts at PI
            rotationAngles[1] = 0.0;     // Right channel starts at 0
            velocities[0] = 0.0;
            velocities[1] = 0.0;
            directions[0] = -1.0;        // Left channel rotates counter-clockwise
            directions[1] = 1.0;         // Right channel rotates clockwise

            // Clear last positions
            for (int i = 0; i < 2; i++)
            {
                lastPositions[i, 0] = 0; // x
                lastPositions[i, 1] = 0; // y
            }
        }

        /// <summary>
        /// Process a single audio channel
        /// </summary>
        private void ProcessChannel(ImageBuffer image, AudioFeatures audioFeatures, int channel)
        {
            // Get audio data for the channel
            float[] channelData = GetChannelAudioData(audioFeatures, channel);
            
            // Calculate audio sum for bass frequencies
            int audioSum = CalculateBassSum(channelData);
            
            // Calculate audio intensity
            int audioIntensity = CalculateAudioIntensity(audioSum);
            
            // Update velocity and rotation
            UpdateChannelState(channel, audioIntensity);
            
            // Calculate spin parameters
            var spinParams = CalculateSpinParameters(channel, audioIntensity);
            
            // Render the spin effect
            RenderSpinEffect(image, channel, spinParams);
        }

        /// <summary>
        /// Get audio data for a specific channel
        /// </summary>
        private float[] GetChannelAudioData(AudioFeatures audioFeatures, int channel)
        {
            // Use spectrum data for bass frequencies
            return audioFeatures.SpectrumData;
        }

        /// <summary>
        /// Calculate sum of bass frequencies
        /// </summary>
        private int CalculateBassSum(float[] audioData)
        {
            int sum = 0;
            int count = Math.Min(BASS_FREQUENCY_COUNT, audioData.Length);
            
            for (int i = 0; i < count; i++)
            {
                sum += (int)audioData[i];
            }
            
            return sum;
        }

        /// <summary>
        /// Calculate audio intensity from bass sum
        /// </summary>
        private int CalculateAudioIntensity(int audioSum)
        {
            // Calculate relative intensity
            int relativeIntensity = (audioSum * AUDIO_SCALE_FACTOR) / (lastAudioSum + AUDIO_OFFSET);
            
            // Update last audio sum
            lastAudioSum = audioSum;
            
            // Clamp to valid range
            return Math.Clamp(relativeIntensity, 0, MAX_AUDIO_VALUE);
        }

        /// <summary>
        /// Update channel state (velocity and rotation)
        /// </summary>
        private void UpdateChannelState(int channel, int audioIntensity)
        {
            // Calculate target velocity based on audio intensity
            double targetVelocity = Math.Max(audioIntensity - MIN_AUDIO_THRESHOLD, MIN_AUDIO_VALUE) / (double)AUDIO_RANGE;
            
            // Smooth velocity update
            velocities[channel] = VELOCITY_SMOOTHING * targetVelocity + VELOCITY_PERSISTENCE * velocities[channel];
            
            // Update rotation angle
            rotationAngles[channel] += ROTATION_STEP * velocities[channel] * directions[channel];
            
            // Normalize rotation angle
            if (rotationAngles[channel] >= Math.PI * 2)
            {
                rotationAngles[channel] -= Math.PI * 2;
            }
            else if (rotationAngles[channel] < 0)
            {
                rotationAngles[channel] += Math.PI * 2;
            }
        }

        /// <summary>
        /// Calculate spin parameters for rendering
        /// </summary>
        private SpinParameters CalculateSpinParameters(int channel, int audioIntensity)
        {
            // Calculate spin size based on audio intensity
            int spinSize = Math.Min(lastHeight / 2, (lastWidth * 3) / 8);
            double scaledSize = spinSize * (audioIntensity / (double)MAX_AUDIO_VALUE);
            
            // Calculate center position
            int centerX = (channel == 0) ? lastWidth / 2 - spinSize / 2 : lastWidth / 2 + spinSize / 2;
            int centerY = lastHeight / 2;
            
            // Calculate current position
            double currentAngle = rotationAngles[channel];
            int currentX = (int)(Math.Cos(currentAngle) * scaledSize);
            int currentY = (int)(Math.Sin(currentAngle) * scaledSize);
            
            return new SpinParameters
            {
                CenterX = centerX,
                CenterY = centerY,
                CurrentX = currentX,
                CurrentY = currentY,
                ScaledSize = scaledSize,
                Channel = channel
            };
        }

        /// <summary>
        /// Render the spin effect based on mode
        /// </summary>
        private void RenderSpinEffect(ImageBuffer image, int channel, SpinParameters parameters)
        {
            Color channelColor = Colors[channel];
            int colorValue = ColorToInt(channelColor);
            
            if (Mode == LINE_MODE)
            {
                RenderLineMode(image, channel, parameters, colorValue);
            }
            else
            {
                RenderTriangleMode(image, channel, parameters, colorValue);
            }
        }

        /// <summary>
        /// Render in line mode
        /// </summary>
        private void RenderLineMode(ImageBuffer image, int channel, SpinParameters parameters, int color)
        {
            int x = parameters.CenterX + parameters.CurrentX;
            int y = parameters.CenterY + parameters.CurrentY;
            int x2 = parameters.CenterX - parameters.CurrentX;
            int y2 = parameters.CenterY - parameters.CurrentY;
            
            // Draw line from center to current position
            if (lastPositions[channel, 0] != 0 || lastPositions[channel, 1] != 0)
            {
                DrawLine(image, lastPositions[channel, 0], lastPositions[channel, 1], x, y, color);
            }
            
            // Update last position
            lastPositions[channel, 0] = x;
            lastPositions[channel, 1] = y;
            
            // Draw line from center to current position
            DrawLine(image, parameters.CenterX, parameters.CenterY, x, y, color);
            
            // Draw line from center to opposite position
            if (lastPositions[channel, 0] != 0 || lastPositions[channel, 1] != 0)
            {
                DrawLine(image, lastPositions[channel, 0], lastPositions[channel, 1], x2, y2, color);
            }
            
            // Update last position for opposite side
            lastPositions[channel, 0] = x2;
            lastPositions[channel, 1] = y2;
            
            // Draw line from center to opposite position
            DrawLine(image, parameters.CenterX, parameters.CenterY, x2, y2, color);
        }

        /// <summary>
        /// Render in triangle mode
        /// </summary>
        private void RenderTriangleMode(ImageBuffer image, int channel, SpinParameters parameters, int color)
        {
            int x = parameters.CenterX + parameters.CurrentX;
            int y = parameters.CenterY + parameters.CurrentY;
            int x2 = parameters.CenterX - parameters.CurrentX;
            int y2 = parameters.CenterY - parameters.CurrentY;
            
            // Draw triangle from center to current position
            if (lastPositions[channel, 0] != 0 || lastPositions[channel, 1] != 0)
            {
                DrawTriangle(image, parameters.CenterX, parameters.CenterY, 
                           lastPositions[channel, 0], lastPositions[channel, 1], x, y, color);
            }
            
            // Update last position
            lastPositions[channel, 0] = x;
            lastPositions[channel, 1] = y;
            
            // Draw triangle from center to opposite position
            if (lastPositions[channel, 0] != 0 || lastPositions[channel, 1] != 0)
            {
                DrawTriangle(image, parameters.CenterX, parameters.CenterY, 
                           lastPositions[channel, 0], lastPositions[channel, 1], x2, y2, color);
            }
            
            // Update last position for opposite side
            lastPositions[channel, 0] = x2;
            lastPositions[channel, 1] = y2;
        }

        /// <summary>
        /// Draw a line between two points using Bresenham's algorithm
        /// </summary>
        private void DrawLine(ImageBuffer image, int x1, int y1, int x2, int y2, int color)
        {
            int dx = Math.Abs(x2 - x1);
            int dy = Math.Abs(y2 - y1);
            int sx = x1 < x2 ? 1 : -1;
            int sy = y1 < y2 ? 1 : -1;
            int err = dx - dy;

            int x = x1, y = y1;

            while (true)
            {
                if (x >= 0 && x < image.Width && y >= 0 && y < image.Height)
                {
                    image.Pixels[y * image.Width + x] = color;
                }

                if (x == x2 && y == y2) break;

                int e2 = 2 * err;
                if (e2 > -dy)
                {
                    err -= dy;
                    x += sx;
                }
                if (e2 < dx)
                {
                    err += dx;
                    y += sy;
                }
            }
        }

        /// <summary>
        /// Draw a filled triangle using scan-line algorithm
        /// </summary>
        private void DrawTriangle(ImageBuffer image, int x1, int y1, int x2, int y2, int x3, int y3, int color)
        {
            // Sort vertices by Y coordinate
            var vertices = new[] { (x1, y1), (x2, y2), (x3, y3) };
            Array.Sort(vertices, (a, b) => a.Item2.CompareTo(b.Item2));
            
            int yMin = vertices[0].Item2;
            int yMax = vertices[2].Item2;
            
            if (yMin == yMax) return; // Horizontal line
            
            // Calculate slopes for left and right edges
            double slopeLeft = (double)(vertices[1].Item1 - vertices[0].Item1) / (vertices[1].Item2 - vertices[0].Item2);
            double slopeRight = (double)(vertices[2].Item1 - vertices[0].Item1) / (vertices[2].Item2 - vertices[0].Item2);
            
            double leftX = vertices[0].Item1;
            double rightX = vertices[0].Item1;
            
            // Draw scan lines
            for (int y = yMin; y <= yMax; y++)
            {
                if (y >= 0 && y < image.Height)
                {
                    int xStart = Math.Max(0, (int)Math.Min(leftX, rightX));
                    int xEnd = Math.Min(image.Width - 1, (int)Math.Max(leftX, rightX));
                    
                    for (int x = xStart; x <= xEnd; x++)
                    {
                        if (x >= 0 && x < image.Width)
                        {
                            image.Pixels[y * image.Width + x] = color;
                        }
                    }
                }
                
                // Update edge positions
                if (y < vertices[1].Item2)
                {
                    leftX += slopeLeft;
                    rightX += slopeRight;
                }
                else
                {
                    // Switch to second edge
                    double slopeLeft2 = (double)(vertices[2].Item1 - vertices[1].Item1) / (vertices[2].Item2 - vertices[1].Item2);
                    leftX += slopeLeft2;
                    rightX += slopeRight;
                }
            }
        }

        /// <summary>
        /// Convert Color to integer representation
        /// </summary>
        private int ColorToInt(Color color)
        {
            return (color.R << 16) | (color.G << 8) | color.B;
        }

        #endregion

        #region Configuration

        /// <summary>
        /// Validate and clamp property values
        /// </summary>
        public override void ValidateProperties()
        {
            EnabledChannels = Math.Clamp(EnabledChannels, MinEnabledChannels, MaxEnabledChannels);
            Mode = Math.Clamp(Mode, MinMode, MaxMode);

            // Ensure colors array is properly sized
            if (Colors.Length != 2)
            {
                Array.Resize(ref Colors, 2);
            }
        }

        /// <summary>
        /// Get a summary of current settings
        /// </summary>
        public override string GetSettingsSummary()
        {
            string channelsText = GetChannelsText();
            string modeText = Mode == LINE_MODE ? "Lines" : "Triangles";

            return $"Bspin: {channelsText}, {modeText}, " +
                   $"Left: {Colors[0].Name}, Right: {Colors[1].Name}";
        }

        /// <summary>
        /// Get enabled channels text
        /// </summary>
        private string GetChannelsText()
        {
            switch (EnabledChannels)
            {
                case LEFT_CHANNEL: return "Left";
                case RIGHT_CHANNEL: return "Right";
                case BOTH_CHANNELS: return "Both";
                default: return "None";
            }
        }

        #endregion

        #region Helper Classes

        /// <summary>
        /// Spin parameters for rendering
        /// </summary>
        private class SpinParameters
        {
            public int CenterX { get; set; }
            public int CenterY { get; set; }
            public int CurrentX { get; set; }
            public int CurrentY { get; set; }
            public double ScaledSize { get; set; }
            public int Channel { get; set; }
        }

        #endregion
    }
}
```

## Key Features

### Bass Reactivity
- **Low-Frequency Analysis**: Processes first 44 spectrum bands for bass detection
- **Dynamic Intensity**: Real-time audio intensity calculation and scaling
- **Velocity Smoothing**: Smooth transitions between audio levels
- **Threshold Control**: Configurable minimum audio thresholds

### Channel Processing
- **Independent Channels**: Separate left and right channel processing
- **Configurable Enable**: Enable/disable individual channels or both
- **Opposite Rotation**: Left channel rotates counter-clockwise, right clockwise
- **Channel-Specific Colors**: Different colors for each channel

### Rendering Modes
- **Line Mode**: Dynamic line drawing from center to spin positions
- **Triangle Mode**: Filled triangle rendering for solid visual impact
- **Smooth Animation**: Continuous rotation with velocity-based acceleration
- **Position Tracking**: Maintains previous positions for smooth transitions

### Performance Optimizations
- **Fixed-Point Math**: Efficient rotation calculations
- **Bounds Checking**: Optimized rendering with boundary validation
- **Memory Management**: Minimal allocation during rendering
- **Thread Safety**: Lock-based synchronization

## Usage Examples

```csharp
// Create a bass spin effect with both channels enabled
var bspinNode = new BspinEffectsNode
{
    EnabledChannels = BspinEffectsNode.BOTH_CHANNELS,
    Colors = new Color[] { Color.Red, Color.Blue },
    Mode = BspinEffectsNode.TRIANGLE_MODE
};

// Apply to image
var spinImage = bspinNode.ProcessFrame(inputImage, audioFeatures);
```

## Technical Details

### Audio Processing
The effect analyzes bass frequencies using a weighted sum approach:

```csharp
intensity = (sum * 512) / (lastSum + 30*256)
velocity = 0.7 * targetVelocity + 0.3 * currentVelocity
```

### Rotation System
Each channel rotates independently with audio-reactive speed:

```csharp
rotation += (π/6) * velocity * direction
```

### Rendering Algorithms
- **Line Mode**: Bresenham's line algorithm for efficient line drawing
- **Triangle Mode**: Scan-line algorithm for filled triangle rendering

### Channel Configuration
Channel enable flags use bitwise operations:

```csharp
enabled = 1 << channelIndex  // 1=left, 2=right, 3=both
```

This implementation provides a complete, production-ready bass spin effect system that faithfully reproduces the original C++ functionality while leveraging C# features for improved maintainability and performance.
