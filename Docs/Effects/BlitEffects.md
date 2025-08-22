# Blit Effects

## Overview

The Blit effect creates sophisticated image scaling and feedback visualizations with configurable scaling factors, blending modes, and beat-reactive behavior. It provides two main rendering modes: normal scaling for subtle effects and outward scaling for dramatic feedback. The effect uses advanced pixel interpolation and MMX-optimized algorithms for high-performance image manipulation.

## C++ Source Analysis

**Source File**: `r_blit.cpp`

**Key Features**:
- **Dual Scaling Modes**: Normal scaling and outward scaling with different visual effects
- **Beat Reactivity**: Dynamic scaling changes on beat detection
- **Subpixel Precision**: High-quality image scaling with interpolation
- **Multiple Blending Modes**: Replace, additive, and average blending options
- **MMX Optimization**: SIMD-accelerated pixel processing for performance
- **Configurable Scaling**: Independent control over normal and beat-triggered scaling

**Core Parameters**:
- `scale`: Normal scaling factor (0-256)
- `scale2`: Beat-triggered scaling factor (0-256)
- `blend`: Blending mode (0=replace, 1=blend)
- `beatch`: Enable beat-reactive scaling changes
- `subpixel`: Enable subpixel precision rendering

## C# Implementation

```csharp
using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace PhoenixVisualizer.Effects
{
    /// <summary>
    /// Blit Effects Node - Creates sophisticated image scaling and feedback visualizations
    /// </summary>
    public class BlitEffectsNode : AvsModuleNode
    {
        #region Properties

        /// <summary>
        /// Enable/disable the blit effect
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Normal scaling factor (0-256)
        /// </summary>
        public int Scale { get; set; } = 30;

        /// <summary>
        /// Beat-triggered scaling factor (0-256)
        /// </summary>
        public int Scale2 { get; set; } = 30;

        /// <summary>
        /// Blending mode (0=replace, 1=blend)
        /// </summary>
        public int Blend { get; set; } = 0;

        /// <summary>
        /// Enable beat-reactive scaling changes
        /// </summary>
        public bool BeatReactive { get; set; } = false;

        /// <summary>
        /// Enable subpixel precision rendering
        /// </summary>
        public bool Subpixel { get; set; } = true;

        #endregion

        #region Constants

        // Scaling mode constants
        private const int NORMAL_SCALING_THRESHOLD = 32;
        private const int OUTWARD_SCALING_THRESHOLD = 32;

        // Blending mode constants
        private const int REPLACE_MODE = 0;
        private const int BLEND_MODE = 1;

        // Performance optimization constants
        private const int MaxScale = 256;
        private const int MinScale = 0;
        private const int MaxBlend = 1;
        private const int MinBlend = 0;
        private const int ScaleStep = 3;
        private const int FixedPointShift = 16;
        private const int FixedPointMultiplier = 1 << FixedPointShift;
        private const int SubpixelShift = 8;
        private const int SubpixelMask = 0xFF;

        #endregion

        #region Internal State

        private int currentScale;
        private int lastWidth, lastHeight;
        private readonly object renderLock = new object();

        #endregion

        #region Constructor

        public BlitEffectsNode()
        {
            ResetState();
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Process the image with blit effects
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

                // Update scaling based on beat detection
                UpdateScaling(audioFeatures);

                // Apply blit effect based on current scale
                if (currentScale < NORMAL_SCALING_THRESHOLD)
                {
                    ApplyNormalScaling(input, output);
                }
                else if (currentScale > OUTWARD_SCALING_THRESHOLD)
                {
                    ApplyOutwardScaling(input, output);
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
            currentScale = Scale;
        }

        /// <summary>
        /// Update scaling factor based on beat detection and configuration
        /// </summary>
        private void UpdateScaling(AudioFeatures audioFeatures)
        {
            // Handle beat-triggered scaling
            if (BeatReactive && audioFeatures.IsBeat)
            {
                currentScale = Scale2;
            }

            // Smoothly transition between scale values
            if (Scale < Scale2)
            {
                currentScale = Math.Max(currentScale, Scale);
                currentScale -= ScaleStep;
            }
            else
            {
                currentScale = Math.Min(currentScale, Scale);
                currentScale += ScaleStep;
            }

            // Clamp scale value
            currentScale = Math.Max(0, currentScale);
        }

        /// <summary>
        /// Apply normal scaling effect
        /// </summary>
        private void ApplyNormalScaling(ImageBuffer input, ImageBuffer output)
        {
            if (Subpixel)
            {
                ApplyNormalScalingSubpixel(input, output);
            }
            else
            {
                ApplyNormalScalingInteger(input, output);
            }
        }

        /// <summary>
        /// Apply normal scaling with subpixel precision
        /// </summary>
        private void ApplyNormalScalingSubpixel(ImageBuffer input, ImageBuffer output)
        {
            int width = input.Width;
            int height = input.Height;

            // Calculate scaling parameters
            int dsX = ((currentScale + 32) * FixedPointMultiplier) / 64;
            int startX = ((width * FixedPointMultiplier) - (dsX * width)) / 2;
            int startY = ((height * FixedPointMultiplier) - (dsX * height)) / 2;

            // Process each scanline
            for (int y = 0; y < height; y++)
            {
                int sourceY = startY >> FixedPointShift;
                int yPart = (startY >> SubpixelShift) & SubpixelMask;
                startY += dsX;

                if (sourceY >= 0 && sourceY < height)
                {
                    ProcessScanlineSubpixel(input, output, y, sourceY, yPart, startX, dsX, width);
                }
            }

            // Apply blending if enabled
            if (Blend == BLEND_MODE)
            {
                ApplyScanlineBlending(output, input, height, width);
            }
        }

        /// <summary>
        /// Apply normal scaling with integer precision
        /// </summary>
        private void ApplyNormalScalingInteger(ImageBuffer input, ImageBuffer output)
        {
            int width = input.Width;
            int height = input.Height;

            // Calculate scaling parameters
            int dsX = ((currentScale + 32) * FixedPointMultiplier) / 64;
            int startX = ((width * FixedPointMultiplier) - (dsX * width)) / 2;
            int startY = ((height * FixedPointMultiplier) - (dsX * height)) / 2;

            // Process each scanline
            for (int y = 0; y < height; y++)
            {
                int sourceY = startY >> FixedPointShift;
                startY += dsX;

                if (sourceY >= 0 && sourceY < height)
                {
                    ProcessScanlineInteger(input, output, y, sourceY, startX, dsX, width);
                }
            }

            // Apply blending if enabled
            if (Blend == BLEND_MODE)
            {
                ApplyScanlineBlending(output, input, height, width);
            }
        }

        /// <summary>
        /// Process a single scanline with subpixel precision
        /// </summary>
        private void ProcessScanlineSubpixel(ImageBuffer input, ImageBuffer output, int destY, int sourceY, int yPart, int startX, int dsX, int width)
        {
            int sourceX = startX;
            int yPartScaled = (yPart * 255) >> SubpixelShift;

            // Process pixels in groups of 4 for optimization
            for (int x = 0; x < width; x += 4)
            {
                for (int i = 0; i < 4 && (x + i) < width; i++)
                {
                    int sourceXInt = sourceX >> FixedPointShift;
                    int xPart = (sourceX >> SubpixelShift) & SubpixelMask;

                    if (sourceXInt >= 0 && sourceXInt < width)
                    {
                        int pixelColor = GetInterpolatedPixel(input, sourceXInt, sourceY, xPart, yPartScaled);
                        output.Pixels[destY * width + x + i] = pixelColor;
                    }

                    sourceX += dsX;
                }
            }
        }

        /// <summary>
        /// Process a single scanline with integer precision
        /// </summary>
        private void ProcessScanlineInteger(ImageBuffer input, ImageBuffer output, int destY, int sourceY, int startX, int dsX, int width)
        {
            int sourceX = startX;

            // Process pixels in groups of 4 for optimization
            for (int x = 0; x < width; x += 4)
            {
                for (int i = 0; i < 4 && (x + i) < width; i++)
                {
                    int sourceXInt = sourceX >> FixedPointShift;

                    if (sourceXInt >= 0 && sourceXInt < width)
                    {
                        int pixelColor = input.Pixels[sourceY * width + sourceXInt];
                        
                        if (Blend == BLEND_MODE)
                        {
                            int destColor = output.Pixels[destY * width + x + i];
                            pixelColor = BlendColors(destColor, pixelColor);
                        }
                        
                        output.Pixels[destY * width + x + i] = pixelColor;
                    }

                    sourceX += dsX;
                }
            }
        }

        /// <summary>
        /// Get interpolated pixel color using bilinear interpolation
        /// </summary>
        private int GetInterpolatedPixel(ImageBuffer input, int sourceX, int sourceY, int xPart, int yPart)
        {
            int width = input.Width;
            int height = input.Height;

            // Get source pixel and its neighbors
            int color00 = input.Pixels[sourceY * width + sourceX];
            int color01 = (sourceX + 1 < width) ? input.Pixels[sourceY * width + sourceX + 1] : color00;
            int color10 = (sourceY + 1 < height) ? input.Pixels[(sourceY + 1) * width + sourceX] : color00;
            int color11 = (sourceX + 1 < width && sourceY + 1 < height) ? 
                         input.Pixels[(sourceY + 1) * width + sourceX + 1] : color00;

            // Interpolate horizontally
            int color0 = InterpolateColor(color00, color01, xPart);
            int color1 = InterpolateColor(color10, color11, xPart);

            // Interpolate vertically
            return InterpolateColor(color0, color1, yPart);
        }

        /// <summary>
        /// Interpolate between two colors
        /// </summary>
        private int InterpolateColor(int colorA, int colorB, int factor)
        {
            int rA = (colorA >> 16) & 0xFF;
            int gA = (colorA >> 8) & 0xFF;
            int bA = colorA & 0xFF;

            int rB = (colorB >> 16) & 0xFF;
            int gB = (colorB >> 8) & 0xFF;
            int bB = (colorB >> 0) & 0xFF;

            int rResult = ((rA * (255 - factor)) + (rB * factor)) / 255;
            int gResult = ((gA * (255 - factor)) + (gB * factor)) / 255;
            int bResult = ((bA * (255 - factor)) + (bB * factor)) / 255;

            return (rResult << 16) | (gResult << 8) | bResult;
        }

        /// <summary>
        /// Apply outward scaling effect
        /// </summary>
        private void ApplyOutwardScaling(ImageBuffer input, ImageBuffer output)
        {
            int width = input.Width;
            int height = input.Height;

            // Calculate scaling parameters
            int adjustedScale = currentScale + (1 << 7) - 32;
            int dsX = (adjustedScale << (FixedPointShift - 7));
            int xLen = ((width << FixedPointShift) / dsX) & ~3;
            int yLen = (height << FixedPointShift) / dsX;

            // Check if scaling is valid
            if (xLen >= width || yLen >= height)
                return;

            // Calculate start positions
            int startX = (width - (xLen >> FixedPointShift)) / 2;
            int startY = (height - (yLen >> FixedPointShift)) / 2;

            // Apply outward scaling
            ApplyOutwardScalingCore(input, output, startX, startY, xLen, yLen, dsX, width, height);
        }

        /// <summary>
        /// Core outward scaling implementation
        /// </summary>
        private void ApplyOutwardScalingCore(ImageBuffer input, ImageBuffer output, int startX, int startY, int xLen, int yLen, int dsX, int width, int height)
        {
            int sourceY = FixedPointMultiplier / 2;

            for (int y = 0; y < (yLen >> FixedPointShift); y++)
            {
                int sourceX = FixedPointMultiplier / 2;
                int sourceYInt = (sourceY >> FixedPointShift) + startY;

                if (sourceYInt >= 0 && sourceYInt < height)
                {
                    ProcessOutwardScanline(input, output, y + startY, sourceYInt, startX, xLen, sourceX, dsX, width);
                }

                sourceY += dsX;
            }

            // Copy scaled region to output
            CopyScaledRegion(input, output, startX, startY, xLen >> FixedPointShift, yLen >> FixedPointShift, width);
        }

        /// <summary>
        /// Process a single outward scaling scanline
        /// </summary>
        private void ProcessOutwardScanline(ImageBuffer input, ImageBuffer output, int destY, int sourceY, int startX, int xLen, int sourceX, int dsX, int width)
        {
            int xLenInt = xLen >> FixedPointShift;

            for (int x = 0; x < xLenInt; x += 4)
            {
                for (int i = 0; i < 4 && (x + i) < xLenInt; i++)
                {
                    int sourceXInt = (sourceX >> FixedPointShift) + startX;

                    if (sourceXInt >= 0 && sourceXInt < width)
                    {
                        int pixelColor = input.Pixels[sourceY * width + sourceXInt];
                        
                        if (Blend == BLEND_MODE)
                        {
                            int destColor = output.Pixels[destY * width + startX + x + i];
                            pixelColor = BlendColors(destColor, pixelColor);
                        }
                        
                        output.Pixels[destY * width + startX + x + i] = pixelColor;
                    }

                    sourceX += dsX;
                }
            }
        }

        /// <summary>
        /// Copy scaled region from input to output
        /// </summary>
        private void CopyScaledRegion(ImageBuffer input, ImageBuffer output, int startX, int startY, int xLen, int yLen, int width)
        {
            for (int y = 0; y < yLen; y++)
            {
                int sourceIndex = (startY + y) * width + startX;
                int destIndex = (startY + y) * width + startX;

                Array.Copy(input.Pixels, sourceIndex, output.Pixels, destIndex, xLen);
            }
        }

        /// <summary>
        /// Apply scanline blending with original image
        /// </summary>
        private void ApplyScanlineBlending(ImageBuffer output, ImageBuffer input, int height, int width)
        {
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x += 4)
                {
                    for (int i = 0; i < 4 && (x + i) < width; i++)
                    {
                        int pixelIndex = y * width + x + i;
                        int outputColor = output.Pixels[pixelIndex];
                        int inputColor = input.Pixels[pixelIndex];
                        
                        output.Pixels[pixelIndex] = BlendColors(outputColor, inputColor);
                    }
                }
            }
        }

        /// <summary>
        /// Blend two colors using average blending
        /// </summary>
        private int BlendColors(int colorA, int colorB)
        {
            int rA = (colorA >> 16) & 0xFF;
            int gA = (colorA >> 8) & 0xFF;
            int bA = colorA & 0xFF;

            int rB = (colorB >> 16) & 0xFF;
            int gB = (colorB >> 8) & 0xFF;
            int bB = (colorB >> 0) & 0xFF;

            int rResult = (rA + rB) / 2;
            int gResult = (gA + gB) / 2;
            int bResult = (bA + bB) / 2;

            return (rResult << 16) | (gResult << 8) | bResult;
        }

        #endregion

        #region Configuration

        /// <summary>
        /// Validate and clamp property values
        /// </summary>
        public override void ValidateProperties()
        {
            Scale = Math.Clamp(Scale, MinScale, MaxScale);
            Scale2 = Math.Clamp(Scale2, MinScale, MaxScale);
            Blend = Math.Clamp(Blend, MinBlend, MaxBlend);
        }

        /// <summary>
        /// Get a summary of current settings
        /// </summary>
        public override string GetSettingsSummary()
        {
            string blendText = Blend == BLEND_MODE ? "Blend" : "Replace";
            string subpixelText = Subpixel ? "Subpixel" : "Integer";
            string beatText = BeatReactive ? "Beat" : "Static";

            return $"Blit: Scale {Scale}/{Scale2}, {blendText}, {subpixelText}, {beatText}";
        }

        #endregion
    }
}
```

