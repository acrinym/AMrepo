# Colorfade Effects

## Overview

The Colorfade effect creates sophisticated color manipulation and fading effects by analyzing color relationships and applying dynamic color transformations. It provides advanced color channel manipulation with beat-reactive behavior, smooth transitions, and intelligent color analysis. The effect uses sophisticated color space analysis to determine dominant colors and apply appropriate transformations.

## C++ Source Analysis

**Source File**: `r_colorfade.cpp`

**Key Features**:
- **Color Space Analysis**: Advanced RGB color relationship analysis
- **Dynamic Fading**: Smooth color channel transitions
- **Beat-Reactive Behavior**: Dynamic color changes on beat detection
- **Multi-threaded Rendering**: SMP support for parallel processing
- **Color Clipping**: Intelligent color value clamping
- **Configurable Channels**: Independent RGB channel control
- **Smooth Transitions**: Gradual color value changes

**Core Parameters**:
- `enabled`: Enable flags (bit 1=effect, bit 2=beat, bit 4=smooth)
- `faders[3]`: Normal RGB channel fader values (-32 to 32)
- `beatfaders[3]`: Beat-reactive RGB channel fader values (-32 to 32)
- `faderpos[3]`: Current RGB channel fader positions
- `c_tab[512][512]`: Color relationship lookup table
- `clip[256+40+40]`: Color clipping table

## C# Implementation

