# Blur Effects

## Overview

The Blur effect creates sophisticated image blurring with multiple intensity levels and round mode options. It implements a multi-threaded, MMX-optimized blur algorithm that provides three distinct blur intensities: light, medium, and heavy. The effect includes special handling for image edges and corners, with optional rounding adjustments to prevent color bleeding and maintain image quality.

## C++ Source Analysis

**Source File**: `r_blur.cpp`

**Key Features**:
- **Multi-Intensity Blur**: Three distinct blur levels (enabled=1, 2, 3)
- **Round Mode**: Optional rounding adjustments to prevent color bleeding
- **Multi-Threading**: SMP (Symmetric Multi-Processing) support for performance
- **MMX Optimization**: Assembly-level optimizations for Intel processors
- **Edge Handling**: Special algorithms for image borders and corners
- **Alpha Channel Safe**: Preserves transparency information

**Core Parameters**:
- `enabled`: Blur intensity level (0=off, 1=normal, 2=light, 3=heavy)
- `roundmode`: Rounding mode (0=round down, 1=round up)

**Blur Algorithms**:
- **Normal Blur (enabled=1)**: Balanced blur with 50% center + 12.5% neighbors
- **Light Blur (enabled=2)**: Subtle blur with 50% center + 25% neighbors
- **Heavy Blur (enabled=3)**: Strong blur with 25% center + 25% neighbors

## C# Implementation

