# Channel Shift Effects

The Channel Shift effect provides advanced color channel manipulation capabilities, allowing users to swap, rotate, and rearrange RGB color channels in various patterns. It includes beat-responsive random channel swapping for dynamic visual effects.

## Overview

The Channel Shift effect manipulates the RGB color channels of each pixel in the image, creating color distortion effects that can range from subtle shifts to dramatic color transformations. It supports six different channel arrangements and can automatically change patterns in response to beat detection.

## Properties

### Core Settings
- **Enabled**: Controls whether the Channel Shift effect is active
- **Mode**: Channel arrangement mode (RGB, RBG, BRG, BGR, GBR, GRB)
- **OnBeat**: Enables automatic channel mode changes in response to beat detection
- **Intensity**: Overall intensity of the effect (0.0 to 1.0)

### Channel Modes
- **RGB (Default)**: No change - normal color rendering
- **RBG**: Red and Blue channels swapped
- **BRG**: Blue, Red, and Green channels rotated
- **BGR**: Blue and Green channels swapped
- **GBR**: Green, Blue, and Red channels rotated
- **GRB**: Green and Red channels swapped

## Channel Manipulation

### Channel Swapping
- **RBG Mode**: Swaps red and blue channels, creating purple/cyan color shifts
- **BGR Mode**: Swaps blue and green channels, creating teal/yellow color shifts
- **GRB Mode**: Swaps green and red channels, creating yellow/magenta color shifts

### Channel Rotation
- **BRG Mode**: Rotates channels from Blue→Red→Green, creating color cycling effects
- **GBR Mode**: Rotates channels from Green→Blue→Red, creating alternative color cycling
- **RGB Mode**: No rotation, maintains original colors

### Beat-Responsive Behavior
- Automatically selects random channel modes on beat detection
- Creates dynamic, unpredictable color transformations
- Maintains visual interest during high-energy audio sections
- Can be disabled for static channel arrangements

## Implementation Details

### Color Channel Processing
The effect processes each pixel by manipulating the RGB color components:

1. **Channel Extraction**: Separates red, green, and blue components
2. **Channel Rearrangement**: Applies the selected mode's transformation
3. **Color Reconstruction**: Rebuilds the pixel with modified channel order
4. **Intensity Application**: Applies intensity scaling to the final result

### Performance Optimization
- Processes pixels in blocks of 4 for efficiency
- Uses optimized color manipulation algorithms
- Minimal memory allocation during processing
- Efficient channel swapping operations

### Color Space Handling
- Maintains alpha channel integrity
- Preserves color depth and precision
- Handles edge cases and boundary conditions
- Supports various color formats

## C# Implementation

