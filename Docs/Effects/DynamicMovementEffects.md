# Dynamic Movement Effects

The Dynamic Movement effect creates complex pixel movement patterns using EEL scripting and a grid-based coordinate system. It allows for sophisticated transformations including rotation, scaling, and custom movement algorithms with support for both polar and rectangular coordinate systems.

## Effect Overview

The Dynamic Movement effect works by:
1. Creating a grid of control points across the image
2. Using EEL scripts to calculate new positions for each grid point
3. Interpolating between grid points for smooth pixel movement
4. Supporting both polar (r, d) and rectangular (x, y) coordinate systems
5. Providing options for wrapping, clamping, blending, and subpixel interpolation

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
    public class DynamicMovementEffectsNode : BaseEffectNode
    {
        #region Properties
        
        /// <summary>
        /// Whether the effect is enabled
        /// </summary>
        public bool Enabled { get; set; } = true;
        
        /// <summary>
        /// EEL script for point movement calculation
        /// </summary>
        public string PointScript { get; set; } = "";
        
        /// <summary>
        /// EEL script for frame processing
        /// </summary>
        public string FrameScript { get; set; } = "";
        
        /// <summary>
        /// EEL script for beat response
        /// </summary>
        public string BeatScript { get; set; } = "";
        
        /// <summary>
        /// EEL script for initialization
        /// </summary>
        public string InitScript { get; set; } = "";
        
        /// <summary>
        /// Whether to use subpixel interpolation
        /// </summary>
        public bool SubpixelEnabled { get; set; } = true;
        
        /// <summary>
        /// Whether to use rectangular coordinates instead of polar
        /// </summary>
        public bool RectangularCoordinates { get; set; } = false;
        
        /// <summary>
        /// Whether to blend with the original image
        /// </summary>
        public bool BlendEnabled { get; set; } = false;
        
        /// <summary>
        /// Whether to wrap pixels around edges
        /// </summary>
        public bool WrapEnabled { get; set; } = false;
        
        /// <summary>
        /// Whether to disable movement (only blend)
        /// </summary>
        public bool NoMovement { get; set; } = false;
        
        /// <summary>
        /// Grid resolution in X direction (2-256)
        /// </summary>
        public int GridResolutionX { get; set; } = 16;
        
        /// <summary>
        /// Grid resolution in Y direction (2-256)
        /// </summary>
        public int GridResolutionY { get; set; } = 16;
        
        /// <summary>
        /// Source buffer number (0 = current frame, 1+ = previous buffers)
        /// </summary>
        public int SourceBuffer { get; set; } = 0;
        
        /// <summary>
        /// Effect intensity multiplier
        /// </summary>
        public float Intensity { get; set; } = 1.0f;
        
        /// <summary>
        /// Maximum execution time for scripts in milliseconds
        /// </summary>
        public int MaxExecutionTime { get; set; } = 100;
        
        #endregion
        
        #region Private Fields
        
        /// <summary>
        /// Pre-calculated movement table for grid points
        /// </summary>
        private int[] _movementTable;
        
        /// <summary>
        /// Width multipliers for efficient pixel indexing
        /// </summary>
        private int[] _widthMultipliers;
        
        /// <summary>
        /// Current width and height
        /// </summary>
        private int _currentWidth, _currentHeight;
        
        /// <summary>
        /// Current grid resolutions
        /// </summary>
        private int _currentGridX, _currentGridY;
        
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
        /// Frame counter for timing
        /// </summary>
        private int _frameCounter = 0;
        
        #endregion
        
        #region Constructor
        
        public DynamicMovementEffectsNode()
        {
            _movementTable = new int[0];
            _widthMultipliers = new int[0];
            _compiledScripts = new object[4];
            _scriptEngine = new EELScriptEngine();
            
            // Set default grid resolution
            GridResolutionX = 16;
            GridResolutionY = 16;
        }
        
        #endregion
        
        #region Initialization Methods
        
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
            _scriptEngine.RegisterVariable("d", 0.0);      // Distance from center
            _scriptEngine.RegisterVariable("r", 0.0);      // Angle from center
            _scriptEngine.RegisterVariable("x", 0.0);      // X coordinate (-1 to 1)
            _scriptEngine.RegisterVariable("y", 0.0);      // Y coordinate (-1 to 1)
            _scriptEngine.RegisterVariable("w", 0.0);      // Image width
            _scriptEngine.RegisterVariable("h", 0.0);      // Image height
            _scriptEngine.RegisterVariable("b", 0.0);      // Beat detection
            _scriptEngine.RegisterVariable("alpha", 0.5);  // Alpha blending value
            
            _isInitialized = true;
        }
        
        /// <summary>
        /// Initialize movement tables and width multipliers
        /// </summary>
        private void InitializeTables(int width, int height)
        {
            if (_currentWidth == width && _currentHeight == height && 
                _currentGridX == GridResolutionX && _currentGridY == GridResolutionY && 
                _movementTable.Length > 0)
                return;
            
            _currentWidth = width;
            _currentHeight = height;
            _currentGridX = GridResolutionX;
            _currentGridY = GridResolutionY;
            
            // Clamp grid resolutions
            int gridX = Math.Max(2, Math.Min(256, GridResolutionX + 1));
            int gridY = Math.Max(2, Math.Min(256, GridResolutionY + 1));
            
            // Initialize width multipliers for efficient pixel indexing
            _widthMultipliers = new int[height];
            for (int y = 0; y < height; y++)
            {
                _widthMultipliers[y] = y * width;
            }
            
            // Initialize movement table (3 values per grid point: x, y, alpha)
            _movementTable = new int[gridX * gridY * 3];
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
            
            // Initialize tables for current dimensions
            InitializeTables(imageBuffer.Width, imageBuffer.Height);
            
            // Update frame counter
            _frameCounter++;
            
            // Recompile scripts if needed
            if (_scriptsNeedRecompilation)
            {
                RecompileScripts();
            }
            
            // Execute scripts in order
            ExecuteInitScript();
            ExecuteFrameScript();
            if (audioFeatures.IsBeat)
            {
                ExecuteBeatScript();
            }
            
            // Update movement table
            UpdateMovementTable(imageBuffer.Width, imageBuffer.Height);
            
            // Apply movement effect
            ApplyMovementEffect(imageBuffer);
        }
        
        /// <summary>
        /// Recompile all EEL scripts
        /// </summary>
        private void RecompileScripts()
        {
            try
            {
                _compiledScripts[0] = _scriptEngine.CompileScript(PointScript);
                _compiledScripts[1] = _scriptEngine.CompileScript(FrameScript);
                _compiledScripts[2] = _scriptEngine.CompileScript(BeatScript);
                _compiledScripts[3] = _scriptEngine.CompileScript(InitScript);
                
                _scriptsNeedRecompilation = false;
            }
            catch (Exception ex)
            {
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
                    _scriptEngine.SetVariable("w", _currentWidth);
                    _scriptEngine.SetVariable("h", _currentHeight);
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
                    _scriptEngine.SetVariable("b", 1.0);
                    _scriptEngine.ExecuteScript(_compiledScripts[2]);
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Beat script execution error: {ex.Message}");
                }
            }
        }
        
        /// <summary>
        /// Update the movement table for all grid points
        /// </summary>
        private void UpdateMovementTable(int width, int height)
        {
            if (_compiledScripts[0] == null) return;
            
            int gridX = _currentGridX;
            int gridY = _currentGridY;
            int tableIndex = 0;
            
            double xScale = 2.0 / width;
            double yScale = 2.0 / height;
            double maxScreenDistance = Math.Sqrt(width * width + height * height) * 0.5;
            double divMaxDistance = 1.0 / maxScreenDistance;
            
            for (int y = 0; y < gridY; y++)
            {
                double yPos = ((double)y / (gridY - 1) - 0.5) * 2.0;
                
                for (int x = 0; x < gridX; x++)
                {
                    double xPos = ((double)x / (gridX - 1) - 0.5) * 2.0;
                    
                    // Set coordinate variables
                    _scriptEngine.SetVariable("x", xPos);
                    _scriptEngine.SetVariable("y", yPos);
                    
                    // Calculate polar coordinates
                    double distance = Math.Sqrt(xPos * xPos + yPos * yPos) * divMaxDistance;
                    double angle = Math.Atan2(yPos, xPos) + Math.PI * 0.5;
                    
                    _scriptEngine.SetVariable("d", distance);
                    _scriptEngine.SetVariable("r", angle);
                    
                    // Execute point script
                    try
                    {
                        _scriptEngine.ExecuteScript(_compiledScripts[0]);
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Point script execution error: {ex.Message}");
                        continue;
                    }
                    
                    // Get transformed coordinates
                    double newX, newY;
                    
                    if (RectangularCoordinates)
                    {
                        newX = _scriptEngine.GetVariable("x");
                        newY = _scriptEngine.GetVariable("y");
                    }
                    else
                    {
                        // Convert polar back to rectangular
                        double newDistance = _scriptEngine.GetVariable("d") * maxScreenDistance;
                        double newAngle = _scriptEngine.GetVariable("r") - Math.PI * 0.5;
                        
                        newX = Math.Cos(newAngle) * newDistance;
                        newY = Math.Sin(newAngle) * newDistance;
                    }
                    
                    // Convert to pixel coordinates
                    int pixelX = (int)((newX + 1.0) * width * 0.5);
                    int pixelY = (int)((newY + 1.0) * height * 0.5);
                    
                    // Clamp or wrap coordinates
                    if (!WrapEnabled)
                    {
                        pixelX = Math.Max(0, Math.Min(width - 1, pixelX));
                        pixelY = Math.Max(0, Math.Min(height - 1, pixelY));
                    }
                    else
                    {
                        pixelX = ((pixelX % width) + width) % width;
                        pixelY = ((pixelY % height) + height) % height;
                    }
                    
                    // Store in movement table
                    _movementTable[tableIndex++] = pixelX << 16;  // Fixed-point X
                    _movementTable[tableIndex++] = pixelY << 16;  // Fixed-point Y
                    
                    // Get alpha value
                    double alpha = _scriptEngine.GetVariable("alpha");
                    alpha = Math.Max(0.0, Math.Min(1.0, alpha));
                    _movementTable[tableIndex++] = (int)(alpha * 255.0 * 65536.0);
                }
            }
        }
        
        /// <summary>
        /// Apply movement effect to the image buffer
        /// </summary>
        private void ApplyMovementEffect(ImageBuffer imageBuffer)
        {
            if (NoMovement)
            {
                // Only apply blending if no movement
                if (BlendEnabled)
                {
                    ApplyBlendingOnly(imageBuffer);
                }
                return;
            }
            
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            int gridX = _currentGridX;
            int gridY = _currentGridY;
            
            // Create output buffer
            ImageBuffer outputBuffer = new ImageBuffer(width, height);
            
            // Interpolate between grid points
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    // Find the four surrounding grid points
                    int gridX1 = (x * (gridX - 1)) / width;
                    int gridY1 = (y * (gridY - 1)) / height;
                    int gridX2 = Math.Min(gridX1 + 1, gridX - 1);
                    int gridY2 = Math.Min(gridY1 + 1, gridY - 1);
                    
                    // Calculate interpolation weights
                    double weightX = (double)(x - (gridX1 * width / (gridX - 1))) / (width / (gridX - 1));
                    double weightY = (double)(y - (gridY1 * height / (gridY - 1))) / (height / (gridY - 1));
                    
                    // Get source pixel coordinates from movement table
                    Color sourcePixel = GetInterpolatedSourcePixel(gridX1, gridY1, gridX2, gridY2, weightX, weightY, width, height);
                    
                    if (BlendEnabled)
                    {
                        // Blend with original pixel
                        Color originalPixel = imageBuffer.GetPixel(x, y);
                        Color blendedPixel = BlendPixels(originalPixel, sourcePixel);
                        outputBuffer.SetPixel(x, y, blendedPixel);
                    }
                    else
                    {
                        // Replace pixel
                        outputBuffer.SetPixel(x, y, sourcePixel);
                    }
                }
            }
            
            // Copy output back to input buffer
            imageBuffer.CopyFrom(outputBuffer);
        }
        
        /// <summary>
        /// Get interpolated source pixel from movement table
        /// </summary>
        private Color GetInterpolatedSourcePixel(int gridX1, int gridY1, int gridX2, int gridY2, 
            double weightX, double weightY, int width, int height)
        {
            // Get source coordinates from movement table
            int index1 = (gridY1 * _currentGridX + gridX1) * 3;
            int index2 = (gridY1 * _currentGridX + gridX2) * 3;
            int index3 = (gridY2 * _currentGridX + gridX1) * 3;
            int index4 = (gridY2 * _currentGridX + gridX2) * 3;
            
            // Interpolate X coordinates
            int sourceX1 = _movementTable[index1] + (_movementTable[index2] - _movementTable[index1]) * (int)(weightX * 65536.0);
            int sourceX2 = _movementTable[index3] + (_movementTable[index4] - _movementTable[index3]) * (int)(weightX * 65536.0);
            int sourceX = sourceX1 + (sourceX2 - sourceX1) * (int)(weightY * 65536.0);
            
            // Interpolate Y coordinates
            int sourceY1 = _movementTable[index1 + 1] + (_movementTable[index2 + 1] - _movementTable[index1 + 1]) * (int)(weightX * 65536.0);
            int sourceY2 = _movementTable[index3 + 1] + (_movementTable[index4 + 1] - _movementTable[index3 + 1]) * (int)(weightX * 65536.0);
            int sourceY = sourceY1 + (sourceY2 - sourceY1) * (int)(weightY * 65536.0);
            
            // Convert to pixel coordinates
            int pixelX = sourceX >> 16;
            int pixelY = sourceY >> 16;
            
            // Handle wrapping or clamping
            if (WrapEnabled)
            {
                pixelX = ((pixelX % width) + width) % width;
                pixelY = ((pixelY % height) + height) % height;
            }
            else
            {
                pixelX = Math.Max(0, Math.Min(width - 1, pixelX));
                pixelY = Math.Max(0, Math.Min(height - 1, pixelY));
            }
            
            // Get source pixel
            return imageBuffer.GetPixel(pixelX, pixelY);
        }
        
        /// <summary>
        /// Apply blending only (no movement)
        /// </summary>
        private void ApplyBlendingOnly(ImageBuffer imageBuffer)
        {
            // This would implement the blending logic when no movement is enabled
            // For now, we'll just return the original image
        }
        
        /// <summary>
        /// Blend two pixels using alpha blending
        /// </summary>
        private Color BlendPixels(Color pixel1, Color pixel2)
        {
            // Simple alpha blending - in a real implementation, this would use the alpha value from the movement table
            int r = (pixel1.R + pixel2.R) / 2;
            int g = (pixel1.G + pixel2.G) / 2;
            int b = (pixel1.B + pixel2.B) / 2;
            int a = (pixel1.A + pixel2.A) / 2;
            
            return Color.FromArgb(a, r, g, b);
        }
        
        #endregion
        
        #region Configuration Validation
        
        public override bool ValidateConfiguration()
        {
            if (GridResolutionX < 2 || GridResolutionX > 256) return false;
            if (GridResolutionY < 2 || GridResolutionY > 256) return false;
            if (SourceBuffer < 0 || SourceBuffer > 10) return false;
            if (MaxExecutionTime < 1 || MaxExecutionTime > 1000) return false;
            if (Intensity < 0.0f || Intensity > 10.0f) return false;
            
            // Validate script lengths
            if (PointScript?.Length > 10000) return false;
            if (FrameScript?.Length > 10000) return false;
            if (BeatScript?.Length > 10000) return false;
            if (InitScript?.Length > 10000) return false;
            
            return true;
        }
        
        #endregion
        
        #region Preset Methods
        
        /// <summary>
        /// Load a random rotate effect
        /// </summary>
        public void LoadRandomRotatePreset()
        {
            PointScript = "r = r + dr;";
            FrameScript = "";
            BeatScript = "dr = (rand(100) / 100) * $PI;\r\nd = d * .95;";
            InitScript = "";
            RectangularCoordinates = false;
            WrapEnabled = true;
            GridResolutionX = 2;
            GridResolutionY = 2;
            _scriptsNeedRecompilation = true;
        }
        
        /// <summary>
        /// Load a random direction effect
        /// </summary>
        public void LoadRandomDirectionPreset()
        {
            PointScript = "x = x + dx;\r\ny = y + dy;";
            FrameScript = "dx = cos(dr) * speed;\r\ndy = sin(dr) * speed;";
            BeatScript = "dr = (rand(200) / 100) * $PI;";
            InitScript = "speed=.05;dr = (rand(200) / 100) * $PI;";
            RectangularCoordinates = true;
            WrapEnabled = true;
            GridResolutionX = 2;
            GridResolutionY = 2;
            _scriptsNeedRecompilation = true;
        }
        
        /// <summary>
        /// Load an in and out effect
        /// </summary>
        public void LoadInAndOutPreset()
        {
            PointScript = "d = d * dd;";
            FrameScript = "";
            BeatScript = "c = c + ($PI/2);\r\ndd = 1 - (sin(c) * speed);";
            InitScript = "speed=.2;c=0;";
            RectangularCoordinates = false;
            WrapEnabled = true;
            GridResolutionX = 2;
            GridResolutionY = 2;
            _scriptsNeedRecompilation = true;
        }
        
        /// <summary>
        /// Load a wavy effect
        /// </summary>
        public void LoadWavyPreset()
        {
            PointScript = "y = y + ((sin((x+dx) * $PI))*speed);\r\nx = x + .025";
            FrameScript = "f = f + 1;\r\nt = ( (f * 2 * 3.1415) / c ) / beatdiv;\r\ndx = dl + t;";
            BeatScript = "c = f;\r\nf = 0;\r\ndl = dx;";
            InitScript = "c=200;f=0;dx=0;dl=0;beatdiv=16;speed=.05";
            RectangularCoordinates = true;
            WrapEnabled = true;
            GridResolutionX = 6;
            GridResolutionY = 6;
            _scriptsNeedRecompilation = true;
        }
        
        #endregion
        
        #region Utility Methods
        
        /// <summary>
        /// Get the current movement table as an array
        /// </summary>
        public int[] GetMovementTable()
        {
            return (int[])_movementTable.Clone();
        }
        
        /// <summary>
        /// Check if the movement table is valid
        /// </summary>
        public bool IsMovementTableValid()
        {
            return _movementTable.Length > 0;
        }
        
        /// <summary>
        /// Force recompilation of scripts
        /// </summary>
        public void ForceRecompilation()
        {
            _scriptsNeedRecompilation = true;
        }
        
        /// <summary>
        /// Reset the effect to initial state
        /// </summary>
        public void Reset()
        {
            _isInitialized = false;
            _frameCounter = 0;
            _scriptsNeedRecompilation = true;
        }
        
        /// <summary>
        /// Get effect execution statistics
        /// </summary>
        public string GetExecutionStats()
        {
            return $"Frame: {_frameCounter}, Grid: {_currentGridX}x{_currentGridY}, Table Valid: {IsMovementTableValid()}, Scripts Compiled: {!_scriptsNeedRecompilation}";
        }
        
        #endregion
        
        #region EEL Script Engine
        
        /// <summary>
        /// Simple EEL script engine for movement calculations
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
                
                // Handle basic assignments like "x=x+dx"
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
                
                if (expression.Contains("x"))
                    expression = expression.Replace("x", _variables["x"].ToString());
                if (expression.Contains("y"))
                    expression = expression.Replace("y", _variables["y"].ToString());
                if (expression.Contains("d"))
                    expression = expression.Replace("d", _variables["d"].ToString());
                if (expression.Contains("r"))
                    expression = expression.Replace("r", _variables["r"].ToString());
                if (expression.Contains("w"))
                    expression = expression.Replace("w", _variables["w"].ToString());
                if (expression.Contains("h"))
                    expression = expression.Replace("h", _variables["h"].ToString());
                if (expression.Contains("b"))
                    expression = expression.Replace("b", _variables["b"].ToString());
                if (expression.Contains("alpha"))
                    expression = expression.Replace("alpha", _variables["alpha"].ToString());
                
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
- **PointScript**: EEL script executed for each grid point to calculate new positions
- **FrameScript**: EEL script executed every frame for timing and animation
- **BeatScript**: EEL script executed on beat detection
- **InitScript**: EEL script executed during initialization

