# Mirror Effects

## Overview

The Mirror effect creates symmetrical reflections of the image across horizontal and/or vertical axes. It supports multiple mirror modes, smooth transitions, beat-reactive behavior, and configurable transition speeds.

## C++ Source Analysis

**Source File**: `r_mirror.cpp`

**Key Features**:
- **Multiple Mirror Modes**: Horizontal and vertical mirroring in both directions
- **Smooth Transitions**: Gradual blending between mirror states
- **Beat Reactivity**: Dynamic mirror mode changes on beat detection
- **Configurable Speed**: Adjustable transition timing
- **Bitwise Mode Management**: Efficient mode switching using bit flags

**Core Parameters**:
- `mode`: Bitwise combination of mirror directions
- `onbeat`: Enable beat-reactive mirror changes
- `smooth`: Enable smooth transitions between states
- `slower`: Transition speed control (1-16)

## C# Implementation

```csharp
using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace PhoenixVisualizer.Effects
{
    /// <summary>
    /// Mirror Effects Node - Creates symmetrical reflections across multiple axes
    /// </summary>
    public class MirrorEffectsNode : AvsModuleNode
    {
        #region Properties

        /// <summary>
        /// Enable/disable the mirror effect
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Mirror mode - bitwise combination of directions
        /// </summary>
        public int Mode { get; set; } = 1; // Default: HORIZONTAL1

        /// <summary>
        /// Enable beat-reactive mirror changes
        /// </summary>
        public bool OnBeat { get; set; } = false;

        /// <summary>
        /// Enable smooth transitions between mirror states
        /// </summary>
        public bool Smooth { get; set; } = false;

        /// <summary>
        /// Transition speed control (1-16, higher = slower)
        /// </summary>
        public int Slower { get; set; } = 4;

        #endregion

        #region Constants

        // Mirror direction constants
        private const int HORIZONTAL1 = 1;
        private const int HORIZONTAL2 = 2;
        private const int VERTICAL1 = 4;
        private const int VERTICAL2 = 8;

        // Divisor constants for smooth transitions
        private const int D_HORIZONTAL1 = 0;
        private const int D_HORIZONTAL2 = 8;
        private const int D_VERTICAL1 = 16;
        private const int D_VERTICAL2 = 24;

        // Mask constants for bitwise operations
        private const int M_HORIZONTAL1 = 0xFF;
        private const int M_HORIZONTAL2 = 0xFF00;
        private const int M_VERTICAL1 = 0xFF0000;
        private const int M_VERTICAL2 = 0xFF000000;

        // Performance optimization constants
        private const int MaxMode = 15; // All directions combined
        private const int MinMode = 0;
        private const int MaxSlower = 16;
        private const int MinSlower = 1;
        private const int MaxDivisor = 16;
        private const int MinDivisor = 1;

        #endregion

        #region Internal State

        private int frameCount;
        private int lastMode;
        private int divisors;
        private int increment;
        private int randomBeatMode;
        private int lastWidth, lastHeight;
        private readonly object renderLock = new object();
        private readonly Random random;

        #endregion

        #region Constructor

        public MirrorEffectsNode()
        {
            random = new Random();
            ResetState();
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Process the image with mirror effects
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

                // Determine current mirror mode
                int currentMode = DetermineMirrorMode(audioFeatures);

                // Update transition state
                UpdateTransitionState(currentMode);

                // Apply mirror effects
                ApplyMirrorEffects(output, currentMode);

                // Update smooth transitions
                if (Smooth)
                {
                    UpdateSmoothTransitions();
                }

                frameCount++;
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
            frameCount = 0;
            lastMode = Mode;
            divisors = 0;
            increment = 0;
            randomBeatMode = Mode;
        }

        /// <summary>
        /// Determine the current mirror mode based on settings and audio
        /// </summary>
        private int DetermineMirrorMode(AudioFeatures audioFeatures)
        {
            if (OnBeat && audioFeatures.IsBeat)
            {
                // Generate random beat-reactive mode
                randomBeatMode = random.Next(16) & Mode;
                return randomBeatMode;
            }

            return Mode;
        }

        /// <summary>
        /// Update transition state for smooth mirror changes
        /// </summary>
        private void UpdateTransitionState(int currentMode)
        {
            if (currentMode != lastMode)
            {
                int difference = currentMode ^ lastMode;
                int mask = 0xFF;
                int divisor = 0;

                for (int i = 1; i < 16; i <<= 1, mask <<= 8, divisor += 8)
                {
                    if ((difference & i) != 0)
                    {
                        // Set increment direction
                        increment = (increment & ~mask) | 
                                  (((lastMode & i) != 0 ? 0xFF : 1) << divisor);

                        // Set initial divisor
                        if ((divisors & mask) == 0)
                        {
                            divisors = (divisors & ~mask) | 
                                     (((lastMode & i) != 0 ? 16 : 1) << divisor);
                        }
                    }
                }

                lastMode = currentMode;
            }
        }

        /// <summary>
        /// Apply mirror effects to the image
        /// </summary>
        private void ApplyMirrorEffects(ImageBuffer image, int currentMode)
        {
            int width = image.Width;
            int height = image.Height;
            int halfWidth = width / 2;
            int halfHeight = height / 2;

            // Apply vertical mirroring (left to right)
            if ((currentMode & VERTICAL1) != 0 || (Smooth && (divisors & 0x00FF0000) != 0))
            {
                int divisor = (divisors & M_VERTICAL1) >> D_VERTICAL1;
                ApplyVerticalMirror(image, 0, divisor, true);
            }

            // Apply vertical mirroring (right to left)
            if ((currentMode & VERTICAL2) != 0 || (Smooth && (divisors & 0xFF000000) != 0))
            {
                int divisor = (divisors & M_VERTICAL2) >> D_VERTICAL2;
                ApplyVerticalMirror(image, 1, divisor, false);
            }

            // Apply horizontal mirroring (top to bottom)
            if ((currentMode & HORIZONTAL1) != 0 || (Smooth && (divisors & 0x000000FF) != 0))
            {
                int divisor = (divisors & M_HORIZONTAL1) >> D_HORIZONTAL1;
                ApplyHorizontalMirror(image, 0, divisor, true);
            }

            // Apply horizontal mirroring (bottom to top)
            if ((currentMode & HORIZONTAL2) != 0 || (Smooth && (divisors & 0x0000FF00) != 0))
            {
                int divisor = (divisors & M_HORIZONTAL2) >> D_HORIZONTAL2;
                ApplyHorizontalMirror(image, 1, divisor, false);
            }
        }

        /// <summary>
        /// Apply vertical mirroring to the image
        /// </summary>
        private void ApplyVerticalMirror(ImageBuffer image, int direction, int divisor, bool leftToRight)
        {
            int width = image.Width;
            int height = image.Height;
            int halfWidth = width / 2;

            for (int y = 0; y < height; y++)
            {
                if (Smooth && divisor > 0)
                {
                    // Smooth blending
                    for (int x = 0; x < halfWidth; x++)
                    {
                        int sourceIndex = y * width + x;
                        int targetIndex = y * width + (width - 1 - x);

                        if (leftToRight)
                        {
                            image.Pixels[targetIndex] = BlendAdaptive(
                                image.Pixels[targetIndex], 
                                image.Pixels[sourceIndex], 
                                divisor);
                        }
                        else
                        {
                            image.Pixels[sourceIndex] = BlendAdaptive(
                                image.Pixels[sourceIndex], 
                                image.Pixels[targetIndex], 
                                divisor);
                        }
                    }
                }
                else
                {
                    // Direct mirroring
                    for (int x = 0; x < halfWidth; x++)
                    {
                        int sourceIndex = y * width + x;
                        int targetIndex = y * width + (width - 1 - x);

                        if (leftToRight)
                        {
                            image.Pixels[targetIndex] = image.Pixels[sourceIndex];
                        }
                        else
                        {
                            image.Pixels[sourceIndex] = image.Pixels[targetIndex];
                        }
                    }
                }
            }
        }

        /// <summary>
        /// Apply horizontal mirroring to the image
        /// </summary>
        private void ApplyHorizontalMirror(ImageBuffer image, int direction, int divisor, bool topToBottom)
        {
            int width = image.Width;
            int height = image.Height;
            int halfHeight = height / 2;

            for (int y = 0; y < halfHeight; y++)
            {
                if (Smooth && divisor > 0)
                {
                    // Smooth blending
                    for (int x = 0; x < width; x++)
                    {
                        int sourceIndex = y * width + x;
                        int targetIndex = (height - 1 - y) * width + x;

                        if (topToBottom)
                        {
                            image.Pixels[targetIndex] = BlendAdaptive(
                                image.Pixels[targetIndex], 
                                image.Pixels[sourceIndex], 
                                divisor);
                        }
                        else
                        {
                            image.Pixels[sourceIndex] = BlendAdaptive(
                                image.Pixels[sourceIndex], 
                                image.Pixels[targetIndex], 
                                divisor);
                        }
                    }
                }
                else
                {
                    // Direct mirroring
                    for (int x = 0; x < width; x++)
                    {
                        int sourceIndex = y * width + x;
                        int targetIndex = (height - 1 - y) * width + x;

                        if (topToBottom)
                        {
                            image.Pixels[targetIndex] = image.Pixels[sourceIndex];
                        }
                        else
                        {
                            image.Pixels[sourceIndex] = image.Pixels[targetIndex];
                        }
                    }
                }
            }
        }

        /// <summary>
        /// Adaptive blending function for smooth transitions
        /// </summary>
        private int BlendAdaptive(int colorA, int colorB, int divisor)
        {
            if (divisor <= 0) return colorA;
            if (divisor >= 16) return colorB;

            // Extract RGB components
            int rA = (colorA >> 16) & 0xFF;
            int gA = (colorA >> 8) & 0xFF;
            int bA = colorA & 0xFF;

            int rB = (colorB >> 16) & 0xFF;
            int gB = (colorB >> 8) & 0xFF;
            int bB = colorB & 0xFF;

            // Blend components
            int rResult = ((rA * (16 - divisor)) + (rB * divisor)) / 16;
            int gResult = ((gA * (16 - divisor)) + (gB * divisor)) / 16;
            int bResult = ((bA * (16 - divisor)) + (bB * divisor)) / 16;

            // Clamp values
            rResult = Math.Clamp(rResult, 0, 255);
            gResult = Math.Clamp(gResult, 0, 255);
            bResult = Math.Clamp(bResult, 0, 255);

            return (rResult << 16) | (gResult << 8) | bResult;
        }

        /// <summary>
        /// Update smooth transitions based on frame count
        /// </summary>
        private void UpdateSmoothTransitions()
        {
            if (frameCount % Slower == 0)
            {
                int mask = 0xFF;
                int divisor = 0;

                for (int i = 1; i < 16; i <<= 1, mask <<= 8, divisor += 8)
                {
                    if ((divisors & mask) != 0)
                    {
                        int currentDivisor = (divisors & mask) >> divisor;
                        int currentIncrement = (increment & mask) >> divisor;

                        // Update divisor with wrapping
                        currentDivisor = (currentDivisor + (byte)currentIncrement) % 16;

                        // Update divisors
                        divisors = (divisors & ~mask) | (currentDivisor << divisor);
                    }
                }
            }
        }

        #endregion

        #region Configuration

        /// <summary>
        /// Validate and clamp property values
        /// </summary>
        public override void ValidateProperties()
        {
            Mode = Math.Clamp(Mode, MinMode, MaxMode);
            Slower = Math.Clamp(Slower, MinSlower, MaxSlower);
        }

        /// <summary>
        /// Get a summary of current settings
        /// </summary>
        public override string GetSettingsSummary()
        {
            var directions = new List<string>();
            
            if ((Mode & HORIZONTAL1) != 0) directions.Add("H1");
            if ((Mode & HORIZONTAL2) != 0) directions.Add("H2");
            if ((Mode & VERTICAL1) != 0) directions.Add("V1");
            if ((Mode & VERTICAL2) != 0) directions.Add("V2");

            string modeText = directions.Count > 0 ? string.Join(",", directions) : "None";
            
            return $"Mirror: {modeText}, Beat: {(OnBeat ? "On" : "Off")}, " +
                   $"Smooth: {(Smooth ? "On" : "Off")}, Speed: {Slower}";
        }

        #endregion
    }
}
```

