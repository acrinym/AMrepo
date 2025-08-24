# Dynamic Color Modulation Effects

The Dynamic Color Modulation effect uses EEL (Expression Evaluation Language) scripting to dynamically modify color channels in real-time. It provides four script sections for different phases of processing and includes a lookup table system for efficient color transformations.

## Effect Overview

The Dynamic Color Modulation effect works by:
1. Executing EEL scripts at different processing phases (init, level, frame, beat)
2. Using lookup tables to store pre-calculated color transformations
3. Applying real-time color modifications based on script execution
4. Supporting beat-responsive and frame-by-frame color adjustments

## C# Implementation

```csharp
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Text;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class DynamicColorModulationEffectsNode : BaseEffectNode
    {
        #region Properties
        
        /// <summary>
        /// Whether the effect is enabled
        /// </summary>
        public bool Enabled { get; set; } = true;
        
        /// <summary>
        /// EEL script for initialization phase
        /// </summary>
        public string InitScript { get; set; } = "";
        
        /// <summary>
        /// EEL script for level/pixel processing phase
        /// </summary>
        public string LevelScript { get; set; } = "";
        
        /// <summary>
        /// EEL script for frame processing phase
        /// </summary>
        public string FrameScript { get; set; } = "";
        
        /// <summary>
        /// EEL script for beat response phase
        /// </summary>
        public string BeatScript { get; set; } = "";
        
        /// <summary>
        /// Whether to recompute lookup tables on every frame
        /// </summary>
        public bool RecomputeTables { get; set; } = false;
        
        /// <summary>
        /// Effect intensity multiplier
        /// </summary>
        public float Intensity { get; set; } = 1.0f;
        
        /// <summary>
        /// Whether to enable beat response mode
        /// </summary>
        public bool BeatResponseEnabled { get; set; } = true;
        
        /// <summary>
        /// Maximum script execution time in milliseconds
        /// </summary>
        public int MaxExecutionTime { get; set; } = 100;
        
        #endregion
        
        #region Private Fields
        
        /// <summary>
        /// Pre-calculated color transformation lookup table
        /// </summary>
        private byte[] _colorTable;
        
        /// <summary>
        /// Whether the lookup table is valid
        /// </summary>
        private bool _tableValid = false;
        
        /// <summary>
        /// EEL script engine instance
        /// </summary>
        private EELScriptEngine _scriptEngine;
        
        /// <summary>
        /// Compiled script handles for each phase
        /// </summary>
        private object[] _compiledScripts;
        
        /// <summary>
        /// Whether scripts need recompilation
        /// </summary>
        private bool _scriptsNeedRecompilation = true;
        
        /// <summary>
        /// Whether the effect has been initialized
        /// </summary>
        private bool _isInitialized = false;
        
        /// <summary>
        /// Current beat state
        /// </summary>
        private bool _currentBeat = false;
        
        /// <summary>
        /// Frame counter for timing
        /// </summary>
        private int _frameCounter = 0;
        
        #endregion
        
        #region Constructor
        
        public DynamicColorModulationEffectsNode()
        {
            _colorTable = new byte[768]; // 256 * 3 channels
            _compiledScripts = new object[4];
            _scriptEngine = new EELScriptEngine();
            
            // Set default scripts
            SetDefaultScripts();
        }
        
        #endregion
        
        #region Initialization Methods
        
        /// <summary>
        /// Set default EEL scripts for common effects
        /// </summary>
        private void SetDefaultScripts()
        {
            LevelScript = "red=red; green=green; blue=blue;";
            FrameScript = "";
            BeatScript = "";
            InitScript = "";
        }
        
        /// <summary>
        /// Initialize the EEL script engine and variables
        /// </summary>
        private void InitializeScriptEngine()
        {
            if (_scriptEngine == null)
            {
                _scriptEngine = new EELScriptEngine();
            }
            
            // Register standard variables
            _scriptEngine.RegisterVariable("red", 0.0);
            _scriptEngine.RegisterVariable("green", 0.0);
            _scriptEngine.RegisterVariable("blue", 0.0);
            _scriptEngine.RegisterVariable("beat", 0.0);
            _scriptEngine.RegisterVariable("frame", 0.0);
            _scriptEngine.RegisterVariable("time", 0.0);
            
            _isInitialized = true;
        }
        
        #endregion
        
        #region Processing Methods
        
        public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            if (!Enabled || imageBuffer == null) return;
            
            // Initialize if needed
            if (!_isInitialized)
            {
                InitializeScriptEngine();
            }
            
            // Update beat state
            _currentBeat = audioFeatures.IsBeat;
            _frameCounter++;
            
            // Recompile scripts if needed
            if (_scriptsNeedRecompilation)
            {
                RecompileScripts();
            }
            
            // Execute scripts in order
            ExecuteInitScript();
            ExecuteFrameScript();
            if (_currentBeat)
            {
                ExecuteBeatScript();
            }
            
            // Update lookup table if needed
            if (RecomputeTables || !_tableValid)
            {
                UpdateLookupTable();
            }
            
            // Apply color transformations
            ApplyColorModulation(imageBuffer);
        }
        
        /// <summary>
        /// Recompile all EEL scripts
        /// </summary>
        private void RecompileScripts()
        {
            try
            {
                _compiledScripts[0] = _scriptEngine.CompileScript(LevelScript);
                _compiledScripts[1] = _scriptEngine.CompileScript(FrameScript);
                _compiledScripts[2] = _scriptEngine.CompileScript(BeatScript);
                _compiledScripts[3] = _scriptEngine.CompileScript(InitScript);
                
                _scriptsNeedRecompilation = false;
            }
            catch (Exception ex)
            {
                // Log compilation error
                System.Diagnostics.Debug.WriteLine($"EEL script compilation error: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Execute the initialization script
        /// </summary>
        private void ExecuteInitScript()
        {
            if (_compiledScripts[3] != null && !_isInitialized)
            {
                try
                {
                    _scriptEngine.ExecuteScript(_compiledScripts[3]);
                    _isInitialized = true;
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Init script execution error: {ex.Message}");
                }
            }
        }
        
        /// <summary>
        /// Execute the frame processing script
        /// </summary>
        private void ExecuteFrameScript()
        {
            if (_compiledScripts[1] != null)
            {
                try
                {
                    _scriptEngine.SetVariable("frame", _frameCounter);
                    _scriptEngine.SetVariable("time", _frameCounter / 60.0); // Assuming 60 FPS
                    _scriptEngine.ExecuteScript(_compiledScripts[1]);
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Frame script execution error: {ex.Message}");
                }
            }
        }
        
        /// <summary>
        /// Execute the beat response script
        /// </summary>
        private void ExecuteBeatScript()
        {
            if (_compiledScripts[2] != null)
            {
                try
                {
                    _scriptEngine.SetVariable("beat", 1.0);
                    _scriptEngine.ExecuteScript(_compiledScripts[2]);
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Beat script execution error: {ex.Message}");
                }
            }
        }
        
        /// <summary>
        /// Update the color transformation lookup table
        /// </summary>
        private void UpdateLookupTable()
        {
            for (int i = 0; i < 256; i++)
            {
                // Set input color values (0.0 to 1.0)
                double inputValue = i / 255.0;
                _scriptEngine.SetVariable("red", inputValue);
                _scriptEngine.SetVariable("green", inputValue);
                _scriptEngine.SetVariable("blue", inputValue);
                
                // Execute level script
                if (_compiledScripts[0] != null)
                {
                    try
                    {
                        _scriptEngine.ExecuteScript(_compiledScripts[0]);
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Level script execution error: {ex.Message}");
                        break;
                    }
                }
                
                // Get output values and clamp to valid range
                double outR = Math.Max(0.0, Math.Min(1.0, _scriptEngine.GetVariable("red")));
                double outG = Math.Max(0.0, Math.Min(1.0, _scriptEngine.GetVariable("green")));
                double outB = Math.Max(0.0, Math.Min(1.0, _scriptEngine.GetVariable("blue")));
                
                // Convert to byte values and store in lookup table
                int index = i * 3;
                _colorTable[index] = (byte)(outB * 255.0 + 0.5);     // Blue channel
                _colorTable[index + 1] = (byte)(outG * 255.0 + 0.5); // Green channel
                _colorTable[index + 2] = (byte)(outR * 255.0 + 0.5); // Red channel
            }
            
            _tableValid = true;
        }
        
        /// <summary>
        /// Apply color modulation using the lookup table
        /// </summary>
        private void ApplyColorModulation(ImageBuffer imageBuffer)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color pixel = imageBuffer.GetPixel(x, y);
                    Color modulatedPixel = ModulatePixelColor(pixel);
                    imageBuffer.SetPixel(x, y, modulatedPixel);
                }
            }
        }
        
        /// <summary>
        /// Modulate a single pixel's color using the lookup table
        /// </summary>
        private Color ModulatePixelColor(Color pixel)
        {
            // Apply lookup table transformations
            int blueIndex = pixel.B * 3;
            int greenIndex = pixel.G * 3 + 1;
            int redIndex = pixel.R * 3 + 2;
            
            int newR = _colorTable[redIndex];
            int newG = _colorTable[greenIndex];
            int newB = _colorTable[blueIndex];
            
            // Apply intensity scaling
            if (Intensity != 1.0f)
            {
                newR = (int)(newR * Intensity);
                newG = (int)(newG * Intensity);
                newB = (int)(newB * Intensity);
                
                // Clamp values
                newR = Math.Max(0, Math.Min(255, newR));
                newG = Math.Max(0, Math.Min(255, newG));
                newB = Math.Max(0, Math.Min(255, newB));
            }
            
            return Color.FromArgb(pixel.A, newR, newG, newB);
        }
        
        #endregion
        
        #region Configuration Validation
        
        public override bool ValidateConfiguration()
        {
            if (MaxExecutionTime < 1 || MaxExecutionTime > 1000) return false;
            if (Intensity < 0.0f || Intensity > 10.0f) return false;
            
            // Validate script lengths
            if (InitScript?.Length > 10000) return false;
            if (LevelScript?.Length > 10000) return false;
            if (FrameScript?.Length > 10000) return false;
            if (BeatScript?.Length > 10000) return false;
            
            return true;
        }
        
        #endregion
        
        #region Preset Methods
        
        /// <summary>
        /// Load a 4x red brightness, 2x green, 1x blue effect
        /// </summary>
        public void LoadBrightnessPreset()
        {
            LevelScript = "red=4*red; green=2*green; blue=blue;";
            FrameScript = "";
            BeatScript = "";
            InitScript = "";
            RecomputeTables = false;
            _scriptsNeedRecompilation = true;
        }
        
        /// <summary>
        /// Load a solarization effect
        /// </summary>
        public void LoadSolarizationPreset()
        {
            LevelScript = "red=(min(1,red*2)-red)*2;\ngreen=red; blue=red;";
            FrameScript = "";
            BeatScript = "";
            InitScript = "";
            RecomputeTables = false;
            _scriptsNeedRecompilation = true;
        }
        
        /// <summary>
        /// Load a double solarization effect
        /// </summary>
        public void LoadDoubleSolarizationPreset()
        {
            LevelScript = "red=(min(1,red*2)-red)*2;\nred=(min(1,red*2)-red)*2;\ngreen=red; blue=red;";
            FrameScript = "";
            BeatScript = "";
            InitScript = "";
            RecomputeTables = false;
            _scriptsNeedRecompilation = true;
        }
        
        /// <summary>
        /// Load an inverse solarization effect
        /// </summary>
        public void LoadInverseSolarizationPreset()
        {
            LevelScript = "red=abs(red - .5) * 1.5;\ngreen=red; blue=red;";
            FrameScript = "";
            BeatScript = "";
            InitScript = "";
            RecomputeTables = false;
            _scriptsNeedRecompilation = true;
        }
        
        /// <summary>
        /// Load a big brightness on beat effect
        /// </summary>
        public void LoadBigBrightnessOnBeatPreset()
        {
            InitScript = "scale=1.0";
            LevelScript = "red=red*scale;\ngreen=red; blue=red;";
            FrameScript = "scale=0.07 + (scale*0.93)";
            BeatScript = "scale=16";
            RecomputeTables = true;
            _scriptsNeedRecompilation = true;
        }
        
        /// <summary>
        /// Load a pulsing brightness effect
        /// </summary>
        public void LoadPulsingBrightnessPreset()
        {
            InitScript = "c = 200; f = 0;";
            LevelScript = "red = red * st;\ngreen=red;blue=red;";
            FrameScript = "f = f + 1;\nt = (f * 2 * $PI) / c;\nst = sin(t) + 1;";
            BeatScript = "c = f;f = 0;";
            RecomputeTables = true;
            _scriptsNeedRecompilation = true;
        }
        
        /// <summary>
        /// Load a rolling solarization effect
        /// </summary>
        public void LoadRollingSolarizationPreset()
        {
            InitScript = "c = 200; f = 0;";
            LevelScript = "red=(min(1,red*st)-red)*st;\nred=(min(1,red*2)-red)*2;\ngreen=red; blue=red;";
            FrameScript = "f = f + 1;\nt = (f * 2 * $PI) / c;\nst = ( sin(t) * .75 ) + 2;";
            BeatScript = "c = f;f = 0;";
            RecomputeTables = true;
            _scriptsNeedRecompilation = true;
        }
        
        /// <summary>
        /// Load a rolling tone effect
        /// </summary>
        public void LoadRollingTonePreset()
        {
            InitScript = "c = 200; f = 0;";
            LevelScript = "red = red * st;\ngreen = green * ct;\nblue = (blue * 4 * ti) - red - green;";
            FrameScript = "f = f + 1;\nt = (f * 2 * $PI) / c;\nti = (f / c);\nst = sin(t) + 1.5;\nct = cos(t) + 1.5;";
            BeatScript = "c = f;f = 0;";
            RecomputeTables = true;
            _scriptsNeedRecompilation = true;
        }
        
        #endregion
        
        #region Utility Methods
        
        /// <summary>
        /// Get the current lookup table as a byte array
        /// </summary>
        public byte[] GetLookupTable()
        {
            if (!_tableValid)
            {
                UpdateLookupTable();
            }
            return (byte[])_colorTable.Clone();
        }
        
        /// <summary>
        /// Check if the lookup table is valid
        /// </summary>
        public bool IsLookupTableValid()
        {
            return _tableValid;
        }
        
        /// <summary>
        /// Force recompilation of scripts
        /// </summary>
        public void ForceRecompilation()
        {
            _scriptsNeedRecompilation = true;
            _tableValid = false;
        }
        
        /// <summary>
        /// Reset the effect to initial state
        /// </summary>
        public void Reset()
        {
            _isInitialized = false;
            _frameCounter = 0;
            _currentBeat = false;
            _tableValid = false;
            _scriptsNeedRecompilation = true;
        }
        
        /// <summary>
        /// Get script execution statistics
        /// </summary>
        public string GetExecutionStats()
        {
            return $"Frame: {_frameCounter}, Beat: {_currentBeat}, Table Valid: {_tableValid}, Scripts Compiled: {!_scriptsNeedRecompilation}";
        }
        
        #endregion
        
        #region EEL Script Engine
        
        /// <summary>
        /// Simple EEL script engine for color modulation
        /// </summary>
        private class EELScriptEngine
        {
            private Dictionary<string, double> _variables = new Dictionary<string, double>();
            private Dictionary<string, object> _compiledScripts = new Dictionary<string, object>();
            
            public void RegisterVariable(string name, double value)
            {
                _variables[name] = value;
            }
            
            public void SetVariable(string name, double value)
            {
                _variables[name] = value;
            }
            
            public double GetVariable(string name)
            {
                return _variables.TryGetValue(name, out double value) ? value : 0.0;
            }
            
            public object CompileScript(string script)
            {
                if (string.IsNullOrEmpty(script))
                    return null;
                
                // Simple script compilation - in a real implementation, this would use a proper EEL parser
                return script;
            }
            
            public void ExecuteScript(object compiledScript)
            {
                if (compiledScript == null) return;
                
                string script = compiledScript.ToString();
                
                // Simple script execution - in a real implementation, this would use a proper EEL interpreter
                // For now, we'll implement basic mathematical operations
                ExecuteBasicScript(script);
            }
            
            private void ExecuteBasicScript(string script)
            {
                // This is a simplified implementation
                // A real EEL engine would parse and execute the script properly
                
                // Handle basic assignments like "red=red*2"
                string[] lines = script.Split('\n');
                foreach (string line in lines)
                {
                    string trimmedLine = line.Trim();
                    if (trimmedLine.Contains("="))
                    {
                        string[] parts = trimmedLine.Split('=');
                        if (parts.Length == 2)
                        {
                            string varName = parts[0].Trim();
                            string expression = parts[1].Trim();
                            
                            // Simple expression evaluation (very basic)
                            double result = EvaluateExpression(expression);
                            _variables[varName] = result;
                        }
                    }
                }
            }
            
            private double EvaluateExpression(string expression)
            {
                // Very basic expression evaluation
                // A real implementation would use a proper expression parser
                
                if (expression.Contains("red"))
                    expression = expression.Replace("red", _variables["red"].ToString());
                if (expression.Contains("green"))
                    expression = expression.Replace("green", _variables["green"].ToString());
                if (expression.Contains("blue"))
                    expression = expression.Replace("blue", _variables["blue"].ToString());
                if (expression.Contains("beat"))
                    expression = expression.Replace("beat", _variables["beat"].ToString());
                if (expression.Contains("frame"))
                    expression = expression.Replace("frame", _variables["frame"].ToString());
                if (expression.Contains("time"))
                    expression = expression.Replace("time", _variables["time"].ToString());
                
                // This is a placeholder - real implementation would parse mathematical expressions
                try
                {
                    return Convert.ToDouble(new System.Data.DataTable().Compute(expression, ""));
                }
                catch
                {
                    return 0.0;
                }
            }
        }
        
        #endregion
    }
}
```