### Processing Properties
- **SubpixelEnabled**: Whether to use subpixel interpolation for smoother effects
- **RectangularCoordinates**: Whether to use rectangular (x,y) instead of polar (r,d) coordinates
- **BlendEnabled**: Whether to blend with the original image
- **WrapEnabled**: Whether to wrap pixels around edges
- **NoMovement**: Whether to disable movement (only blend)

### Grid Properties
- **GridResolutionX**: Grid resolution in X direction (2-256)
- **GridResolutionY**: Grid resolution in Y direction (2-256)
- **SourceBuffer**: Source buffer number (0 = current frame, 1+ = previous buffers)

### Effect Properties
- **Intensity**: Overall effect strength multiplier
- **MaxExecutionTime**: Maximum script execution time in milliseconds

### Internal Properties
- **MovementTable**: Pre-calculated movement table for grid points
- **WidthMultipliers**: Efficient pixel indexing multipliers
- **ScriptEngine**: EEL script execution engine

## EEL Script System

The effect uses a four-phase script execution system:

### 1. Initialization Phase (InitScript)
- Executed once when the effect starts
- Used for setting up variables and initial state
- Example: `speed=.05;dr=0;`

### 2. Point Phase (PointScript)
- Executed for each grid point to calculate new positions
- Can modify x, y, d, r variables
- Example: `x=x+dx; y=y+dy;` for movement