```csharp
using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace PhoenixVisualizer.Effects
{
    /// <summary>
    /// Colorfade Effects Node - Creates sophisticated color manipulation and fading effects
    /// </summary>
    public class ColorfadeEffectsNode : AvsModuleNode
    {
        #region Properties

        /// <summary>
        /// Enable the colorfade effect
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Enable beat-reactive behavior
        /// </summary>
        public bool BeatReactive { get; set; } = false;

        /// <summary>
        /// Enable smooth transitions
        /// </summary>
        public bool SmoothTransitions { get; set; } = false;

        /// <summary>
        /// Red channel fader value (-32 to 32)
        /// </summary>
        public int RedFader { get; set; } = 8;

        /// <summary>
        /// Green channel fader value (-32 to 32)
        /// </summary>
        public int GreenFader { get; set; } = -8;

        /// <summary>
        /// Blue channel fader value (-32 to 32)
        /// </summary>
        public int BlueFader { get; set; } = -8;

        /// <summary>
        /// Beat-reactive red channel fader value (-32 to 32)
        /// </summary>
        public int BeatRedFader { get; set; } = 8;

        /// <summary>
        /// Beat-reactive green channel fader value (-32 to 32)
        /// </summary>
        public int BeatGreenFader { get; set; } = -8;

        /// <summary>
        /// Beat-reactive blue channel fader value (-32 to 32)
        /// </summary>
        public int BeatBlueFader { get; set; } = -8;

        #endregion

        #region Constants

        // Fader value constants
        private const int MinFaderValue = -32;
        private const int MaxFaderValue = 32;
        private const int DefaultFaderValue = 8;

        // Color table constants
        private const int ColorTableSize = 512;
        private const int ColorTableCenter = 255;
        private const int ColorTableMaxIndex = 511;

        // Clipping table constants
        private const int ClippingTableSize = 256 + 40 + 40;
        private const int ClippingOffset = 40;
        private const int MaxColorValue = 255;

        // Color relationship constants
        private const int COLOR_RED = 0;
        private const int COLOR_GREEN = 1;
        private const int COLOR_BLUE = 2;
        private const int COLOR_NEUTRAL = 3;

        #endregion

        #region Internal State

        private int lastWidth, lastHeight;
        private readonly object renderLock = new object();
        private readonly byte[,] colorTable;
        private readonly byte[] clippingTable;
        private readonly int[,] faderTable;

        // Current fader positions
        private int currentRedFader;
        private int currentGreenFader;
        private int currentBlueFader;

        #endregion

        #region Constructor

        public ColorfadeEffectsNode()
        {
            // Initialize color relationship table
            colorTable = new byte[ColorTableSize, ColorTableSize];
            InitializeColorTable();

            // Initialize clipping table
            clippingTable = new byte[ClippingTableSize];
            InitializeClippingTable();

            // Initialize fader table
            faderTable = new int[4, 3];

            ResetState();
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Process the image with colorfade effects
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

                // Update fader positions
                UpdateFaderPositions(audioFeatures);

                // Update fader table
                UpdateFaderTable();

                // Create output buffer
                var output = new ImageBuffer(input.Width, input.Height);
                Array.Copy(input.Pixels, output.Pixels, input.Pixels.Length);

                // Apply colorfade effects
                ApplyColorfadeEffects(input, output);

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
            currentRedFader = RedFader;
            currentGreenFader = GreenFader;
            currentBlueFader = BlueFader;
        }

        /// <summary>
        /// Initialize color relationship table
        /// </summary>
        private void InitializeColorTable()
        {
            for (int x = 0; x < ColorTableSize; x++)
            {
                for (int y = 0; y < ColorTableSize; y++)
                {
                    int xp = x - ColorTableCenter;
                    int yp = y - ColorTableCenter;

                    // Determine dominant color based on RGB relationships
                    if (xp > 0 && xp > -yp)
                    {
                        // Green > Blue and Green > Red
                        colorTable[x, y] = COLOR_GREEN;
                    }
                    else if (yp < 0 && xp < -yp)
                    {
                        // Red > Blue and Red > Green
                        colorTable[x, y] = COLOR_RED;
                    }
                    else if (xp < 0 && yp > 0)
                    {
                        // Blue > Green and Blue > Red
                        colorTable[x, y] = COLOR_BLUE;
                    }
                    else
                    {
                        // Neutral or mixed colors
                        colorTable[x, y] = COLOR_NEUTRAL;
                    }
                }
            }
        }

        /// <summary>
        /// Initialize clipping table
        /// </summary>
        private void InitializeClippingTable()
        {
            for (int i = 0; i < ClippingTableSize; i++)
            {
                clippingTable[i] = (byte)Math.Clamp(i - ClippingOffset, 0, MaxColorValue);
            }
        }

        /// <summary>
        /// Update fader positions based on beat and smooth transitions
        /// </summary>
        private void UpdateFaderPositions(AudioFeatures audioFeatures)
        {
            if (!SmoothTransitions)
            {
                // Direct assignment without smooth transitions
                currentRedFader = RedFader;
                currentGreenFader = GreenFader;
                currentBlueFader = BlueFader;
            }
            else
            {
                // Smooth transitions
                SmoothFaderTransition(ref currentRedFader, RedFader);
                SmoothFaderTransition(ref currentGreenFader, GreenFader);
                SmoothFaderTransition(ref currentBlueFader, BlueFader);
            }

            // Beat-reactive behavior
            if (BeatReactive && audioFeatures.IsBeat)
            {
                if (SmoothTransitions)
                {
                    // Random beat-reactive values with smooth transitions
                    currentRedFader = GetRandomBeatFader();
                    currentGreenFader = GetRandomBeatFader();
                    currentBlueFader = GetRandomBeatFader();
                }
                else
                {
                    // Direct beat-reactive values
                    currentRedFader = BeatRedFader;
                    currentGreenFader = BeatGreenFader;
                    currentBlueFader = BeatBlueFader;
                }
            }
        }

        /// <summary>
        /// Smooth fader transition
        /// </summary>
        private void SmoothFaderTransition(ref int currentValue, int targetValue)
        {
            if (currentValue < targetValue)
                currentValue++;
            else if (currentValue > targetValue)
                currentValue--;
        }

        /// <summary>
        /// Get random beat-reactive fader value
        /// </summary>
        private int GetRandomBeatFader()
        {
            Random random = new Random();
            int value = random.Next(64) - 32;
            
            // Avoid values near zero for more dramatic effects
            if (value >= 0 && value < 16)
                value = 32;
            else if (value < 0 && value > -16)
                value = -32;
                
            return value;
        }

        /// <summary>
        /// Update fader table with current values
        /// </summary>
        private void UpdateFaderTable()
        {
            // Pattern 1: Blue, Green, Red
            faderTable[0, 0] = currentBlueFader;
            faderTable[0, 1] = currentGreenFader;
            faderTable[0, 2] = currentRedFader;

            // Pattern 2: Green, Red, Blue
            faderTable[1, 0] = currentGreenFader;
            faderTable[1, 1] = currentRedFader;
            faderTable[1, 2] = currentBlueFader;

            // Pattern 3: Red, Blue, Green
            faderTable[2, 0] = currentRedFader;
            faderTable[2, 1] = currentBlueFader;
            faderTable[2, 2] = currentGreenFader;

            // Pattern 4: Blue, Blue, Blue (uniform)
            faderTable[3, 0] = currentBlueFader;
            faderTable[3, 1] = currentBlueFader;
            faderTable[3, 2] = currentBlueFader;
        }

        /// <summary>
        /// Apply colorfade effects to the image
        /// </summary>
        private void ApplyColorfadeEffects(ImageBuffer input, ImageBuffer output)
        {
            int width = input.Width;
            int height = input.Height;

            // Process pixels in parallel for better performance
            Parallel.For(0, height, y =>
            {
                int rowOffset = y * width;
                for (int x = 0; x < width; x++)
                {
                    int pixelIndex = rowOffset + x;
                    int pixel = input.Pixels[pixelIndex];

                    // Extract RGB components
                    int r = (pixel >> 16) & 0xFF;
                    int g = (pixel >> 8) & 0xFF;
                    int b = pixel & 0xFF;

                    // Calculate color relationship index
                    int colorIndex = CalculateColorIndex(r, g, b);

                    // Get fader pattern based on color relationship
                    int faderPattern = GetFaderPattern(colorIndex);

                    // Apply color transformation
                    int newR = ApplyColorFader(r, faderTable[faderPattern, 0]);
                    int newG = ApplyColorFader(g, faderTable[faderPattern, 1]);
                    int newB = ApplyColorFader(b, faderTable[faderPattern, 2]);

                    // Combine new RGB values
                    output.Pixels[pixelIndex] = (newR << 16) | (newG << 8) | newB;
                }
            });
        }

        /// <summary>
        /// Calculate color relationship index
        /// </summary>
        private int CalculateColorIndex(int r, int g, int b)
        {
            // Calculate color relationship using the same formula as C++
            int gb = g - b;
            int br = b - r;
            
            // Map to table coordinates
            int x = gb + ColorTableCenter;
            int y = br + ColorTableCenter;
            
            // Clamp to valid table range
            x = Math.Clamp(x, 0, ColorTableMaxIndex);
            y = Math.Clamp(y, 0, ColorTableMaxIndex);
            
            return colorTable[x, y];
        }

        /// <summary>
        /// Get fader pattern based on color relationship
        /// </summary>
        private int GetFaderPattern(int colorIndex)
        {
            // Map color relationships to fader patterns
            switch (colorIndex)
            {
                case COLOR_RED: return 0;     // Blue, Green, Red
                case COLOR_GREEN: return 1;   // Green, Red, Blue
                case COLOR_BLUE: return 2;    // Red, Blue, Green
                default: return 3;            // Uniform (Blue, Blue, Blue)
            }
        }

        /// <summary>
        /// Apply color fader with clipping
        /// </summary>
        private int ApplyColorFader(int colorValue, int faderValue)
        {
            int newValue = colorValue + faderValue + ClippingOffset;
            return clippingTable[Math.Clamp(newValue, 0, ClippingTableSize - 1)];
        }

        #endregion

        #region Configuration

        /// <summary>
        /// Validate and clamp property values
        /// </summary>
        public override void ValidateProperties()
        {
            RedFader = Math.Clamp(RedFader, MinFaderValue, MaxFaderValue);
            GreenFader = Math.Clamp(GreenFader, MinFaderValue, MaxFaderValue);
            BlueFader = Math.Clamp(BlueFader, MinFaderValue, MaxFaderValue);
            BeatRedFader = Math.Clamp(BeatRedFader, MinFaderValue, MaxFaderValue);
            BeatGreenFader = Math.Clamp(BeatGreenFader, MinFaderValue, MaxFaderValue);
            BeatBlueFader = Math.Clamp(BeatBlueFader, MinFaderValue, MaxFaderValue);
        }

        /// <summary>
        /// Get a summary of current settings
        /// </summary>
        public override string GetSettingsSummary()
        {
            string enabledText = Enabled ? "Enabled" : "Disabled";
            string beatText = BeatReactive ? "Beat-Reactive" : "Static";
            string smoothText = SmoothTransitions ? "Smooth" : "Instant";
            string faderText = $"R:{RedFader} G:{GreenFader} B:{BlueFader}";
            string beatFaderText = $"R:{BeatRedFader} G:{BeatGreenFader} B:{BeatBlueFader}";

            return $"Colorfade: {enabledText}, {beatText}, {smoothText}, Normal: {faderText}, Beat: {beatFaderText}";
        }

        #endregion
    }
}
```

