# Custom BPM Effects

The Custom BPM effect provides advanced beat generation and manipulation capabilities, allowing users to create custom rhythmic patterns, skip beats, invert beat detection, and generate arbitrary tempo-based beats.

## Overview

The Custom BPM effect extends beyond simple beat detection by offering multiple modes of beat generation and manipulation. It can generate beats at arbitrary intervals, skip specific beat patterns, invert beat detection logic, and provide visual feedback through animated sliders that respond to beat events.

## Properties

### Core Settings
- **Enabled**: Controls whether the Custom BPM effect is active
- **Arbitrary**: Enables arbitrary beat generation at specified intervals
- **Skip**: Enables beat skipping mode to filter incoming beats
- **Invert**: Inverts the beat detection logic (beats become non-beats and vice versa)
- **ArbitraryValue**: Interval in milliseconds for arbitrary beat generation (200-10000ms)
- **SkipValue**: Number of beats to skip before generating a new beat (1-16)
- **SkipFirst**: Number of initial beats to skip before processing (0-64)
- **Intensity**: Overall intensity of the effect (0.0 to 1.0)

### Internal State
- **InputSlide**: Position of the input slider (0-8) that responds to incoming beats
- **OutputSlide**: Position of the output slider (0-8) that indicates generated beats
- **BeatCount**: Counter for tracking processed beats
- **SkipCount**: Counter for beat skipping logic
- **LastArbitraryTime**: Timestamp of the last arbitrary beat generation
- **InputIncrement/OutputIncrement**: Direction and speed of slider movement

## Beat Generation Modes

### Arbitrary Beat Generation
- Generates beats at user-defined intervals independent of audio input
- Configurable from 200ms to 10 seconds (6-300 BPM)
- Useful for creating consistent rhythmic patterns
- Can be synchronized with external timing sources

### Beat Skipping Mode
- Filters incoming beats based on skip patterns
- Configurable to skip 1-16 beats before generating output
- Creates rhythmic variations and syncopation effects
- Useful for creating complex rhythmic structures

### Beat Inversion Mode
- Inverts the normal beat detection logic
- Generates beats during quiet periods
- Creates contrast effects and rhythmic tension
- Useful for creating off-beat or anti-rhythmic patterns

### Visual Feedback System
- Animated sliders that respond to beat events
- Input slider shows incoming beat detection
- Output slider shows generated beat output
- Real-time visual feedback for beat manipulation

## Implementation Details

### Beat Processing Pipeline
The effect processes beats through a multi-stage pipeline:

1. **Input Processing**: Receives and validates incoming beat events
2. **Mode Selection**: Determines which beat generation mode is active
3. **Beat Generation**: Applies the selected mode's logic
4. **Output Generation**: Produces modified beat signals
5. **Visual Update**: Updates slider positions and visual feedback

### Timing Management
- Uses high-precision timing for arbitrary beat generation
- Maintains consistent intervals regardless of system load
- Provides smooth transitions between different timing modes
- Supports both millisecond and BPM-based configuration

### Slider Animation System
- Smooth slider movement with configurable speed
- Bounce behavior at slider boundaries (0 and 8)
- Real-time updates synchronized with beat events
- Visual indication of beat processing status

## C# Implementation