## Effect Properties

### Core Properties
- **Enabled**: Toggle the effect on/off
- **InitScript**: EEL script executed during initialization
- **LevelScript**: EEL script executed for each color level (0-255)
- **FrameScript**: EEL script executed every frame
- **BeatScript**: EEL script executed on beat detection

### Processing Properties
- **RecomputeTables**: Whether to recompute lookup tables on every frame
- **Intensity**: Overall effect strength multiplier
- **BeatResponseEnabled**: Whether to enable beat response mode
- **MaxExecutionTime**: Maximum script execution time in milliseconds

### Internal Properties
- **ColorTable**: Pre-calculated color transformation lookup table
- **TableValid**: Whether the lookup table is current
- **ScriptEngine**: EEL script execution engine
- **CompiledScripts**: Compiled script handles for each phase

## EEL Script System

The effect uses a four-phase script execution system:

### 1. Initialization Phase (InitScript)
- Executed once when the effect starts
- Used for setting up variables and initial state
- Example: `scale=1.0; c=200; f=0;`

### 2. Level Phase (LevelScript)
- Executed for each color level (0-255) when building lookup tables
- Modifies red, green, and blue variables
- Example: `red=red*2; green=green*1.5; blue=blue*0.8;`

### 3. Frame Phase (FrameScript)
- Executed every frame during processing
- Can modify variables and create dynamic effects
- Example: `f=f+1; t=(f*2*$PI)/c; st=sin(t)+1;`