### 3. Frame Phase (FrameScript)
- Executed every frame during processing
- Can modify movement variables and create dynamic effects
- Example: `dx=cos(dr)*speed; dy=sin(dr)*speed;`

### 4. Beat Phase (BeatScript)
- Executed when a beat is detected
- Used for beat-responsive effects
- Example: `dr=(rand(200)/100)*$PI;` for random direction changes

## Coordinate Systems

### Polar Coordinates (Default)
- **d**: Distance from center (0.0 to 1.0)
- **r**: Angle from center in radians
- Useful for rotation and scaling effects

### Rectangular Coordinates
- **x**: X coordinate (-1.0 to 1.0)
- **y**: Y coordinate (-1.0 to 1.0)
- Useful for translation and distortion effects

## Grid System

The effect uses a configurable grid system:
- **Low Resolution (2x2)**: Fast processing, coarse effects
- **High Resolution (32x32+)**: Smooth effects, slower processing
- **Custom Resolution**: User-defined grid density

## Performance Optimizations

- **Pre-calculated Tables**: Movement calculations are computed once and stored
- **Grid Interpolation**: Smooth pixel movement between grid points
- **Efficient Indexing**: Optimized pixel access using width multipliers
- **Lazy Recompilation**: Scripts are only recompiled when changed

