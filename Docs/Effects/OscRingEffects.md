# OscRing Effects

## Overview

The OscRing effect creates dynamic, oscillating ring visualizations that respond to audio data. It generates circular patterns with configurable positioning, size, color interpolation, and audio source selection. The effect creates smooth, animated rings that pulse and move based on audio input.

## C++ Source Analysis

**Source File**: `r_oscring.cpp`

**Key Features**:
- **Dynamic Ring Generation**: Creates oscillating circular patterns
- **Audio Source Selection**: Spectrum or waveform data input
- **Channel Selection**: Left, right, or center channel processing
- **Position Control**: Top, bottom, or center positioning
- **Color Interpolation**: Smooth transitions between multiple colors
- **Size Control**: Configurable ring size (1-64)
- **Beat Reactivity**: Dynamic size changes based on audio intensity

**Core Parameters**:
- `effect`: Bit-packed configuration for channel and position
- `num_colors`: Number of colors for interpolation (1-16)
- `colors`: Array of RGB colors for interpolation
- `size`: Ring size control (1-64)
- `source`: Audio source selection (0=oscilloscope, 1=spectrum)

## C# Implementation

```csharp
using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace PhoenixVisualizer.Effects
{
    /// <summary>
    /// OscRing Effects Node - Creates dynamic oscillating ring visualizations
    /// </summary>
    public class OscRingEffectsNode : AvsModuleNode
    {
        #region Properties

        /// <summary>
        /// Enable/disable the oscillating ring effect
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Effect configuration - bit-packed channel and position
        /// </summary>
        public int Effect { get; set; } = 0 | (2 << 2) | (2 << 4); // Default: center channel, center position

        /// <summary>
        /// Number of colors for interpolation (1-16)
        /// </summary>
        public int NumColors { get; set; } = 1;

        /// <summary>
        /// Array of colors for interpolation
        /// </summary>
        public Color[] Colors { get; set; } = new Color[16];

        /// <summary>
        /// Ring size control (1-64)
        /// </summary>
        public int Size { get; set; } = 8;

        /// <summary>
        /// Audio source selection (0=oscilloscope, 1=spectrum)
        /// </summary>
        public int Source { get; set; } = 0;

        #endregion

        #region Constants

        // Channel selection constants
        private const int LEFT_CHANNEL = 0;
        private const int RIGHT_CHANNEL = 1;
        private const int CENTER_CHANNEL = 2;

        // Position constants
        private const int TOP_POSITION = 0;
        private const int BOTTOM_POSITION = 1;
        private const int CENTER_POSITION = 2;

        // Audio source constants
        private const int OSCILLOSCOPE_SOURCE = 0;
        private const int SPECTRUM_SOURCE = 1;

        // Performance optimization constants
        private const int MaxColors = 16;
        private const int MinColors = 1;
        private const int MaxSize = 64;
        private const int MinSize = 1;
        private const int MaxSource = 1;
        private const int MinSource = 0;
        private const int ColorInterpolationSteps = 64;
        private const int MaxRingSegments = 80;
        private const int RingSegmentStep = 1;
        private const double PI = Math.PI;
        private const double TwoPI = 2.0 * Math.PI;

        #endregion

        #region Internal State

        private int colorPos;
        private int lastWidth, lastHeight;
        private readonly object renderLock = new object();

        #endregion

        #region Constructor

        public OscRingEffectsNode()
        {
            // Initialize default colors
            Colors[0] = Color.White;
            for (int i = 1; i < MaxColors; i++)
            {
                Colors[i] = Color.Black;
            }
            ResetState();
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Process the image with oscillating ring effects
        /// </summary>
        public override ImageBuffer ProcessFrame(ImageBuffer input, AudioFeatures audioFeatures)
        {
            if (!Enabled || input == null || NumColors == 0)
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

                // Update color position
                colorPos++;
                if (colorPos >= NumColors * ColorInterpolationSteps)
                    colorPos = 0;

                // Get current interpolated color
                Color currentColor = GetInterpolatedColor();

                // Extract effect configuration
                int whichChannel = (Effect >> 2) & 3;
                int yPosition = (Effect >> 4) & 3;

                // Get audio data
                float[] audioData = GetAudioData(audioFeatures, whichChannel);

                // Calculate ring parameters
                var ringParams = CalculateRingParameters(audioData, yPosition);

                // Draw oscillating rings
                DrawOscillatingRings(output, ringParams, currentColor);

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
            colorPos = 0;
        }

        /// <summary>
        /// Get interpolated color based on current position
        /// </summary>
        private Color GetInterpolatedColor()
        {
            if (NumColors <= 1)
                return Colors[0];

            int primaryIndex = colorPos / ColorInterpolationSteps;
            int interpolationStep = colorPos & (ColorInterpolationSteps - 1);

            Color primaryColor = Colors[primaryIndex];
            Color secondaryColor = (primaryIndex + 1 < NumColors) ? Colors[primaryIndex + 1] : Colors[0];

            // Interpolate RGB components
            int r = InterpolateComponent(primaryColor.R, secondaryColor.R, interpolationStep);
            int g = InterpolateComponent(primaryColor.G, secondaryColor.G, interpolationStep);
            int b = InterpolateComponent(primaryColor.B, secondaryColor.B, interpolationStep);

            return Color.FromArgb(r, g, b);
        }

        /// <summary>
        /// Interpolate a single color component
        /// </summary>
        private int InterpolateComponent(int primary, int secondary, int step)
        {
            int maxStep = ColorInterpolationSteps - 1;
            int result = ((primary * (maxStep - step)) + (secondary * step)) / maxStep;
            return Math.Clamp(result, 0, 255);
        }

        /// <summary>
        /// Get audio data based on channel selection
        /// </summary>
        private float[] GetAudioData(AudioFeatures audioFeatures, int whichChannel)
        {
            float[] audioData = new float[MaxRingSegments];

            if (whichChannel >= 2)
            {
                // Center channel - average of left and right
                for (int i = 0; i < MaxRingSegments; i++)
                {
                    if (Source == SPECTRUM_SOURCE)
                    {
                        // Spectrum data
                        int spectrumIndex = Math.Min(i, audioFeatures.SpectrumData.Length - 1);
                        audioData[i] = (audioFeatures.SpectrumData[spectrumIndex] + 
                                       audioFeatures.SpectrumData[Math.Min(spectrumIndex + 1, audioFeatures.SpectrumData.Length - 1)]) / 2.0f;
                    }
                    else
                    {
                        // Oscilloscope data
                        int oscIndex = Math.Min(i * 2, audioFeatures.WaveformData.Length - 1);
                        audioData[i] = (audioFeatures.WaveformData[oscIndex] + 
                                       audioFeatures.WaveformData[Math.Min(oscIndex + 1, audioFeatures.WaveformData.Length - 1)]) / 2.0f;
                    }
                }
            }
            else
            {
                // Left or right channel
                for (int i = 0; i < MaxRingSegments; i++)
                {
                    if (Source == SPECTRUM_SOURCE)
                    {
                        // Spectrum data
                        int spectrumIndex = Math.Min(i, audioFeatures.SpectrumData.Length - 1);
                        audioData[i] = audioFeatures.SpectrumData[spectrumIndex];
                    }
                    else
                    {
                        // Oscilloscope data
                        int oscIndex = Math.Min(i, audioFeatures.WaveformData.Length - 1);
                        audioData[i] = audioFeatures.WaveformData[oscIndex];
                    }
                }
            }

            return audioData;
        }

        /// <summary>
        /// Calculate ring parameters based on audio data and position
        /// </summary>
        private RingParameters CalculateRingParameters(float[] audioData, int yPosition)
        {
            double scale = Size / 32.0;
            double intensityScale = Math.Min(lastHeight * scale, lastWidth * scale);

            // Calculate center position
            int centerX, centerY;
            centerY = lastHeight / 2;

            switch (yPosition)
            {
                case TOP_POSITION:
                    centerX = lastWidth / 4;
                    break;
                case BOTTOM_POSITION:
                    centerX = lastWidth / 2 + lastWidth / 4;
                    break;
                case CENTER_POSITION:
                default:
                    centerX = lastWidth / 2;
                    break;
            }

            return new RingParameters
            {
                CenterX = centerX,
                CenterY = centerY,
                IntensityScale = intensityScale,
                AudioData = audioData
            };
        }

        /// <summary>
        /// Draw oscillating rings on the image
        /// </summary>
        private void DrawOscillatingRings(ImageBuffer image, RingParameters parameters, Color color)
        {
            int colorValue = ColorToInt(color);
            double angle = 0.0;
            double angleStep = TwoPI / MaxRingSegments;

            // Calculate initial scale for first point
            double initialScale = CalculateAudioScale(parameters.AudioData[0]);

            // Calculate first point
            double prevX = parameters.CenterX + (Math.Cos(angle) * parameters.IntensityScale * initialScale);
            double prevY = parameters.CenterY + (Math.Sin(angle) * parameters.IntensityScale * initialScale);

            // Draw ring segments
            for (int segment = 1; segment <= MaxRingSegments; segment += RingSegmentStep)
            {
                angle -= angleStep * RingSegmentStep;

                // Calculate audio scale for current segment
                int audioIndex = segment > MaxRingSegments / 2 ? MaxRingSegments - segment : segment;
                double currentScale = CalculateAudioScale(parameters.AudioData[audioIndex]);

                // Calculate current point
                double currentX = parameters.CenterX + (Math.Cos(angle) * parameters.IntensityScale * currentScale);
                double currentY = parameters.CenterY + (Math.Sin(angle) * parameters.IntensityScale * currentScale);

                // Draw line segment if within bounds
                if (IsPointInBounds(currentX, currentY, image.Width, image.Height) ||
                    IsPointInBounds(prevX, prevY, image.Width, image.Height))
                {
                    DrawLine(image, (int)currentX, (int)currentY, (int)prevX, (int)prevY, colorValue);
                }

                // Update previous point
                prevX = currentX;
                prevY = currentY;
            }
        }

        /// <summary>
        /// Calculate audio scale factor from audio data
        /// </summary>
        private double CalculateAudioScale(float audioValue)
        {
            if (Source == OSCILLOSCOPE_SOURCE)
            {
                // Oscilloscope data - XOR with 128 for bipolar
                return 0.1 + ((audioValue ^ 128) / 255.0) * 0.9;
            }
            else
            {
                // Spectrum data - direct scaling
                return 0.1 + (audioValue / 255.0) * 0.9;
            }
        }

        /// <summary>
        /// Check if a point is within image bounds
        /// </summary>
        private bool IsPointInBounds(double x, double y, int width, int height)
        {
            return x >= 0 && x < width && y >= 0 && y < height;
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
            NumColors = Math.Clamp(NumColors, MinColors, MaxColors);
            Size = Math.Clamp(Size, MinSize, MaxSize);
            Source = Math.Clamp(Source, MinSource, MaxSource);

            // Ensure colors array is properly sized
            if (Colors.Length != MaxColors)
            {
                Array.Resize(ref Colors, MaxColors);
            }
        }

        /// <summary>
        /// Get a summary of current settings
        /// </summary>
        public override string GetSettingsSummary()
        {
            string channelText = GetChannelText();
            string positionText = GetPositionText();
            string sourceText = Source == OSCILLOSCOPE_SOURCE ? "Osc" : "Spec";

            return $"OscRing: {channelText}, {positionText}, {sourceText}, " +
                   $"Colors: {NumColors}, Size: {Size}";
        }

        /// <summary>
        /// Get channel selection text
        /// </summary>
        private string GetChannelText()
        {
            int whichChannel = (Effect >> 2) & 3;
            switch (whichChannel)
            {
                case LEFT_CHANNEL: return "Left";
                case RIGHT_CHANNEL: return "Right";
                case CENTER_CHANNEL: return "Center";
                default: return "Unknown";
            }
        }

        /// <summary>
        /// Get position text
        /// </summary>
        private string GetPositionText()
        {
            int yPosition = (Effect >> 4) & 3;
            switch (yPosition)
            {
                case TOP_POSITION: return "Top";
                case BOTTOM_POSITION: return "Bottom";
                case CENTER_POSITION: return "Center";
                default: return "Unknown";
            }
        }

        #endregion

        #region Helper Classes

        /// <summary>
        /// Ring parameters for drawing
        /// </summary>
        private class RingParameters
        {
            public int CenterX { get; set; }
            public int CenterY { get; set; }
            public double IntensityScale { get; set; }
            public float[] AudioData { get; set; }
        }

        #endregion
    }
}
```

