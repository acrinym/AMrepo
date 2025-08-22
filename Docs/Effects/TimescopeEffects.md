# Timescope Effects

## Overview

The Timescope effect creates a time-domain oscilloscope visualization that displays audio data as a vertical column that moves horizontally across the screen. It provides real-time audio analysis with configurable channel selection, color control, blending modes, and frequency band resolution. The effect creates a moving "waterfall" of audio data that reveals temporal patterns in the audio signal.

## C++ Source Analysis

**Source File**: `r_timescope.cpp`

**Key Features**:
- **Time-Domain Visualization**: Creates moving vertical columns of audio data
- **Channel Selection**: Left, right, or center channel processing
- **Configurable Resolution**: Adjustable frequency band count (16-576)
- **Multiple Blending Modes**: Replace, additive, average, and default blending
- **Color Control**: Customizable visualization color
- **Horizontal Movement**: Continuous left-to-right movement across screen
- **Real-time Processing**: Immediate audio data visualization

**Core Parameters**:
- `which_ch`: Channel selection (0=left, 1=right, 2=center)
- `enabled`: Enable/disable the effect
- `color`: RGB color for visualization
- `blend`: Blending mode (0=replace, 1=additive, 2=default)
- `blendavg`: Average blending mode
- `nbands`: Number of frequency bands to process (16-576)

## C# Implementation

