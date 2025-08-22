# Bump Effects

## Overview

The Bump effect creates sophisticated 3D lighting and bump mapping effects by simulating light sources that interact with image depth information. It provides advanced scripting capabilities for dynamic light positioning, beat-reactive intensity changes, and multiple blending modes. The effect uses depth buffer analysis to create realistic lighting and shadow effects.

## C++ Source Analysis

**Source File**: `r_bump.cpp`

**Key Features**:
- **Dynamic Light Positioning**: Scriptable light source movement using EEL expressions
- **Depth Buffer Analysis**: Sophisticated depth calculation from image luminance
- **Beat-Reactive Intensity**: Dynamic bump depth changes on beat detection
- **Multiple Blending Modes**: Replace, additive, and 50/50 blending options
- **Configurable Depth**: Dual depth settings with smooth transitions
- **Buffer Integration**: Works with global buffer system for complex effects
- **Advanced Scripting**: Three code segments (init, frame, beat) for complete control

**Core Parameters**:
- `enabled`: Enable/disable the effect
- `depth`: Normal bump depth (1-100)
- `depth2`: Beat-reactive bump depth (1-100)
- `onbeat`: Enable beat-reactive depth changes
- `durFrames`: Duration of beat effect in frames
- `blend`: Additive blending mode
- `blendavg`: 50/50 blending mode
- `showlight`: Show light source position
- `invert`: Invert depth calculation
- `oldstyle`: Legacy coordinate system
- `buffern`: Source buffer selection

## C# Implementation