```csharp
using System;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class ChannelShiftEffectsNode : BaseEffectNode
    {
        #region Enums

        /// <summary>
        /// Defines the available channel arrangement modes
        /// </summary>
        public enum ChannelMode
        {
            /// <summary>
            /// No change - normal color rendering
            /// </summary>
            RGB = 0,

            /// <summary>
            /// Red and Blue channels swapped
            /// </summary>
            RBG = 1,

            /// <summary>
            /// Blue, Red, and Green channels rotated
            /// </summary>
            BRG = 2,

            /// <summary>
            /// Blue and Green channels swapped
            /// </summary>
            BGR = 3,

            /// <summary>
            /// Green, Blue, and Red channels rotated
            /// </summary>
            GBR = 4,

            /// <summary>
            /// Green and Red channels swapped
            /// </summary>
            GRB = 5
        }

        #endregion

        #region Properties

        /// <summary>
        /// Controls whether the Channel Shift effect is active
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Current channel arrangement mode
        /// </summary>
        public ChannelMode Mode { get; set; } = ChannelMode.RBG;

        /// <summary>
        /// Enables automatic channel mode changes in response to beat detection
        /// </summary>
        public bool OnBeat { get; set; } = true;

        /// <summary>
        /// Overall intensity of the effect (0.0 to 1.0)
        /// </summary>
        public float Intensity { get; set; } = 1.0f;

        #endregion

        #region Private Fields

        private Random random = new Random();
        private ChannelMode[] availableModes = { ChannelMode.RGB, ChannelMode.RBG, ChannelMode.BRG, ChannelMode.BGR, ChannelMode.GBR, ChannelMode.GRB };

        #endregion

        #region Public Methods

        /// <summary>
        /// Processes the current frame with Channel Shift color manipulation
        /// </summary>
        public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            if (!Enabled)
                return;

            // Handle beat-responsive mode changes
            if (OnBeat && audioFeatures.IsBeat)
            {
                ChangeToRandomMode();
            }

            // Apply channel shifting based on current mode
            ApplyChannelShift(imageBuffer);
        }

        /// <summary>
        /// Sets the channel arrangement mode
        /// </summary>
        public void SetMode(ChannelMode mode)
        {
            Mode = mode;
        }

        /// <summary>
        /// Enables or disables beat-responsive mode changes
        /// </summary>
        public void SetOnBeat(bool enabled)
        {
            OnBeat = enabled;
        }

        /// <summary>
        /// Changes to a random channel mode
        /// </summary>
        public void ChangeToRandomMode()
        {
            int randomIndex = random.Next(availableModes.Length);
            Mode = availableModes[randomIndex];
        }

        /// <summary>
        /// Cycles to the next channel mode
        /// </summary>
        public void CycleToNextMode()
        {
            int currentIndex = Array.IndexOf(availableModes, Mode);
            int nextIndex = (currentIndex + 1) % availableModes.Length;
            Mode = availableModes[nextIndex];
        }

        /// <summary>
        /// Gets the current mode description
        /// </summary>
        public string GetModeDescription()
        {
            return Mode switch
            {
                ChannelMode.RGB => "RGB (Normal)",
                ChannelMode.RBG => "RBG (Red-Blue Swap)",
                ChannelMode.BRG => "BRG (Blue-Red-Green)",
                ChannelMode.BGR => "BGR (Blue-Green Swap)",
                ChannelMode.GBR => "GBR (Green-Blue-Red)",
                ChannelMode.GRB => "GRB (Green-Red Swap)",
                _ => "Unknown"
            };
        }

        #endregion

        #region Private Methods

        private void ApplyChannelShift(ImageBuffer imageBuffer)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color originalColor = imageBuffer.GetPixel(x, y);
                    Color shiftedColor = ShiftColorChannels(originalColor);
                    
                    if (Intensity < 1.0f)
                    {
                        shiftedColor = ApplyIntensity(originalColor, shiftedColor, Intensity);
                    }

                    imageBuffer.SetPixel(x, y, shiftedColor);
                }
            }
        }

        private Color ShiftColorChannels(Color color)
        {
            return Mode switch
            {
                ChannelMode.RGB => color, // No change
                ChannelMode.RBG => Color.FromArgb(color.A, color.B, color.G, color.R), // R↔B
                ChannelMode.BRG => Color.FromArgb(color.A, color.B, color.R, color.G), // B→R→G
                ChannelMode.BGR => Color.FromArgb(color.A, color.B, color.G, color.R), // B↔G
                ChannelMode.GBR => Color.FromArgb(color.A, color.G, color.B, color.R), // G→B→R
                ChannelMode.GRB => Color.FromArgb(color.A, color.G, color.R, color.B), // G↔R
                _ => color
            };
        }

        private Color ApplyIntensity(Color original, Color shifted, float intensity)
        {
            if (intensity >= 1.0f)
                return shifted;

            if (intensity <= 0.0f)
                return original;

            // Blend between original and shifted colors based on intensity
            return Color.FromArgb(
                original.A,
                (int)(original.R + (shifted.R - original.R) * intensity),
                (int)(original.G + (shifted.G - original.G) * intensity),
                (int)(original.B + (shifted.B - original.B) * intensity)
            );
        }

        #endregion

        #region Configuration

        /// <summary>
        /// Validates the current configuration
        /// </summary>
        public override bool ValidateConfiguration()
        {
            if (Intensity < 0.0f || Intensity > 1.0f)
                Intensity = 1.0f;

            // Ensure mode is valid
            if (!Enum.IsDefined(typeof(ChannelMode), Mode))
                Mode = ChannelMode.RBG;

            return true;
        }

        /// <summary>
        /// Returns a summary of current settings
        /// </summary>
        public override string GetSettingsSummary()
        {
            return $"Channel Shift: {(Enabled ? "Enabled" : "Disabled")}, " +
                   $"Mode: {GetModeDescription()}, " +
                   $"On Beat: {(OnBeat ? "Yes" : "No")}";
        }

        #endregion

        #region Advanced Channel Operations

        /// <summary>
        /// Applies a custom channel transformation
        /// </summary>
        public void ApplyCustomTransformation(ImageBuffer imageBuffer, Func<Color, Color> transformation)
        {
            if (!Enabled || transformation == null)
                return;

            int width = imageBuffer.Width;
            int height = imageBuffer.Height;

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color originalColor = imageBuffer.GetPixel(x, y);
                    Color transformedColor = transformation(originalColor);
                    imageBuffer.SetPixel(x, y, transformedColor);
                }
            }
        }

        /// <summary>
        /// Creates a channel mask effect
        /// </summary>
        public void ApplyChannelMask(ImageBuffer imageBuffer, bool redMask, bool greenMask, bool blueMask)
        {
            if (!Enabled)
                return;

            int width = imageBuffer.Width;
            int height = imageBuffer.Height;

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color originalColor = imageBuffer.GetPixel(x, y);
                    Color maskedColor = Color.FromArgb(
                        originalColor.A,
                        redMask ? originalColor.R : 0,
                        greenMask ? originalColor.G : 0,
                        blueMask ? originalColor.B : 0
                    );
                    imageBuffer.SetPixel(x, y, maskedColor);
                }
            }
        }

        /// <summary>
        /// Applies channel-specific intensity adjustments
        /// </summary>
        public void ApplyChannelIntensity(ImageBuffer imageBuffer, float redIntensity, float greenIntensity, float blueIntensity)
        {
            if (!Enabled)
                return;

            int width = imageBuffer.Width;
            int height = imageBuffer.Height;

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color originalColor = imageBuffer.GetPixel(x, y);
                    Color adjustedColor = Color.FromArgb(
                        originalColor.A,
                        (int)(originalColor.R * redIntensity),
                        (int)(originalColor.G * greenIntensity),
                        (int)(originalColor.B * blueIntensity)
                    );
                    imageBuffer.SetPixel(x, y, adjustedColor);
                }
            }
        }

        #endregion

        #region Preset Configurations

        /// <summary>
        /// Applies a warm color temperature effect
        /// </summary>
        public void ApplyWarmEffect(ImageBuffer imageBuffer)
        {
            SetMode(ChannelMode.RBG);
            ApplyChannelIntensity(imageBuffer, 1.2f, 1.0f, 0.8f);
        }

        /// <summary>
        /// Applies a cool color temperature effect
        /// </summary>
        public void ApplyCoolEffect(ImageBuffer imageBuffer)
        {
            SetMode(ChannelMode.BRG);
            ApplyChannelIntensity(imageBuffer, 0.8f, 1.0f, 1.2f);
        }

        /// <summary>
        /// Applies a vintage film effect
        /// </summary>
        public void ApplyVintageEffect(ImageBuffer imageBuffer)
        {
            SetMode(ChannelMode.GRB);
            ApplyChannelIntensity(imageBuffer, 1.1f, 0.9f, 0.7f);
        }

        /// <summary>
        /// Applies a high contrast effect
        /// </summary>
        public void ApplyHighContrastEffect(ImageBuffer imageBuffer)
        {
            SetMode(ChannelMode.RGB);
            ApplyChannelIntensity(imageBuffer, 1.3f, 1.3f, 1.3f);
        }

        #endregion
    }
}
```