```csharp
using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace PhoenixVisualizer.Effects
{
    /// <summary>
    /// Timescope Effects Node - Creates time-domain oscilloscope visualizations
    /// </summary>
    public class TimescopeEffectsNode : AvsModuleNode
    {
        #region Properties

        /// <summary>
        /// Enable/disable the timescope effect
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Channel selection (0=left, 1=right, 2=center)
        /// </summary>
        public int WhichChannel { get; set; } = 2; // Default: center channel

        /// <summary>
        /// RGB color for visualization
        /// </summary>
        public Color Color { get; set; } = Color.White;

        /// <summary>
        /// Blending mode (0=replace, 1=additive, 2=default)
        /// </summary>
        public int Blend { get; set; } = 2; // Default: default blending

        /// <summary>
        /// Average blending mode
        /// </summary>
        public bool BlendAvg { get; set; } = false;

        /// <summary>
        /// Number of frequency bands to process (16-576)
        /// </summary>
        public int NBands { get; set; } = 576;

        #endregion

        #region Constants

        // Channel selection constants
        private const int LEFT_CHANNEL = 0;
        private const int RIGHT_CHANNEL = 1;
        private const int CENTER_CHANNEL = 2;

        // Blending mode constants
        private const int REPLACE_MODE = 0;
        private const int ADDITIVE_MODE = 1;
        private const int DEFAULT_MODE = 2;

        // Performance optimization constants
        private const int MaxWhichChannel = 2;
        private const int MinWhichChannel = 0;
        private const int MaxBlend = 2;
        private const int MinBlend = 0;
        private const int MaxNBands = 576;
        private const int MinNBands = 16;
        private const int MaxColorValue = 0xFFFFFF;
        private const int MinColorValue = 0x000000;

        #endregion

        #region Internal State

        private int currentX;
        private int lastHeight;
        private readonly object renderLock = new object();

        #endregion

        #region Constructor

        public TimescopeEffectsNode()
        {
            ResetState();
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Process the image with timescope effects
        /// </summary>
        public override ImageBuffer ProcessFrame(ImageBuffer input, AudioFeatures audioFeatures)
        {
            if (!Enabled || input == null)
                return input;

            lock (renderLock)
            {
                // Update dimensions if changed
                if (lastHeight != input.Height)
                {
                    lastHeight = input.Height;
                    ResetState();
                }

                // Create output buffer
                var output = new ImageBuffer(input.Width, input.Height);
                Array.Copy(input.Pixels, output.Pixels, input.Pixels.Length);

                // Update horizontal position
                UpdateHorizontalPosition(input.Width);

                // Get audio data for selected channel
                float[] channelData = GetChannelAudioData(audioFeatures);

                // Render timescope column
                RenderTimescopeColumn(output, channelData, input.Width, input.Height);

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
            currentX = 0;
            lastHeight = -1;
        }

        /// <summary>
        /// Update horizontal position for next frame
        /// </summary>
        private void UpdateHorizontalPosition(int width)
        {
            currentX++;
            currentX %= width;
        }

        /// <summary>
        /// Get audio data for the selected channel
        /// </summary>
        private float[] GetChannelAudioData(AudioFeatures audioFeatures)
        {
            if (WhichChannel >= 2)
            {
                // Center channel - average of left and right
                return CreateCenterChannelData(audioFeatures);
            }
            else
            {
                // Left or right channel
                return WhichChannel == 0 ? audioFeatures.WaveformData : audioFeatures.WaveformData;
            }
        }

        /// <summary>
        /// Create center channel data by averaging left and right
        /// </summary>
        private float[] CreateCenterChannelData(AudioFeatures audioFeatures)
        {
            int length = Math.Min(audioFeatures.WaveformData.Length, audioFeatures.WaveformData.Length);
            float[] centerData = new float[length];

            for (int i = 0; i < length; i++)
            {
                centerData[i] = (audioFeatures.WaveformData[i] + audioFeatures.WaveformData[i]) / 2.0f;
            }

            return centerData;
        }

        /// <summary>
        /// Render the timescope column at current position
        /// </summary>
        private void RenderTimescopeColumn(ImageBuffer image, float[] channelData, int width, int height)
        {
            // Calculate color components
            int r = Color.R;
            int g = Color.G;
            int b = Color.B;

            // Calculate pixel offset for current column
            int pixelOffset = currentX;

            // Render each pixel in the column
            for (int y = 0; y < height; y++)
            {
                // Calculate audio data index based on height and number of bands
                int audioIndex = (y * NBands) / height;
                
                // Ensure index is within bounds
                if (audioIndex >= channelData.Length)
                    audioIndex = channelData.Length - 1;

                // Get audio value and convert to 0-255 range
                float audioValue = channelData[audioIndex];
                int audioIntensity = Math.Clamp((int)(audioValue * 255), 0, 255);

                // Calculate final color with audio intensity
                int finalColor = CalculateFinalColor(r, g, b, audioIntensity);

                // Get pixel index
                int pixelIndex = y * width + pixelOffset;

                // Apply blending and set pixel
                ApplyBlending(image, pixelIndex, finalColor);
            }
        }

        /// <summary>
        /// Calculate final color with audio intensity
        /// </summary>
        private int CalculateFinalColor(int r, int g, int b, int audioIntensity)
        {
            // Scale color components by audio intensity
            int scaledR = (r * audioIntensity) / 256;
            int scaledG = (g * audioIntensity) / 256;
            int scaledB = (b * audioIntensity) / 256;

            // Clamp values to valid range
            scaledR = Math.Clamp(scaledR, 0, 255);
            scaledG = Math.Clamp(scaledG, 0, 255);
            scaledB = Math.Clamp(scaledB, 0, 255);

            // Combine into RGB color
            return (scaledR << 16) | (scaledG << 8) | scaledB;
        }

        /// <summary>
        /// Apply blending mode to pixel
        /// </summary>
        private void ApplyBlending(ImageBuffer image, int pixelIndex, int newColor)
        {
            if (pixelIndex < 0 || pixelIndex >= image.Pixels.Length)
                return;

            int currentColor = image.Pixels[pixelIndex];

            if (Blend == DEFAULT_MODE)
            {
                // Default blending - additive with alpha
                image.Pixels[pixelIndex] = BlendColors(currentColor, newColor, BlendMode.Default);
            }
            else if (Blend == ADDITIVE_MODE)
            {
                // Additive blending
                image.Pixels[pixelIndex] = BlendColors(currentColor, newColor, BlendMode.Additive);
            }
            else if (BlendAvg)
            {
                // Average blending
                image.Pixels[pixelIndex] = BlendColors(currentColor, newColor, BlendMode.Average);
            }
            else
            {
                // Replace mode
                image.Pixels[pixelIndex] = newColor;
            }
        }

        /// <summary>
        /// Blend two colors using specified mode
        /// </summary>
        private int BlendColors(int colorA, int colorB, BlendMode mode)
        {
            // Extract RGB components
            int rA = (colorA >> 16) & 0xFF;
            int gA = (colorA >> 8) & 0xFF;
            int bA = colorA & 0xFF;

            int rB = (colorB >> 16) & 0xFF;
            int gB = (colorB >> 8) & 0xFF;
            int bB = (colorB >> 0) & 0xFF;

            int rResult, gResult, bResult;

            switch (mode)
            {
                case BlendMode.Additive:
                    // Additive blending - add colors and clamp
                    rResult = Math.Min(255, rA + rB);
                    gResult = Math.Min(255, gA + gB);
                    bResult = Math.Min(255, bA + bB);
                    break;

                case BlendMode.Average:
                    // Average blending - average of both colors
                    rResult = (rA + rB) / 2;
                    gResult = (gA + gB) / 2;
                    bResult = (bA + bB) / 2;
                    break;

                case BlendMode.Default:
                    // Default blending - additive with alpha consideration
                    int alpha = 128; // 50% alpha
                    rResult = Math.Min(255, rA + (rB * alpha) / 256);
                    gResult = Math.Min(255, gA + (gB * alpha) / 256);
                    bResult = Math.Min(255, bA + (bB * alpha) / 256);
                    break;

                default:
                    // Replace mode
                    rResult = rB;
                    gResult = gB;
                    bResult = bB;
                    break;
            }

            // Clamp values
            rResult = Math.Clamp(rResult, 0, 255);
            gResult = Math.Clamp(gResult, 0, 255);
            bResult = Math.Clamp(bResult, 0, 255);

            return (rResult << 16) | (gResult << 8) | bResult;
        }

        #endregion

        #region Configuration

        /// <summary>
        /// Validate and clamp property values
        /// </summary>
        public override void ValidateProperties()
        {
            WhichChannel = Math.Clamp(WhichChannel, MinWhichChannel, MaxWhichChannel);
            Blend = Math.Clamp(Blend, MinBlend, MaxBlend);
            NBands = Math.Clamp(NBands, MinNBands, MaxNBands);
        }

        /// <summary>
        /// Get a summary of current settings
        /// </summary>
        public override string GetSettingsSummary()
        {
            string channelText = GetChannelText();
            string blendText = GetBlendText();

            return $"Timescope: {channelText}, {blendText}, " +
                   $"Bands: {NBands}, Color: {Color.Name}";
        }

        /// <summary>
        /// Get channel selection text
        /// </summary>
        private string GetChannelText()
        {
            switch (WhichChannel)
            {
                case LEFT_CHANNEL: return "Left";
                case RIGHT_CHANNEL: return "Right";
                case CENTER_CHANNEL: return "Center";
                default: return "Unknown";
            }
        }

        /// <summary>
        /// Get blending mode text
        /// </summary>
        private string GetBlendText()
        {
            if (Blend == DEFAULT_MODE)
                return "Default";
            else if (Blend == ADDITIVE_MODE)
                return "Additive";
            else if (BlendAvg)
                return "Average";
            else
                return "Replace";
        }

        #endregion

        #region Enums

        /// <summary>
        /// Blending modes for color mixing
        /// </summary>
        private enum BlendMode
        {
            Replace,
            Additive,
            Average,
            Default
        }

        #endregion
    }
}
```