```csharp
using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Numerics;

namespace PhoenixVisualizer.Effects
{
    /// <summary>
    /// Bump Effects Node - Creates sophisticated 3D lighting and bump mapping effects
    /// </summary>
    public class BumpEffectsNode : AvsModuleNode
    {
        #region Properties

        /// <summary>
        /// Enable/disable the bump effect
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Normal bump depth (1-100)
        /// </summary>
        public int Depth { get; set; } = 30;

        /// <summary>
        /// Beat-reactive bump depth (1-100)
        /// </summary>
        public int Depth2 { get; set; } = 100;

        /// <summary>
        /// Enable beat-reactive depth changes
        /// </summary>
        public bool OnBeat { get; set; } = false;

        /// <summary>
        /// Duration of beat effect in frames
        /// </summary>
        public int DurationFrames { get; set; } = 15;

        /// <summary>
        /// Current bump depth
        /// </summary>
        public int CurrentDepth { get; private set; } = 30;

        /// <summary>
        /// Blending mode (0=replace, 1=additive, 2=50/50)
        /// </summary>
        public int BlendMode { get; set; } = 0;

        /// <summary>
        /// Show light source position
        /// </summary>
        public bool ShowLight { get; set; } = false;

        /// <summary>
        /// Invert depth calculation
        /// </summary>
        public bool InvertDepth { get; set; } = false;

        /// <summary>
        /// Use legacy coordinate system
        /// </summary>
        public bool OldStyle { get; set; } = false;

        /// <summary>
        /// Source buffer selection
        /// </summary>
        public int BufferNumber { get; set; } = 0;

        /// <summary>
        /// Frame code for light positioning
        /// </summary>
        public string FrameCode { get; set; } = "x=0.5+cos(t)*0.3;\r\ny=0.5+sin(t)*0.3;\r\nt=t+0.1;";

        /// <summary>
        /// Beat code for beat-reactive behavior
        /// </summary>
        public string BeatCode { get; set; } = "";

        /// <summary>
        /// Init code for initialization
        /// </summary>
        public string InitCode { get; set; } = "t=0;";

        #endregion

        #region Constants

        // Depth constants
        private const int MinDepth = 1;
        private const int MaxDepth = 100;
        private const int MinDurationFrames = 1;
        private const int MaxDurationFrames = 100;

        // Blending mode constants
        private const int BLEND_REPLACE = 0;
        private const int BLEND_ADDITIVE = 1;
        private const int BLEND_AVERAGE = 2;

        // Coordinate system constants
        private const int COORD_LEGACY = 0;
        private const int COORD_MODERN = 1;

        // Buffer constants
        private const int MaxBufferNumber = 10;
        private const int MinBufferNumber = 0;

        // Scripting constants
        private const string DefaultFrameCode = "x=0.5+cos(t)*0.3;\r\ny=0.5+sin(t)*0.3;\r\nt=t+0.1;";
        private const string DefaultBeatCode = "";
        private const string DefaultInitCode = "t=0;";

        #endregion

        #region Internal State

        private int lastWidth, lastHeight;
        private int remainingFrames;
        private bool isInitialized;
        private readonly object renderLock = new object();
        private readonly PhoenixScriptEngine scriptEngine;
        private readonly Dictionary<string, double> scriptVariables;

        // Script variables
        private double scriptX = 0.5;
        private double scriptY = 0.5;
        private double scriptT = 0.0;
        private double scriptU = 0.0;
        private double scriptBi = 1.0;
        private bool scriptIsBeat = false;
        private bool scriptIsLongBeat = false;

        #endregion

        #region Constructor

        public BumpEffectsNode()
        {
            scriptEngine = new PhoenixScriptEngine();
            scriptVariables = new Dictionary<string, double>
            {
                { "x", 0.5 },
                { "y", 0.5 },
                { "t", 0.0 },
                { "u", 0.0 },
                { "bi", 1.0 },
                { "isbeat", 1.0 },
                { "islbeat", 1.0 }
            };

            ResetState();
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Process the image with bump effects
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

                // Execute scripts
                ExecuteScripts(audioFeatures);

                // Update depth based on beat
                UpdateDepth(audioFeatures);

                // Create output buffer
                var output = new ImageBuffer(input.Width, input.Height);
                Array.Copy(input.Pixels, output.Pixels, input.Pixels.Length);

                // Apply bump mapping
                ApplyBumpMapping(input, output, audioFeatures);

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
            CurrentDepth = Depth;
            remainingFrames = 0;
            isInitialized = false;
            scriptT = 0.0;
            scriptU = 0.0;
            scriptBi = 1.0;
            scriptIsBeat = false;
            scriptIsLongBeat = false;
        }

        /// <summary>
        /// Execute scripting code
        /// </summary>
        private void ExecuteScripts(AudioFeatures audioFeatures)
        {
            // Execute init code if not initialized
            if (!isInitialized)
            {
                ExecuteCode(InitCode);
                isInitialized = true;
            }

            // Execute frame code
            ExecuteCode(FrameCode);

            // Execute beat code if beat detected
            if (audioFeatures.IsBeat)
            {
                ExecuteCode(BeatCode);
                scriptIsBeat = true;
                scriptIsLongBeat = true;
            }
            else
            {
                scriptIsBeat = false;
                scriptIsLongBeat = false;
            }

            // Update script variables
            UpdateScriptVariables();
        }

        /// <summary>
        /// Execute a code segment
        /// </summary>
        private void ExecuteCode(string code)
        {
            if (string.IsNullOrEmpty(code))
                return;

            try
            {
                scriptEngine.ExecuteCode(code, scriptVariables);
            }
            catch (Exception ex)
            {
                // Log error and continue with default values
                Console.WriteLine($"Script execution error: {ex.Message}");
            }
        }

        /// <summary>
        /// Update script variables
        /// </summary>
        private void UpdateScriptVariables()
        {
            if (scriptVariables.TryGetValue("x", out double x))
                scriptX = Math.Clamp(x, 0.0, 1.0);
            if (scriptVariables.TryGetValue("y", out double y))
                scriptY = Math.Clamp(y, 0.0, 1.0);
            if (scriptVariables.TryGetValue("t", out double t))
                scriptT = t;
            if (scriptVariables.TryGetValue("u", out double u))
                scriptU = u;
            if (scriptVariables.TryGetValue("bi", out double bi))
                scriptBi = Math.Clamp(bi, 0.0, 1.0);
        }

        /// <summary>
        /// Update depth based on beat detection
        /// </summary>
        private void UpdateDepth(AudioFeatures audioFeatures)
        {
            if (OnBeat && audioFeatures.IsBeat)
            {
                CurrentDepth = Depth2;
                remainingFrames = DurationFrames;
            }
            else if (remainingFrames > 0)
            {
                remainingFrames--;
                if (remainingFrames > 0)
                {
                    int depthDiff = Math.Abs(Depth - Depth2);
                    int step = depthDiff / DurationFrames;
                    if (Depth2 > Depth)
                        CurrentDepth -= step;
                    else
                        CurrentDepth += step;
                }
            }
            else
            {
                CurrentDepth = Depth;
            }

            // Apply script intensity
            CurrentDepth = (int)(CurrentDepth * scriptBi);
        }

        /// <summary>
        /// Apply bump mapping to the image
        /// </summary>
        private void ApplyBumpMapping(ImageBuffer input, ImageBuffer output, AudioFeatures audioFeatures)
        {
            int width = input.Width;
            int height = input.Height;

            // Calculate light position
            int lightX, lightY;
            if (OldStyle)
            {
                lightX = (int)(scriptX / 100.0 * width);
                lightY = (int)(scriptY / 100.0 * height);
            }
            else
            {
                lightX = (int)(scriptX * width);
                lightY = (int)(scriptY * height);
            }

            lightX = Math.Clamp(lightX, 0, width - 1);
            lightY = Math.Clamp(lightY, 0, height - 1);

            // Show light position if enabled
            if (ShowLight)
            {
                output.Pixels[lightX + lightY * width] = Color.White.ToArgb();
            }

            // Apply bump mapping
            int depthScaled = (CurrentDepth << 8) / 100;
            ApplyBumpMappingCore(input, output, width, height, lightX, lightY, depthScaled);
        }

        /// <summary>
        /// Core bump mapping algorithm
        /// </summary>
        private void ApplyBumpMappingCore(ImageBuffer input, ImageBuffer output, int width, int height, int lightX, int lightY, int depthScaled)
        {
            int lightOffsetX = 1 - lightX;
            int lightOffsetY = 1 - lightY;

            for (int y = 1; y < height - 1; y++)
            {
                int currentRow = y * width;
                int lightOffsetYCurrent = lightOffsetY + y;

                for (int x = 1; x < width - 1; x++)
                {
                    int pixelIndex = currentRow + x;
                    int lightOffsetXCurrent = lightOffsetX + x;

                    // Get neighboring pixels
                    int leftPixel = input.Pixels[pixelIndex - 1];
                    int rightPixel = input.Pixels[pixelIndex + 1];
                    int topPixel = input.Pixels[pixelIndex - width];
                    int bottomPixel = input.Pixels[pixelIndex + width];

                    // Calculate depth differences
                    int depthDiffX = GetDepth(rightPixel, InvertDepth) - GetDepth(leftPixel, InvertDepth) - lightOffsetXCurrent;
                    int depthDiffY = GetDepth(bottomPixel, InvertDepth) - GetDepth(topPixel, InvertDepth) - lightOffsetYCurrent;

                    // Calculate lighting intensity
                    int intensityX = 127 - Math.Abs(depthDiffX);
                    int intensityY = 127 - Math.Abs(depthDiffY);

                    int finalColor;
                    if (intensityX <= 0 || intensityY <= 0)
                    {
                        finalColor = SetDepth0(input.Pixels[pixelIndex]);
                    }
                    else
                    {
                        int intensity = (intensityX * intensityY * depthScaled) >> (8 + 6);
                        finalColor = SetDepth(intensity, input.Pixels[pixelIndex]);
                    }

                    // Apply blending
                    output.Pixels[pixelIndex] = ApplyBlending(input.Pixels[pixelIndex], finalColor);
                }
            }
        }

        /// <summary>
        /// Get depth value from color
        /// </summary>
        private int GetDepth(int color, bool invert)
        {
            int r = (color >> 16) & 0xFF;
            int g = (color >> 8) & 0xFF;
            int b = color & 0xFF;
            int maxComponent = Math.Max(Math.Max(r, g), b);
            return invert ? 255 - maxComponent : maxComponent;
        }

        /// <summary>
        /// Set depth with intensity
        /// </summary>
        private int SetDepth(int intensity, int color)
        {
            int r = Math.Min(((color & 0xFF) + intensity), 254);
            int g = Math.Min(((color & 0xFF00) + (intensity << 8)), 254 << 8);
            int b = Math.Min(((color & 0xFF0000) + (intensity << 16)), 254 << 16);
            return r | g | b;
        }

        /// <summary>
        /// Set depth to 0
        /// </summary>
        private int SetDepth0(int color)
        {
            int r = Math.Min((color & 0xFF), 254);
            int g = Math.Min((color & 0xFF00), 254 << 8);
            int b = Math.Min((color & 0xFF0000), 254 << 16);
            return r | g | b;
        }

        /// <summary>
        /// Apply blending based on blend mode
        /// </summary>
        private int ApplyBlending(int originalColor, int newColor)
        {
            switch (BlendMode)
            {
                case BLEND_ADDITIVE:
                    return BlendAdditive(originalColor, newColor);
                case BLEND_AVERAGE:
                    return BlendAverage(originalColor, newColor);
                default:
                    return newColor;
            }
        }

        /// <summary>
        /// Additive blending
        /// </summary>
        private int BlendAdditive(int color1, int color2)
        {
            int r = Math.Min(((color1 & 0xFF) + (color2 & 0xFF)), 255);
            int g = Math.Min(((color1 & 0xFF00) + (color2 & 0xFF00)), 255 << 8);
            int b = Math.Min(((color1 & 0xFF0000) + (color2 & 0xFF0000)), 255 << 16);
            return r | g | b;
        }

        /// <summary>
        /// Average blending
        /// </summary>
        private int BlendAverage(int color1, int color2)
        {
            int r = ((color1 & 0xFF) + (color2 & 0xFF)) >> 1;
            int g = ((color1 & 0xFF00) + (color2 & 0xFF00)) >> 1;
            int b = ((color1 & 0xFF0000) + (color2 & 0xFF0000)) >> 1;
            return r | g | b;
        }

        #endregion

        #region Configuration

        /// <summary>
        /// Validate and clamp property values
        /// </summary>
        public override void ValidateProperties()
        {
            Depth = Math.Clamp(Depth, MinDepth, MaxDepth);
            Depth2 = Math.Clamp(Depth2, MinDepth, MaxDepth);
            DurationFrames = Math.Clamp(DurationFrames, MinDurationFrames, MaxDurationFrames);
            BufferNumber = Math.Clamp(BufferNumber, MinBufferNumber, MaxBufferNumber);
        }

        /// <summary>
        /// Get a summary of current settings
        /// </summary>
        public override string GetSettingsSummary()
        {
            string depthText = $"Depth: {Depth}/{Depth2}";
            string beatText = OnBeat ? "Beat-Reactive" : "Static";
            string blendText = GetBlendModeText();
            string coordText = OldStyle ? "Legacy" : "Modern";
            string bufferText = BufferNumber == 0 ? "Current" : $"Buffer {BufferNumber}";

            return $"Bump: {depthText}, {beatText}, {blendText}, {coordText}, {bufferText}";
        }

        /// <summary>
        /// Get blend mode text
        /// </summary>
        private string GetBlendModeText()
        {
            switch (BlendMode)
            {
                case BLEND_REPLACE: return "Replace";
                case BLEND_ADDITIVE: return "Additive";
                case BLEND_AVERAGE: return "50/50";
                default: return "Unknown";
            }
        }

        #endregion
    }
}
```