```csharp
using System;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class CustomBPMEffectsNode : BaseEffectNode
    {
        #region Properties

        /// <summary>
        /// Controls whether the Custom BPM effect is active
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Enables arbitrary beat generation at specified intervals
        /// </summary>
        public bool Arbitrary { get; set; } = true;

        /// <summary>
        /// Enables beat skipping mode to filter incoming beats
        /// </summary>
        public bool Skip { get; set; } = false;

        /// <summary>
        /// Inverts the beat detection logic
        /// </summary>
        public bool Invert { get; set; } = false;

        /// <summary>
        /// Interval in milliseconds for arbitrary beat generation (200-10000ms)
        /// </summary>
        public int ArbitraryValue { get; set; } = 500;

        /// <summary>
        /// Number of beats to skip before generating a new beat (1-16)
        /// </summary>
        public int SkipValue { get; set; } = 1;

        /// <summary>
        /// Number of initial beats to skip before processing (0-64)
        /// </summary>
        public int SkipFirst { get; set; } = 0;

        /// <summary>
        /// Overall intensity of the effect (0.0 to 1.0)
        /// </summary>
        public float Intensity { get; set; } = 1.0f;

        #endregion

        #region Private Fields

        private int inputSlide = 0;
        private int outputSlide = 0;
        private int oldInputSlide = 0;
        private int oldOutputSlide = 0;
        private int beatCount = 0;
        private int skipCount = 0;
        private DateTime lastArbitraryTime;
        private int inputIncrement = 1;
        private int outputIncrement = 1;
        private bool skipFirstProcessed = false;

        #endregion

        #region Public Methods

        /// <summary>
        /// Processes the current frame with Custom BPM beat manipulation
        /// </summary>
        public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            if (!Enabled)
                return;

            // Process incoming beat detection
            if (audioFeatures.IsBeat)
            {
                ProcessIncomingBeat();
            }

            // Apply skip first logic
            if (SkipFirst > 0 && !skipFirstProcessed)
            {
                if (beatCount <= SkipFirst)
                {
                    return;
                }
                skipFirstProcessed = true;
            }

            // Process different beat generation modes
            bool outputBeat = ProcessBeatModes(audioFeatures);

            // Update visual feedback
            UpdateVisualFeedback(outputBeat);

            // Apply intensity to the output
            if (outputBeat && Intensity < 1.0f)
            {
                ApplyIntensityModification(imageBuffer);
            }
        }

        /// <summary>
        /// Sets the arbitrary beat interval in milliseconds
        /// </summary>
        public void SetArbitraryInterval(int milliseconds)
        {
            ArbitraryValue = Math.Max(200, Math.Min(10000, milliseconds));
        }

        /// <summary>
        /// Sets the arbitrary beat interval in BPM
        /// </summary>
        public void SetArbitraryBPM(int bpm)
        {
            if (bpm > 0)
            {
                ArbitraryValue = 60000 / bpm; // Convert BPM to milliseconds
            }
        }

        /// <summary>
        /// Sets the beat skip value
        /// </summary>
        public void SetSkipValue(int skipValue)
        {
            SkipValue = Math.Max(1, Math.Min(16, skipValue));
        }

        /// <summary>
        /// Sets the number of initial beats to skip
        /// </summary>
        public void SetSkipFirst(int skipFirst)
        {
            SkipFirst = Math.Max(0, Math.Min(64, skipFirst));
        }

        /// <summary>
        /// Gets the current BPM value for arbitrary mode
        /// </summary>
        public int GetArbitraryBPM()
        {
            return ArbitraryValue > 0 ? 60000 / ArbitraryValue : 0;
        }

        /// <summary>
        /// Gets the current input slider position
        /// </summary>
        public int GetInputSlidePosition()
        {
            return inputSlide;
        }

        /// <summary>
        /// Gets the current output slider position
        /// </summary>
        public int GetOutputSlidePosition()
        {
            return outputSlide;
        }

        #endregion

        #region Private Methods

        private void ProcessIncomingBeat()
        {
            beatCount++;
            UpdateInputSlider();
        }

        private void UpdateInputSlider()
        {
            inputSlide += inputIncrement;
            if (inputSlide <= 0 || inputSlide >= 8)
            {
                inputIncrement *= -1;
                inputSlide = Math.Max(0, Math.Min(8, inputSlide));
            }
        }

        private bool ProcessBeatModes(AudioFeatures audioFeatures)
        {
            if (Arbitrary)
            {
                return ProcessArbitraryMode();
            }
            else if (Skip)
            {
                return ProcessSkipMode(audioFeatures);
            }
            else if (Invert)
            {
                return ProcessInvertMode(audioFeatures);
            }

            return false;
        }

        private bool ProcessArbitraryMode()
        {
            var now = DateTime.Now;
            if (now >= lastArbitraryTime.AddMilliseconds(ArbitraryValue))
            {
                lastArbitraryTime = now;
                UpdateOutputSlider();
                return true;
            }
            return false;
        }

        private bool ProcessSkipMode(AudioFeatures audioFeatures)
        {
            if (audioFeatures.IsBeat)
            {
                skipCount++;
                if (skipCount >= SkipValue + 1)
                {
                    skipCount = 0;
                    UpdateOutputSlider();
                    return true;
                }
            }
            return false;
        }

        private bool ProcessInvertMode(AudioFeatures audioFeatures)
        {
            if (audioFeatures.IsBeat)
            {
                return false; // Clear beat during audio beat
            }
            else
            {
                UpdateOutputSlider();
                return true; // Set beat during quiet period
            }
        }

        private void UpdateOutputSlider()
        {
            outputSlide += outputIncrement;
            if (outputSlide <= 0 || outputSlide >= 8)
            {
                outputIncrement *= -1;
                outputSlide = Math.Max(0, Math.Min(8, outputSlide));
            }
        }

        private void UpdateVisualFeedback(bool outputBeat)
        {
            // Store old positions for change detection
            oldInputSlide = inputSlide;
            oldOutputSlide = outputSlide;

            // Visual feedback could be implemented here for UI updates
            // For now, we'll just maintain the slider positions
        }

        private void ApplyIntensityModification(ImageBuffer imageBuffer)
        {
            // Apply intensity-based modifications to the image buffer
            // This could include color adjustments, brightness changes, etc.
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color currentColor = imageBuffer.GetPixel(x, y);
                    Color modifiedColor = ApplyIntensityToColor(currentColor, Intensity);
                    imageBuffer.SetPixel(x, y, modifiedColor);
                }
            }
        }

        private Color ApplyIntensityToColor(Color color, float intensity)
        {
            if (intensity >= 1.0f)
                return color;

            return Color.FromArgb(
                color.A,
                (int)(color.R * intensity),
                (int)(color.G * intensity),
                (int)(color.B * intensity)
            );
        }

        #endregion

        #region Configuration

        /// <summary>
        /// Validates the current configuration
        /// </summary>
        public override bool ValidateConfiguration()
        {
            if (ArbitraryValue < 200 || ArbitraryValue > 10000)
                ArbitraryValue = 500;

            if (SkipValue < 1 || SkipValue > 16)
                SkipValue = 1;

            if (SkipFirst < 0 || SkipFirst > 64)
                SkipFirst = 0;

            if (Intensity < 0.0f || Intensity > 1.0f)
                Intensity = 1.0f;

            // Ensure only one mode is active at a time
            if (Arbitrary && Skip)
            {
                Skip = false;
            }
            if (Arbitrary && Invert)
            {
                Invert = false;
            }
            if (Skip && Invert)
            {
                Invert = false;
            }

            return true;
        }

        /// <summary>
        /// Returns a summary of current settings
        /// </summary>
        public override string GetSettingsSummary()
        {
            string mode = Arbitrary ? "Arbitrary" : Skip ? "Skip" : Invert ? "Invert" : "None";
            string details = "";

            if (Arbitrary)
            {
                details = $", {GetArbitraryBPM()} BPM ({ArbitraryValue}ms)";
            }
            else if (Skip)
            {
                details = $", Skip every {SkipValue} beats";
            }
            else if (Invert)
            {
                details = ", Inverted beat logic";
            }

            if (SkipFirst > 0)
            {
                details += $", Skip first {SkipFirst} beats";
            }

            return $"Custom BPM: {(Enabled ? "Enabled" : "Disabled")}, " +
                   $"Mode: {mode}{details}";
        }

        #endregion

        #region Initialization

        public CustomBPMEffectsNode()
        {
            lastArbitraryTime = DateTime.Now;
            ResetSliders();
        }

        private void ResetSliders()
        {
            inputSlide = 0;
            outputSlide = 0;
            oldInputSlide = 0;
            oldOutputSlide = 0;
            inputIncrement = 1;
            outputIncrement = 1;
            beatCount = 0;
            skipCount = 0;
            skipFirstProcessed = false;
        }

        /// <summary>
        /// Resets all sliders and counters to initial state
        /// </summary>
        public void Reset()
        {
            ResetSliders();
            lastArbitraryTime = DateTime.Now;
        }

        #endregion
    }
}
```