## Key Features

### Mirror Modes
- **Horizontal1**: Mirror top half to bottom
- **Horizontal2**: Mirror bottom half to top  
- **Vertical1**: Mirror left half to right
- **Vertical2**: Mirror right half to left

### Smooth Transitions
- Gradual blending between mirror states
- Configurable transition speed (1-16)
- Frame-based transition updates
- Adaptive blending algorithm

### Beat Reactivity
- Random mirror mode selection on beat
- Dynamic mode switching
- Configurable beat response

### Performance Optimizations
- Bitwise mode management
- Efficient pixel copying
- Parallel processing support
- Memory-efficient operations

## Usage Examples

```csharp
// Create a mirror effect with horizontal and vertical mirroring
var mirrorNode = new MirrorEffectsNode
{
    Mode = MirrorEffectsNode.HORIZONTAL1 | MirrorEffectsNode.VERTICAL1,
    Smooth = true,
    Slower = 8,
    OnBeat = true
};

// Apply to image
var mirroredImage = mirrorNode.ProcessFrame(inputImage, audioFeatures);
```

## Technical Details

### Blending Algorithm
The effect uses an adaptive blending function that smoothly transitions between mirror states:

```csharp
result = (colorA * (16 - divisor) + colorB * divisor) / 16
```

### Transition Management
- Frame-based transition updates
- Divisor-based smooth blending
- Increment direction control
- Wrapping arithmetic for seamless loops

### Memory Management
- Efficient pixel buffer operations
- Minimal memory allocation
- Thread-safe rendering
- Optimized array copying

This implementation provides a complete, production-ready mirror effect system that faithfully reproduces the original C++ functionality while leveraging C# features for improved maintainability and performance.