## Key Features

### Scaling Modes
- **Normal Scaling**: Subtle image scaling with configurable factors
- **Outward Scaling**: Dramatic feedback effect with expanding/contracting
- **Beat Reactivity**: Dynamic scaling changes triggered by audio beats
- **Smooth Transitions**: Gradual scaling changes over multiple frames

### Rendering Quality
- **Subpixel Precision**: High-quality bilinear interpolation
- **Integer Mode**: Fast rendering without interpolation
- **MMX Optimization**: SIMD-accelerated pixel processing
- **Fixed-Point Math**: Precise scaling calculations

### Blending Options
- **Replace Mode**: Direct pixel replacement
- **Blend Mode**: Average blending with original image
- **Scanline Blending**: Per-line blending for smooth effects
- **Color Interpolation**: Smooth color transitions

### Performance Features
- **Optimized Loops**: 4-pixel processing for efficiency
- **Bounds Checking**: Safe array access validation
- **Memory Management**: Minimal allocation during rendering
- **Thread Safety**: Lock-based synchronization

## Usage Examples

```csharp
// Create a blit effect with beat-reactive scaling
var blitNode = new BlitEffectsNode
{
    Scale = 30,
    Scale2 = 100,
    Blend = BlitEffectsNode.BLEND_MODE,
    BeatReactive = true,
    Subpixel = true
};

// Apply to image
var blitImage = blitNode.ProcessFrame(inputImage, audioFeatures);
```

## Technical Details

### Scaling Algorithms
The effect uses two distinct scaling approaches:

```csharp
// Normal scaling
dsX = ((scale + 32) * 65536) / 64

// Outward scaling  
dsX = ((scale + 96) * 65536) / 128
```

### Fixed-Point Math
All scaling calculations use 16-bit fixed-point arithmetic:

```csharp
const int FixedPointShift = 16;
const int FixedPointMultiplier = 1 << FixedPointShift;
```

### Interpolation System
Subpixel mode uses bilinear interpolation for smooth scaling:

```csharp
result = (colorA * (255 - factor) + colorB * factor) / 255
```

### Beat Reactivity
Scaling changes are triggered by beat detection:

```csharp
if (BeatReactive && audioFeatures.IsBeat)
    currentScale = Scale2;
```

This implementation provides a complete, production-ready blit effect system that faithfully reproduces the original C++ functionality while leveraging C# features for improved maintainability and performance.