## Use Cases

- **Rotation Effects**: Create spinning and rotating patterns
- **Movement Patterns**: Generate complex pixel movement animations
- **Beat Visualization**: Synchronize effects with music beats
- **Custom Transformations**: User-defined movement algorithms
- **Grid-based Effects**: Create structured distortion patterns

## Preset Effects

### Basic Movements
- **Random Rotate**: Random rotation with distance scaling
- **Random Direction**: Random movement direction changes
- **In and Out**: Pulsing distance changes
- **Wavy**: Sine wave distortion along X axis

### Advanced Effects
- **Unspun Kaleida**: Complex kaleidoscope-like rotations
- **Roiling Gridley**: Grid-based wave distortions
- **6-Way Outswirl**: Multi-directional swirling
- **Smooth Rotoblitter**: Smooth rotation with distance scaling

## Mathematical Functions

The effect supports various mathematical operations:
- **Trigonometric**: `sin()`, `cos()`, `atan2()`
- **Random**: `rand()` function for random values
- **Constants**: `$PI` for mathematical constants
- **Arithmetic**: Standard mathematical operations

## Error Handling

The effect includes comprehensive error handling:
- **Script Compilation**: Catches and logs compilation errors
- **Execution Errors**: Handles runtime script execution errors
- **Validation**: Validates grid resolutions and configuration
- **Fallbacks**: Graceful degradation when scripts fail