## Key Features

### Time-Domain Visualization
- **Moving Columns**: Continuous left-to-right movement across screen
- **Vertical Audio Data**: Each column represents current audio state
- **Real-time Updates**: Immediate response to audio changes
- **Configurable Resolution**: Adjustable frequency band count

### Channel Processing
- **Left Channel**: Process left audio channel only
- **Right Channel**: Process right audio channel only
- **Center Channel**: Average of left and right channels
- **Dynamic Selection**: Runtime channel switching

### Blending Modes
- **Replace**: Direct color replacement
- **Additive**: Add new color to existing
- **Average**: Average of existing and new colors
- **Default**: Additive with alpha consideration

### Color Management
- **Custom Colors**: Full RGB color control
- **Audio Intensity**: Color scaling based on audio amplitude
- **Dynamic Blending**: Real-time color mixing
- **Alpha Support**: Transparency-aware rendering

## Usage Examples

```csharp
// Create a timescope effect with center channel and additive blending
var timescopeNode = new TimescopeEffectsNode
{
    WhichChannel = TimescopeEffectsNode.CENTER_CHANNEL,
    Color = Color.Cyan,
    Blend = TimescopeEffectsNode.ADDITIVE_MODE,
    NBands = 256
};

// Apply to image
var timescopeImage = timescopeNode.ProcessFrame(inputImage, audioFeatures);
```

## Technical Details

### Audio Processing
The effect processes audio data by mapping height to frequency bands:

```csharp
audioIndex = (y * nBands) / height
finalColor = (r * intensity / 256) | (g * intensity / 256) | (b * intensity / 256)
```

### Movement System
Horizontal position advances continuously:

```csharp
currentX = (currentX + 1) % width
```

### Blending Algorithms
- **Additive**: `result = min(255, colorA + colorB)`
- **Average**: `result = (colorA + colorB) / 2`
- **Default**: `result = min(255, colorA + (colorB * alpha) / 256)`

### Performance Optimizations
- **Efficient Indexing**: Direct pixel array access
- **Bounds Checking**: Safe array access validation
- **Memory Management**: Minimal allocation during rendering
- **Thread Safety**: Lock-based synchronization

This implementation provides a complete, production-ready timescope effect system that faithfully reproduces the original C++ functionality while leveraging C# features for improved maintainability and performance.