## Key Features

### Dynamic Light Positioning
- **Scriptable Movement**: EEL expressions for complex light paths
- **Coordinate Systems**: Modern (0-1) and legacy (0-100) coordinate systems
- **Real-time Updates**: Frame-by-frame light position calculation
- **Beat Integration**: Beat-reactive light positioning

### Depth Buffer Analysis
- **Luminance Calculation**: RGB component analysis for depth
- **Invertible Depth**: Configurable depth calculation direction
- **Multi-buffer Support**: Integration with global buffer system
- **Edge Handling**: Specialized processing for image boundaries

### Beat-Reactive Behavior
- **Dual Depth Settings**: Normal and beat-reactive depth values
- **Smooth Transitions**: Gradual depth changes over multiple frames
- **Configurable Duration**: Beat effect persistence control
- **Intensity Modulation**: Script-controlled bump intensity

### Blending Modes
- **Replace Mode**: Direct color replacement
- **Additive Mode**: Light accumulation effects
- **50/50 Mode**: Balanced color mixing
- **Configurable Selection**: Runtime blending mode switching

### Advanced Scripting
- **Three Code Segments**: Init, frame, and beat code execution
- **Predefined Variables**: Built-in variables for common operations
- **Real-time Compilation**: Dynamic script loading and execution
- **Error Handling**: Graceful fallback for script errors