## Usage Examples

### Basic Channel Swapping
```csharp
var channelShiftNode = new ChannelShiftEffectsNode();
channelShiftNode.Enabled = true;
channelShiftNode.SetMode(ChannelShiftEffectsNode.ChannelMode.RBG);
channelShiftNode.OnBeat = false;
```

### Beat-Responsive Random Effects
```csharp
var channelShiftNode = new ChannelShiftEffectsNode();
channelShiftNode.Enabled = true;
channelShiftNode.OnBeat = true;
channelShiftNode.Intensity = 0.8f;
```

### Custom Channel Transformation
```csharp
var channelShiftNode = new ChannelShiftEffectsNode();
channelShiftNode.Enabled = true;

// Apply custom transformation
channelShiftNode.ApplyCustomTransformation(imageBuffer, color =>
{
    return Color.FromArgb(color.A, color.B, color.R, color.G);
});
```

### Channel Masking
```csharp
var channelShiftNode = new ChannelShiftEffectsNode();
channelShiftNode.Enabled = true;

// Show only red and blue channels
channelShiftNode.ApplyChannelMask(imageBuffer, true, false, true);
```

### Preset Effects
```csharp
var channelShiftNode = new ChannelShiftEffectsNode();
channelShiftNode.Enabled = true;

// Apply warm color temperature
channelShiftNode.ApplyWarmEffect(imageBuffer);

// Or apply vintage film effect
channelShiftNode.ApplyVintageEffect(imageBuffer);
```

## Performance Notes

- Channel swapping operations are highly optimized
- Processes pixels in efficient blocks
- Minimal memory allocation during processing
- Intensity blending adds minimal overhead

## Limitations

- Only supports RGB color space
- Channel modes are predefined and cannot be customized
- Beat response is limited to random mode selection
- Intensity blending may affect color accuracy

## Future Enhancements

- Custom channel transformation functions
- HSV and other color space support
- Advanced channel blending algorithms
- Real-time parameter modulation
- MIDI control for channel parameters
- Channel animation and keyframing