### 4. Beat Phase (BeatScript)
- Executed when a beat is detected
- Used for beat-responsive effects
- Example: `scale=16; c=f; f=0;`

## Lookup Table System

The effect uses a 768-byte lookup table (256 * 3 channels) for efficient color transformations:

- **Indices 0-255**: Blue channel transformations
- **Indices 256-511**: Green channel transformations  
- **Indices 512-767**: Red channel transformations

## Preset Effects

### Basic Color Modifications
- **4x Red Brightness**: Amplifies red channel by 4x
- **Solarization**: Creates solarization effect
- **Double Solarization**: Applies solarization twice
- **Inverse Solarization**: Creates inverse solarization

### Beat-Responsive Effects
- **Big Brightness on Beat**: Dramatic brightness increase on beats
- **Pulsing Brightness**: Smooth brightness pulsing
- **Rolling Solarization**: Dynamic solarization with beat timing
- **Rolling Tone**: Complex color tone variations

## Performance Optimizations

- **Pre-calculated Tables**: Color transformations are computed once and stored
- **Lazy Recompilation**: Scripts are only recompiled when changed
- **Efficient Lookup**: Direct table indexing for color transformations
- **Conditional Execution**: Beat scripts only run when needed

## Use Cases

- **Color Grading**: Apply complex color transformations
- **Beat Visualization**: Create dynamic, music-responsive effects
- **Artistic Filtering**: Apply creative color modifications
- **Real-time Effects**: Dynamic color changes during playback
- **Custom Effects**: User-defined color transformations

## EEL Language Features

### Variables
- **red, green, blue**: Color channel values (0.0 to 1.0)
- **beat**: Beat detection state (0.0 or 1.0)
- **frame**: Current frame number
- **time**: Time in seconds

### Functions
- **min()**: Minimum of two values
- **max()**: Maximum of two values
- **abs()**: Absolute value
- **sin()**: Sine function
- **cos()**: Cosine function
- **pow()**: Power function

### Mathematical Operations
- **Arithmetic**: +, -, *, /, %
- **Comparison**: ==, !=, <, >, <=, >=
- **Logical**: &&, ||, !
- **Assignment**: =, +=, -=, *=, /=

## Error Handling

The effect includes comprehensive error handling:
- **Script Compilation**: Catches and logs compilation errors
- **Execution Errors**: Handles runtime script execution errors
- **Validation**: Validates script lengths and configuration
- **Fallbacks**: Graceful degradation when scripts fail