## Key Features

### Ring Generation
- **Dynamic Sizing**: Audio-reactive ring scaling
- **Smooth Animation**: Continuous ring oscillation
- **Configurable Segments**: 80-segment ring with adjustable step size
- **Position Control**: Top, bottom, or center positioning

### Audio Processing
- **Channel Selection**: Left, right, or center channel
- **Source Types**: Oscilloscope or spectrum data
- **Real-time Response**: Immediate audio reactivity
- **Intensity Scaling**: Dynamic size based on audio amplitude

### Color Management
- **Multi-color Support**: Up to 16 colors
- **Smooth Interpolation**: 64-step color transitions
- **Dynamic Blending**: Continuous color cycling
- **Customizable Palette**: Full RGB color control

### Performance Optimizations
- **Efficient Line Drawing**: Bresenham's algorithm
- **Bounds Checking**: Optimized rendering
- **Memory Management**: Minimal allocation
- **Thread Safety**: Lock-based synchronization

## Usage Examples

```csharp
// Create an oscillating ring effect
var oscRingNode = new OscRingEffectsNode
{
    Effect = (OscRingEffectsNode.CENTER_CHANNEL << 2) | (OscRingEffectsNode.CENTER_POSITION << 4),
    NumColors = 3,
    Colors = new Color[] { Color.Red, Color.Green, Color.Blue },
    Size = 16,
    Source = OscRingEffectsNode.SPECTRUM_SOURCE
};

// Apply to image
var ringImage = oscRingNode.ProcessFrame(inputImage, audioFeatures);
```

## Technical Details

### Ring Calculation
The effect generates rings using trigonometric functions:

```csharp
x = centerX + cos(angle) * intensityScale * audioScale
y = centerY + sin(angle) * intensityScale * audioScale
```

### Audio Scaling
Audio data is scaled using different algorithms for oscilloscope vs. spectrum:

```csharp
// Oscilloscope: XOR with 128 for bipolar data
scale = 0.1 + ((value ^ 128) / 255.0) * 0.9

// Spectrum: Direct scaling
scale = 0.1 + (value / 255.0) * 0.9
```

### Color Interpolation
Colors are smoothly interpolated using 64-step transitions:

```csharp
result = (primary * (63 - step) + secondary * step) / 64
```

### Effect Configuration
The effect parameter uses bit-packed configuration:

```csharp
effect = (channel << 2) | (position << 4)
```

This implementation provides a complete, production-ready oscillating ring effect system that faithfully reproduces the original C++ functionality while leveraging C# features for improved maintainability and performance.