## Key Features

### Color Space Analysis
- **RGB Relationship Analysis**: Sophisticated color dominance detection
- **Color Table Lookup**: Pre-calculated color relationship mapping
- **Pattern Recognition**: Automatic color pattern identification
- **Intelligent Mapping**: Dynamic color transformation selection

### Dynamic Fading System
- **Independent Channels**: Separate RGB channel control
- **Configurable Values**: -32 to 32 fader range for each channel
- **Smooth Transitions**: Gradual color value changes
- **Instant Switching**: Direct color value assignment

### Beat-Reactive Behavior
- **Dynamic Changes**: Beat-triggered color transformations
- **Random Variations**: Stochastic beat-reactive values
- **Configurable Intensity**: Separate beat-reactive fader values
- **Smooth Integration**: Seamless beat effect integration

### Multi-threaded Rendering
- **Parallel Processing**: SMP support for optimal performance
- **Row-based Distribution**: Efficient thread workload distribution
- **Memory Optimization**: Optimized pixel processing algorithms
- **Scalable Performance**: Automatic thread count adaptation

### Color Clipping System
- **Intelligent Clamping**: Sophisticated color value boundaries
- **Pre-calculated Tables**: Optimized clipping lookup tables
- **Range Protection**: Safe color value manipulation
- **Quality Preservation**: Maintains color integrity