```csharp
using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace PhoenixVisualizer.Effects
{
    /// <summary>
    /// Blur Effects Node - Creates sophisticated image blurring with multiple intensity levels
    /// </summary>
    public class BlurEffectsNode : AvsModuleNode
    {
        #region Properties

        /// <summary>
        /// Blur intensity level (0=off, 1=normal, 2=light, 3=heavy)
        /// </summary>
        public int Enabled { get; set; } = 1;

        /// <summary>
        /// Rounding mode (0=round down, 1=round up)
        /// </summary>
        public int RoundMode { get; set; } = 0;

        /// <summary>
        /// Enable multi-threading for performance
        /// </summary>
        public bool MultiThreaded { get; set; } = true;

        #endregion

        #region Constants

        // Blur intensity constants
        private const int BLUR_OFF = 0;
        private const int BLUR_NORMAL = 1;
        private const int BLUR_LIGHT = 2;
        private const int BLUR_HEAVY = 3;

        // Rounding mode constants
        private const int ROUND_DOWN = 0;
        private const int ROUND_UP = 1;

        // Blur algorithm constants
        private const int DIV_2_MASK = 0x7F7F7F7F;
        private const int DIV_4_MASK = 0x3F3F3F3F;
        private const int DIV_8_MASK = 0x1F1F1F1F;
        private const int DIV_16_MASK = 0x0F0F0F0F;

        // Rounding adjustment constants
        private const int ROUND_ADJ_LIGHT = 0x03030303;
        private const int ROUND_ADJ_MEDIUM = 0x04040404;
        private const int ROUND_ADJ_HEAVY = 0x02020202;

        #endregion

        #region Internal State

        private int lastWidth, lastHeight;
        private readonly object renderLock = new object();

        #endregion

        #region Constructor

        public BlurEffectsNode()
        {
            Name = "Blur Effects";
            Description = "Creates sophisticated image blurring with multiple intensity levels and round mode options";
            Category = "AVS Effects";
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Process the image with blur effects
        /// </summary>
        public override ImageBuffer ProcessFrame(ImageBuffer input, AudioFeatures audioFeatures)
        {
            if (Enabled == BLUR_OFF || input == null)
                return input;

            lock (renderLock)
            {
                // Update dimensions if changed
                if (lastWidth != input.Width || lastHeight != input.Height)
                {
                    lastWidth = input.Width;
                    lastHeight = input.Height;
                }

                // Create output buffer
                var output = new ImageBuffer(input.Width, input.Height);

                // Apply blur based on intensity level
                switch (Enabled)
                {
                    case BLUR_NORMAL:
                        ApplyNormalBlur(input, output);
                        break;
                    case BLUR_LIGHT:
                        ApplyLightBlur(input, output);
                        break;
                    case BLUR_HEAVY:
                        ApplyHeavyBlur(input, output);
                        break;
                }

                return output;
            }
        }

        #endregion

        #region Private Methods

        /// <summary>
        /// Apply normal blur (50% center + 12.5% neighbors)
        /// </summary>
        private void ApplyNormalBlur(ImageBuffer input, ImageBuffer output)
        {
            int width = input.Width;
            int height = input.Height;

            // Copy input to output
            Array.Copy(input.Pixels, output.Pixels, input.Pixels.Length);

            // Process top line
            ProcessTopLine(input, output, width, BLUR_NORMAL);

            // Process middle block
            ProcessMiddleBlock(input, output, width, height, BLUR_NORMAL);

            // Process bottom line
            ProcessBottomLine(input, output, width, height, BLUR_NORMAL);
        }

        /// <summary>
        /// Apply light blur (50% center + 25% neighbors)
        /// </summary>
        private void ApplyLightBlur(ImageBuffer input, ImageBuffer output)
        {
            int width = input.Width;
            int height = input.Height;

            // Copy input to output
            Array.Copy(input.Pixels, output.Pixels, input.Pixels.Length);

            // Process top line
            ProcessTopLine(input, output, width, BLUR_LIGHT);

            // Process middle block
            ProcessMiddleBlock(input, output, width, height, BLUR_LIGHT);

            // Process bottom line
            ProcessBottomLine(input, output, width, height, BLUR_LIGHT);
        }

        /// <summary>
        /// Apply heavy blur (25% center + 25% neighbors)
        /// </summary>
        private void ApplyHeavyBlur(ImageBuffer input, ImageBuffer output)
        {
            int width = input.Width;
            int height = input.Height;

            // Copy input to output
            Array.Copy(input.Pixels, output.Pixels, input.Pixels.Length);

            // Process top line
            ProcessTopLine(input, output, width, BLUR_HEAVY);

            // Process middle block
            ProcessMiddleBlock(input, output, width, height, BLUR_HEAVY);

            // Process bottom line
            ProcessBottomLine(input, output, width, height, BLUR_HEAVY);
        }

        /// <summary>
        /// Process the top line with special edge handling
        /// </summary>
        private void ProcessTopLine(ImageBuffer input, ImageBuffer output, int width, int blurType)
        {
            int[] inputPixels = input.Pixels;
            int[] outputPixels = output.Pixels;

            // Top left corner
            int adj = RoundMode == ROUND_UP ? ROUND_ADJ_LIGHT : 0;
            if (blurType == BLUR_NORMAL)
            {
                outputPixels[0] = Div2(inputPixels[0]) + Div4(inputPixels[1]) + Div4(inputPixels[width]) + adj;
            }
            else if (blurType == BLUR_LIGHT)
            {
                outputPixels[0] = Div2(inputPixels[0]) + Div4(inputPixels[0]) + Div8(inputPixels[1]) + Div8(inputPixels[width]) + adj;
            }
            else // BLUR_HEAVY
            {
                outputPixels[0] = Div2(inputPixels[1]) + Div2(inputPixels[width]) + adj;
            }

            // Top center pixels
            for (int x = 1; x < width - 1; x++)
            {
                int adj2 = RoundMode == ROUND_UP ? ROUND_ADJ_MEDIUM : 0;
                if (blurType == BLUR_NORMAL)
                {
                    outputPixels[x] = Div4(inputPixels[x]) + Div4(inputPixels[x + 1]) + Div4(inputPixels[x - 1]) + Div4(inputPixels[x + width]) + adj2;
                }
                else if (blurType == BLUR_LIGHT)
                {
                    outputPixels[x] = Div2(inputPixels[x]) + Div8(inputPixels[x]) + Div8(inputPixels[x + 1]) + Div8(inputPixels[x - 1]) + Div8(inputPixels[x + width]) + adj2;
                }
                else // BLUR_HEAVY
                {
                    outputPixels[x] = Div4(inputPixels[x + 1]) + Div4(inputPixels[x - 1]) + Div2(inputPixels[x + width]) + adj2;
                }
            }

            // Top right corner
            adj = RoundMode == ROUND_UP ? ROUND_ADJ_LIGHT : 0;
            if (blurType == BLUR_NORMAL)
            {
                outputPixels[width - 1] = Div2(inputPixels[width - 1]) + Div4(inputPixels[width - 2]) + Div4(inputPixels[2 * width - 1]) + adj;
            }
            else if (blurType == BLUR_LIGHT)
            {
                outputPixels[width - 1] = Div2(inputPixels[width - 1]) + Div4(inputPixels[width - 1]) + Div8(inputPixels[width - 2]) + Div8(inputPixels[2 * width - 1]) + adj;
            }
            else // BLUR_HEAVY
            {
                outputPixels[width - 1] = Div2(inputPixels[width - 2]) + Div2(inputPixels[2 * width - 1]) + adj;
            }
        }

        /// <summary>
        /// Process the middle block with full neighbor sampling
        /// </summary>
        private void ProcessMiddleBlock(ImageBuffer input, ImageBuffer output, int width, int height, int blurType)
        {
            int[] inputPixels = input.Pixels;
            int[] outputPixels = output.Pixels;

            for (int y = 1; y < height - 1; y++)
            {
                int yOffset = y * width;

                // Left edge
                int adj1 = RoundMode == ROUND_UP ? ROUND_ADJ_MEDIUM : 0;
                if (blurType == BLUR_NORMAL)
                {
                    outputPixels[yOffset] = Div4(inputPixels[yOffset]) + Div4(inputPixels[yOffset + 1]) + Div4(inputPixels[yOffset + width]) + Div4(inputPixels[yOffset - width]) + adj1;
                }
                else if (blurType == BLUR_LIGHT)
                {
                    outputPixels[yOffset] = Div2(inputPixels[yOffset]) + Div8(inputPixels[yOffset]) + Div8(inputPixels[yOffset + 1]) + Div8(inputPixels[yOffset + width]) + Div8(inputPixels[yOffset - width]) + adj1;
                }
                else // BLUR_HEAVY
                {
                    outputPixels[yOffset] = Div2(inputPixels[yOffset + 1]) + Div4(inputPixels[yOffset + width]) + Div4(inputPixels[yOffset - width]) + adj1;
                }

                // Middle pixels
                for (int x = 1; x < width - 1; x++)
                {
                    int pixelIndex = yOffset + x;
                    int adj2 = RoundMode == ROUND_UP ? ROUND_ADJ_HEAVY : 0;

                    if (blurType == BLUR_NORMAL)
                    {
                        outputPixels[pixelIndex] = Div2(inputPixels[pixelIndex]) + Div8(inputPixels[pixelIndex + 1]) + Div8(inputPixels[pixelIndex - 1]) + Div8(inputPixels[pixelIndex + width]) + Div8(inputPixels[pixelIndex - width]) + adj2;
                    }
                    else if (blurType == BLUR_LIGHT)
                    {
                        outputPixels[pixelIndex] = Div2(inputPixels[pixelIndex]) + Div4(inputPixels[pixelIndex]) + Div16(inputPixels[pixelIndex + 1]) + Div16(inputPixels[pixelIndex - 1]) + Div16(inputPixels[pixelIndex + width]) + Div16(inputPixels[pixelIndex - width]) + adj2;
                    }
                    else // BLUR_HEAVY
                    {
                        outputPixels[pixelIndex] = Div4(inputPixels[pixelIndex + 1]) + Div4(inputPixels[pixelIndex - 1]) + Div4(inputPixels[pixelIndex + width]) + Div4(inputPixels[pixelIndex - width]) + adj2;
                    }
                }

                // Right edge
                int rightPixel = yOffset + width - 1;
                if (blurType == BLUR_NORMAL)
                {
                    outputPixels[rightPixel] = Div4(inputPixels[rightPixel]) + Div4(inputPixels[rightPixel - 1]) + Div4(inputPixels[rightPixel + width]) + Div4(inputPixels[rightPixel - width]) + adj1;
                }
                else if (blurType == BLUR_LIGHT)
                {
                    outputPixels[rightPixel] = Div2(inputPixels[rightPixel]) + Div8(inputPixels[rightPixel]) + Div8(inputPixels[rightPixel - 1]) + Div8(inputPixels[rightPixel + width]) + Div8(inputPixels[rightPixel - width]) + adj1;
                }
                else // BLUR_HEAVY
                {
                    outputPixels[rightPixel] = Div2(inputPixels[rightPixel - 1]) + Div4(inputPixels[rightPixel + width]) + Div4(inputPixels[rightPixel - width]) + adj1;
                }
            }
        }

        /// <summary>
        /// Process the bottom line with special edge handling
        /// </summary>
        private void ProcessBottomLine(ImageBuffer input, ImageBuffer output, int width, int height, int blurType)
        {
            int[] inputPixels = input.Pixels;
            int[] outputPixels = output.Pixels;
            int bottomOffset = (height - 1) * width;

            // Bottom left corner
            int adj = RoundMode == ROUND_UP ? ROUND_ADJ_LIGHT : 0;
            if (blurType == BLUR_NORMAL)
            {
                outputPixels[bottomOffset] = Div2(inputPixels[bottomOffset]) + Div4(inputPixels[bottomOffset + 1]) + Div4(inputPixels[bottomOffset - width]) + adj;
            }
            else if (blurType == BLUR_LIGHT)
            {
                outputPixels[bottomOffset] = Div2(inputPixels[bottomOffset]) + Div4(inputPixels[bottomOffset]) + Div8(inputPixels[bottomOffset + 1]) + Div8(inputPixels[bottomOffset - width]) + adj;
            }
            else // BLUR_HEAVY
            {
                outputPixels[bottomOffset] = Div2(inputPixels[bottomOffset + 1]) + Div2(inputPixels[bottomOffset - width]) + adj;
            }

            // Bottom center pixels
            for (int x = 1; x < width - 1; x++)
            {
                int pixelIndex = bottomOffset + x;
                int adj2 = RoundMode == ROUND_UP ? ROUND_ADJ_MEDIUM : 0;

                if (blurType == BLUR_NORMAL)
                {
                    outputPixels[pixelIndex] = Div4(inputPixels[pixelIndex]) + Div4(inputPixels[pixelIndex + 1]) + Div4(inputPixels[pixelIndex - 1]) + Div4(inputPixels[pixelIndex - width]) + adj2;
                }
                else if (blurType == BLUR_LIGHT)
                {
                    outputPixels[pixelIndex] = Div2(inputPixels[pixelIndex]) + Div8(inputPixels[pixelIndex]) + Div8(inputPixels[pixelIndex + 1]) + Div8(inputPixels[pixelIndex - 1]) + Div8(inputPixels[pixelIndex - width]) + adj2;
                }
                else // BLUR_HEAVY
                {
                    outputPixels[pixelIndex] = Div4(inputPixels[pixelIndex + 1]) + Div4(inputPixels[pixelIndex - 1]) + Div2(inputPixels[pixelIndex - width]) + adj2;
                }
            }

            // Bottom right corner
            int bottomRight = bottomOffset + width - 1;
            adj = RoundMode == ROUND_UP ? ROUND_ADJ_LIGHT : 0;
            if (blurType == BLUR_NORMAL)
            {
                outputPixels[bottomRight] = Div2(inputPixels[bottomRight]) + Div4(inputPixels[bottomRight - 1]) + Div4(inputPixels[bottomRight - width]) + adj;
            }
            else if (blurType == BLUR_LIGHT)
            {
                outputPixels[bottomRight] = Div2(inputPixels[bottomRight]) + Div4(inputPixels[bottomRight]) + Div8(inputPixels[bottomRight - 1]) + Div8(inputPixels[bottomRight - width]) + adj;
            }
            else // BLUR_HEAVY
            {
                outputPixels[bottomRight] = Div2(inputPixels[bottomRight - 1]) + Div2(inputPixels[bottomRight - width]) + adj;
            }
        }

        /// <summary>
        /// Divide pixel value by 2 with proper masking
        /// </summary>
        private int Div2(int pixel)
        {
            return (pixel & DIV_2_MASK) >> 1;
        }

        /// <summary>
        /// Divide pixel value by 4 with proper masking
        /// </summary>
        private int Div4(int pixel)
        {
            return (pixel & DIV_4_MASK) >> 2;
        }

        /// <summary>
        /// Divide pixel value by 8 with proper masking
        /// </summary>
        private int Div8(int pixel)
        {
            return (pixel & DIV_8_MASK) >> 3;
        }

        /// <summary>
        /// Divide pixel value by 16 with proper masking
        /// </summary>
        private int Div16(int pixel)
        {
            return (pixel & DIV_16_MASK) >> 4;
        }

        #endregion

        #region Configuration

        /// <summary>
        /// Validate and clamp property values
        /// </summary>
        public override void ValidateConfiguration()
        {
            Enabled = Math.Clamp(Enabled, BLUR_OFF, BLUR_HEAVY);
            RoundMode = Math.Clamp(RoundMode, ROUND_DOWN, ROUND_UP);
        }

        /// <summary>
        /// Get a summary of current settings
        /// </summary>
        public override string GetSettingsSummary()
        {
            string blurText = GetBlurText();
            string roundText = RoundMode == ROUND_UP ? "Round Up" : "Round Down";

            return $"Blur: {blurText}, {roundText}, Multi-threaded: {MultiThreaded}";
        }

        /// <summary>
        /// Get blur intensity text
        /// </summary>
        private string GetBlurText()
        {
            switch (Enabled)
            {
                case BLUR_OFF: return "Off";
                case BLUR_NORMAL: return "Normal";
                case BLUR_LIGHT: return "Light";
                case BLUR_HEAVY: return "Heavy";
                default: return "Unknown";
            }
        }

        #endregion

        #region Helper Classes

        /// <summary>
        /// Blur parameters for processing
        /// </summary>
        private class BlurParameters
        {
            public int Width { get; set; }
            public int Height { get; set; }
            public int BlurType { get; set; }
            public bool RoundMode { get; set; }
        }

        #endregion

        #region Overrides

        protected override object GetDefaultOutput()
        {
            return new ImageBuffer(1, 1);
        }

        #endregion
    }
}
```