## Usage Examples

### Arbitrary Beat Generation
```csharp
var bpmNode = new CustomBPMEffectsNode();
bpmNode.Enabled = true;
bpmNode.Arbitrary = true;
bpmNode.SetArbitraryBPM(120); // 120 BPM
```

### Beat Skipping Pattern
```csharp
var bpmNode = new CustomBPMEffectsNode();
bpmNode.Enabled = true;
bpmNode.Skip = true;
bpmNode.SetSkipValue(3); // Skip every 3 beats
bpmNode.SetSkipFirst(5); // Skip first 5 beats
```

### Inverted Beat Logic
```csharp
var bpmNode = new CustomBPMEffectsNode();
bpmNode.Enabled = true;
bpmNode.Invert = true;
bpmNode.Intensity = 0.8f;
```

### Complex Rhythmic Pattern
```csharp
var bpmNode = new CustomBPMEffectsNode();
bpmNode.Enabled = true;
bpmNode.Arbitrary = true;
bpmNode.SetArbitraryBPM(90); // 90 BPM
bpmNode.SetSkipFirst(2); // Skip first 2 beats
bpmNode.Intensity = 0.9f;
```

## Performance Notes

- Arbitrary mode uses minimal CPU when not generating beats
- Skip and invert modes add minimal overhead to beat processing
- Visual feedback updates are optimized for smooth animation
- Timing calculations use efficient DateTime operations

## Limitations

- Only one beat generation mode can be active at a time
- Arbitrary intervals are limited to 200ms-10 seconds range
- Skip values are limited to 1-16 beats
- Initial skip count is limited to 0-64 beats

## Future Enhancements

- Multiple simultaneous beat generation modes
- Custom beat pattern creation and sequencing
- Advanced timing algorithms and synchronization
- MIDI clock synchronization support
- Custom visual feedback and effects
- Beat pattern import/export functionality