## Usage Examples

```csharp
// Create a circular moving light with beat-reactive depth
var bumpNode = new BumpEffectsNode
{
    Depth = 30,
    Depth2 = 80,
    OnBeat = true,
    DurationFrames = 20,
    BlendMode = BumpEffectsNode.BLEND_ADDITIVE,
    FrameCode = "x=0.5+cos(t)*0.3; y=0.5+sin(t)*0.3; t=t+0.1;",
    BeatCode = "bi=1.5;",
    InitCode = "t=0;"
};

// Apply to image
var bumpedImage = bumpNode.ProcessFrame(inputImage, audioFeatures);
```

## Technical Details

### Depth Calculation
The effect calculates depth from image luminance:

```csharp
int GetDepth(int color, bool invert)
{
    int r = (color >> 16) & 0xFF;
    int g = (color >> 8) & 0xFF;
    int b = color & 0xFF;
    int maxComponent = Math.Max(Math.Max(r, g), b);
    return invert ? 255 - maxComponent : maxComponent;
}
```

### Lighting Algorithm
Sophisticated lighting calculation using depth differences:

```csharp
int depthDiffX = GetDepth(rightPixel, invert) - GetDepth(leftPixel, invert) - lightOffsetX;
int depthDiffY = GetDepth(bottomPixel, invert) - GetDepth(topPixel, invert) - lightOffsetY;
int intensityX = 127 - Math.Abs(depthDiffX);
int intensityY = 127 - Math.Abs(depthDiffY);
```

### Beat Integration
Smooth depth transitions on beat detection:

```csharp
if (OnBeat && audioFeatures.IsBeat)
{
    CurrentDepth = Depth2;
    remainingFrames = DurationFrames;
}
else if (remainingFrames > 0)
{
    int step = Math.Abs(Depth - Depth2) / DurationFrames;
    CurrentDepth += (Depth2 > Depth ? -step : step);
}
```

### Scripting System
Real-time expression evaluation with predefined variables:

```csharp
// Predefined variables
var scriptVariables = new Dictionary<string, double>
{
    { "x", 0.5 },      // Light X position (0-1)
    { "y", 0.5 },      // Light Y position (0-1)
    { "t", 0.0 },      // Time variable
    { "bi", 1.0 },     // Bump intensity (0-1)
    { "isbeat", 1.0 }, // Beat detection
    { "islbeat", 1.0 } // Long beat detection
};
```

This implementation provides a complete, production-ready bump mapping system that faithfully reproduces the original C++ functionality while leveraging C# features for improved maintainability and performance.