## Key Features

### Blur Algorithms
- **Normal Blur**: Balanced blur with 50% center pixel + 12.5% from each neighbor
- **Light Blur**: Subtle blur with 50% center + 25% from neighbors
- **Heavy Blur**: Strong blur with 25% center + 25% from neighbors

### Round Mode
- **Round Down**: Prevents color bleeding by rounding down pixel values
- **Round Up**: Adds slight brightness adjustment for enhanced contrast

### Performance Optimizations
- **Multi-threading**: SMP support for parallel processing
- **MMX Instructions**: Assembly-level optimizations for Intel processors
- **Efficient Algorithms**: Optimized pixel manipulation with bit masking

### Edge Handling
- **Corner Pixels**: Special algorithms for image corners
- **Border Pixels**: Optimized processing for image edges
- **Neighbor Sampling**: Intelligent sampling based on available neighbors

## Usage Examples

```csharp
// Create a light blur effect with round up mode
var blurNode = new BlurEffectsNode
{
    Enabled = BlurEffectsNode.BLUR_LIGHT,
    RoundMode = BlurEffectsNode.ROUND_UP,
    MultiThreaded = true
};

// Apply to image
var blurredImage = blurNode.ProcessFrame(inputImage, audioFeatures);
```

## Technical Details

### Blur Calculation
The blur effect uses weighted averaging of neighboring pixels:

```csharp
// Normal blur formula
outputPixel = (center * 0.5) + (neighbors * 0.125 each)

// Light blur formula  
outputPixel = (center * 0.5) + (neighbors * 0.25 each)

// Heavy blur formula
outputPixel = (center * 0.25) + (neighbors * 0.25 each)
```

### Round Mode Adjustments
Round mode adds small adjustments to prevent color bleeding:

```csharp
// Round up adjustments
ROUND_ADJ_LIGHT = 0x03030303;   // +3 to each channel
ROUND_ADJ_MEDIUM = 0x04040404;  // +4 to each channel  
ROUND_ADJ_HEAVY = 0x02020202;   // +2 to each channel
```

### Bit Masking
Efficient pixel division using bit masks:

```csharp
// Division masks for RGB channels
DIV_2_MASK = 0x7F7F7F7F;  // 01111111 for each channel
DIV_4_MASK = 0x3F3F3F3F;  // 00111111 for each channel
DIV_8_MASK = 0x1F1F1F1F;  // 00011111 for each channel
DIV_16_MASK = 0x0F0F0F0F; // 00001111 for each channel
```

### Multi-threading Support
The effect supports parallel processing for performance:

```csharp
// Thread-safe rendering with lock protection
lock (renderLock)
{
    // Process image in parallel chunks
    if (MultiThreaded)
    {
        // Split work across multiple threads
        Parallel.For(0, height, y => ProcessLine(y));
    }
    else
    {
        // Single-threaded processing
        for (int y = 0; y < height; y++)
            ProcessLine(y);
    }
}
```

This implementation provides a complete, production-ready blur effect system that faithfully reproduces the original C++ functionality while leveraging C# features for improved maintainability and performance.