## Usage Examples

```csharp
// Create a beat-reactive colorfade with smooth transitions
var colorfadeNode = new ColorfadeEffectsNode
{
    RedFader = 16,
    GreenFader = -8,
    BlueFader = 0,
    BeatRedFader = 24,
    BeatGreenFader = -16,
    BeatBlueFader = 8,
    BeatReactive = true,
    SmoothTransitions = true
};

// Apply to image
var colorfadedImage = colorfadeNode.ProcessFrame(inputImage, audioFeatures);
```

## Technical Details

### Color Relationship Analysis
The effect analyzes RGB relationships to determine dominant colors:

```csharp
// Calculate color relationship using the same formula as C++
int gb = g - b;    // Green vs Blue relationship
int br = b - r;    // Blue vs Red relationship

// Map to table coordinates
int x = gb + ColorTableCenter;
int y = br + ColorTableCenter;
```

### Fader Pattern System
Four different fader patterns based on color relationships:

```csharp
// Pattern 1: Blue, Green, Red (for red-dominant colors)
// Pattern 2: Green, Red, Blue (for green-dominant colors)  
// Pattern 3: Red, Blue, Green (for blue-dominant colors)
// Pattern 4: Blue, Blue, Blue (for neutral/mixed colors)
```

### Smooth Transition Algorithm
Gradual fader value changes for smooth effects:

```csharp
private void SmoothFaderTransition(ref int currentValue, int targetValue)
{
    if (currentValue < targetValue)
        currentValue++;
    else if (currentValue > targetValue)
        currentValue--;
}
```

### Beat Integration
Random beat-reactive values with intelligent range selection:

```csharp
private int GetRandomBeatFader()
{
    Random random = new Random();
    int value = random.Next(64) - 32;
    
    // Avoid values near zero for more dramatic effects
    if (value >= 0 && value < 16)
        value = 32;
    else if (value < 0 && value > -16)
        value = -32;
        
    return value;
}
```

### Color Clipping
Efficient color value clamping using pre-calculated tables:

```csharp
private int ApplyColorFader(int colorValue, int faderValue)
{
    int newValue = colorValue + faderValue + ClippingOffset;
    return clippingTable[Math.Clamp(newValue, 0, ClippingTableSize - 1)];
}
```

This implementation provides a complete, production-ready colorfade system that faithfully reproduces the original C++ functionality while leveraging C# features for improved maintainability and performance.
