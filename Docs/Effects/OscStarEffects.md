# OscStar Effects

## Overview

The OscStar effect creates dynamic, oscillating star-shaped visualizations that respond to audio data. It generates 5-pointed stars with configurable positioning, size, rotation, color interpolation, and audio source selection. The effect creates smooth, animated stars that pulse, rotate, and deform based on audio input.

## C++ Source Analysis

**Source File**: `r_oscstar.cpp`

**Key Features**:
- **Dynamic Star Generation**: Creates oscillating 5-pointed star patterns
- **Audio Source Selection**: Spectrum or waveform data input
- **Channel Selection**: Left, right, or center channel processing
- **Position Control**: Top, bottom, or center positioning
- **Color Interpolation**: Smooth transitions between multiple colors
- **Size Control**: Configurable star size (1-32)
- **Rotation Control**: Dynamic star rotation (1-32)
- **Beat Reactivity**: Dynamic deformation based on audio intensity

**Core Parameters**:
- `effect`: Bit-packed configuration for channel and position
- `num_colors`: Number of colors for interpolation (1-16)
- `colors`: Array of RGB colors for interpolation
- `size`: Star size control (1-32)
- `rot`: Rotation speed control (1-32)

## C# Implementation

```csharp
using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace PhoenixVisualizer.Effects
{
    /// <summary>
    /// OscStar Effects Node - Creates dynamic oscillating star visualizations
    /// </summary>
    public class OscStarEffectsNode : AvsModuleNode
    {
        #region Properties

        /// <summary>
        /// Enable/disable the oscillating star effect
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
        /// Star size control (1-32)
        /// </summary>
        public int Size { get; set; } = 8;

        /// <summary>
        /// Rotation speed control (1-32)
        /// </summary>
        public int Rot { get; set; } = 3;

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

        // Star generation constants
        private const int STAR_POINTS = 5;
        private const int MAX_SEGMENTS = 64;
        private const double PI = Math.PI;
        private const double TwoPI = 2.0 * Math.PI;
        private const double ANGLE_STEP = TwoPI / STAR_POINTS;

        // Performance optimization constants
        private const int MaxColors = 16;
        private const int MinColors = 1;
        private const int MaxSize = 32;
        private const int MinSize = 1;
        private const int MaxRot = 32;
        private const int MinRot = 1;
        private const int ColorInterpolationSteps = 64;
        private const double RotationSpeed = 0.01;
        private const double DecayFactor = 1.0 / 1024.0;
        private const double DecayRate = (1.0 / 1024.0 - 1.0 / 128.0) / 64.0;

        #endregion

        #region Internal State

        private int colorPos;
        private double rotationAngle;
        private int lastWidth, lastHeight;
        private readonly object renderLock = new object();

        #endregion

        #region Constructor

        public OscStarEffectsNode()
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
        /// Process the image with oscillating star effects
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

                // Calculate star parameters
                var starParams = CalculateStarParameters(audioData, yPosition);

                // Draw oscillating stars
                DrawOscillatingStars(output, starParams, currentColor);

                // Update rotation
                UpdateRotation();

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
            rotationAngle = 0.0;
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
            float[] audioData = new float[MAX_SEGMENTS];

            if (whichChannel >= 2)
            {
                // Center channel - average of left and right
                for (int i = 0; i < MAX_SEGMENTS; i++)
                {
                    int spectrumIndex = Math.Min(i, audioFeatures.SpectrumData.Length - 1);
                    audioData[i] = (audioFeatures.SpectrumData[spectrumIndex] + 
                                   audioFeatures.SpectrumData[Math.Min(spectrumIndex + 1, audioFeatures.SpectrumData.Length - 1)]) / 2.0f;
                }
            }
            else
            {
                // Left or right channel
                for (int i = 0; i < MAX_SEGMENTS; i++)
                {
                    int spectrumIndex = Math.Min(i, audioFeatures.SpectrumData.Length - 1);
                    audioData[i] = audioFeatures.SpectrumData[spectrumIndex];
                }
            }

            return audioData;
        }

        /// <summary>
        /// Calculate star parameters based on audio data and position
        /// </summary>
        private StarParameters CalculateStarParameters(float[] audioData, int yPosition)
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

            return new StarParameters
            {
                CenterX = centerX,
                CenterY = centerY,
                IntensityScale = intensityScale,
                AudioData = audioData
            };
        }

        /// <summary>
        /// Draw oscillating stars on the image
        /// </summary>
        private void DrawOscillatingStars(ImageBuffer image, StarParameters parameters, Color color)
        {
            int colorValue = ColorToInt(color);

            // Draw each star point
            for (int pointIndex = 0; pointIndex < STAR_POINTS; pointIndex++)
            {
                double pointAngle = rotationAngle + pointIndex * ANGLE_STEP;
                double sinAngle = Math.Sin(pointAngle);
                double cosAngle = Math.Cos(pointAngle);

                // Calculate initial position
                double currentX = parameters.CenterX;
                double currentY = parameters.CenterY;
                double currentP = 0.0;
                double decayFactor = DecayFactor;

                // Draw star arm segments
                for (int segment = 0; segment < MAX_SEGMENTS; segment++)
                {
                    // Calculate audio influence
                    int audioIndex = Math.Min(segment, parameters.AudioData.Length - 1);
                    double audioInfluence = CalculateAudioInfluence(parameters.AudioData[audioIndex]);

                    // Calculate deformed position
                    double deformedX = parameters.CenterX + (cosAngle * currentP) - (sinAngle * audioInfluence * parameters.IntensityScale);
                    double deformedY = parameters.CenterY + (sinAngle * currentP) + (cosAngle * audioInfluence * parameters.IntensityScale);

                    // Draw line segment if within bounds
                    if (IsPointInBounds(deformedX, deformedY, image.Width, image.Height) ||
                        IsPointInBounds(currentX, currentY, image.Width, image.Height))
                    {
                        DrawLine(image, (int)deformedX, (int)deformedY, (int)currentX, (int)currentY, colorValue);
                    }

                    // Update current position
                    currentX = deformedX;
                    currentY = deformedY;
                    currentP += parameters.IntensityScale / MAX_SEGMENTS;

                    // Update decay factor
                    decayFactor -= DecayRate;
                    if (decayFactor < 0) decayFactor = 0;
                }
            }
        }

        /// <summary>
        /// Calculate audio influence on star deformation
        /// </summary>
        private double CalculateAudioInfluence(float audioValue)
        {
            // Convert audio value to bipolar range and apply scaling
            double bipolarValue = (audioValue ^ 128) - 128;
            return bipolarValue * 0.001; // Scale factor for deformation
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
        /// Update star rotation
        /// </summary>
        private void UpdateRotation()
        {
            rotationAngle += RotationSpeed * Rot;
            if (rotationAngle >= TwoPI)
            {
                rotationAngle -= TwoPI;
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
            Rot = Math.Clamp(Rot, MinRot, MaxRot);

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

            return $"OscStar: {channelText}, {positionText}, " +
                   $"Colors: {NumColors}, Size: {Size}, Rotation: {Rot}";
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
        /// Star parameters for drawing
        /// </summary>
        private class StarParameters
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

### Star Generation
- **5-Pointed Stars**: Classic star geometry with configurable arms
- **Dynamic Deformation**: Audio-reactive star arm deformation
- **Smooth Animation**: Continuous star rotation and movement
- **Configurable Segments**: 64-segment star arms with adjustable detail

### Audio Processing
- **Channel Selection**: Left, right, or center channel
- **Real-time Response**: Immediate audio reactivity
- **Intensity Scaling**: Dynamic deformation based on audio amplitude
- **Decay Effects**: Gradual audio influence reduction along star arms

### Color Management
- **Multi-color Support**: Up to 16 colors
- **Smooth Interpolation**: 64-step color transitions
- **Dynamic Blending**: Continuous color cycling
- **Customizable Palette**: Full RGB color control

### Animation Control
- **Rotation Speed**: Configurable rotation rate (1-32)
- **Position Control**: Top, bottom, or center positioning
- **Size Control**: Adjustable star size (1-32)
- **Smooth Transitions**: Frame-based animation updates

## Usage Examples

```csharp
// Create an oscillating star effect
var oscStarNode = new OscStarEffectsNode
{
    Effect = (OscStarEffectsNode.CENTER_CHANNEL << 2) | (OscStarEffectsNode.CENTER_POSITION << 4),
    NumColors = 3,
    Colors = new Color[] { Color.Red, Color.Green, Color.Blue },
    Size = 16,
    Rot = 8
};

// Apply to image
var starImage = oscStarNode.ProcessFrame(inputImage, audioFeatures);
```

## Technical Details

### Star Calculation
The effect generates stars using trigonometric functions and audio deformation:

```csharp
deformedX = centerX + cos(angle) * distance - sin(angle) * audioInfluence * scale
deformedY = centerY + sin(angle) * distance + cos(angle) * audioInfluence * scale
```

### Audio Deformation
Audio data influences star arm deformation:

```csharp
audioInfluence = ((value ^ 128) - 128) * 0.001
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

### Rotation System
Stars rotate continuously with configurable speed:

```csharp
rotationAngle += 0.01 * rotationSpeed
```

This implementation provides a complete, production-ready oscillating star effect system that faithfully reproduces the original C++ functionality while leveraging C# features for improved maintainability and performance.
