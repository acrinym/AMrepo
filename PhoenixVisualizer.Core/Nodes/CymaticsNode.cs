using System;
using System.Collections.Generic;
using System.Numerics;

namespace PhoenixVisualizer.Core.Nodes;

/// <summary>
/// Cymatics Visualizer - Replicates vibrational patterns in different materials
/// Based on Earth harmonics, Solfeggio frequencies, and sacred geometry
/// </summary>
public class CymaticsNode : IEffectNode
{
    // Material properties for different substances
    private enum MaterialType
    {
        Water,      // Liquid - fluid dynamics, ripples
        Sand,       // Granular - geometric patterns
        Salt,       // Crystalline - sharp, angular forms
        Metal,      // Conductive - electromagnetic patterns
        Air,        // Gaseous - wave interference
        Plasma      // Ionized - complex field patterns
    }

    // Solfeggio frequency database
    private static readonly Dictionary<string, (float Hz, string Note, string Meaning)> SolfeggioFrequencies = new()
    {
        ["UT"] = (396f, "G#", "Liberation from guilt and fear"),
        ["RE"] = (417f, "G#", "Undoing situations and facilitating change"),
        ["MI"] = (528f, "C", "Transformation and miracles"),
        ["FA"] = (639f, "D#", "Connecting relationships"),
        ["SOL"] = (741f, "F#", "Awakening intuition"),
        ["LA"] = (852f, "G#", "Spiritual order")
    };

    // Earth harmonics from the research
    private static readonly Dictionary<string, (float Hz, string Note, string Description)> EarthHarmonics = new()
    {
        ["B-flat"] = (14.4f, "Bb", "Base Earth frequency"),
        ["F"] = (10.8f, "F", "5th harmonic of Earth"),
        ["F#"] = (11.377f, "F#", "3rd harmonic of Earth"),
        ["E"] = (20.222f, "E", "Higher harmonic"),
        ["G"] = (192f, "G", "Octave harmonic"),
        ["C"] = (256f, "C", "Octave harmonic")
    };

    // Lost Solfeggio frequencies
    private static readonly Dictionary<string, (float Hz, string Note)> LostSolfeggio = new()
    {
        ["E#"] = (83.437037f, "E#"),
        ["Gb#"] = (93.8666f, "Gb#"),
        ["Db#"] = (140.8f, "Db#"),
        ["Ab#"] = (105.6f, "Ab#")
    };

    private MaterialType _currentMaterial = MaterialType.Water;
    private float _currentFrequency = 432f; // A 432 Hz - Earth's natural tuning
    private float _materialDensity = 1.0f;
    private float _temperature = 20f; // Celsius
    private float _pressure = 1.0f; // Atmospheric
    private bool _showHarmonicSeries = true;
    private bool _showSolfeggioOverlay = true;
    private float _patternComplexity = 1.0f;
    private float _animationSpeed = 1.0f;
    private string _selectedFrequency = "432";

    public string Name => "Cymatics Visualizer";
    public Dictionary<string, EffectParam> Params { get; } = new()
    {
        ["frequency"] = new EffectParam {
            Label = "Frequency (Hz)",
            Type = "dropdown",
            StringValue = "432",
            Options = new() { 
                "432", "396", "417", "528", "639", "741", "852", // Solfeggio
                "14.4", "10.8", "11.377", "20.222", "192", "256", // Earth Harmonics
                "83.437", "93.867", "140.8", "105.6", // Lost Solfeggio
                "custom"
            }
        },
        ["customFreq"] = new EffectParam {
            Label = "Custom Frequency",
            Type = "slider",
            Min = 1,
            Max = 1000,
            FloatValue = 432f
        },
        ["material"] = new EffectParam {
            Label = "Material",
            Type = "dropdown",
            StringValue = "water",
            Options = new() { "water", "sand", "salt", "metal", "air", "plasma" }
        },
        ["density"] = new EffectParam {
            Label = "Material Density",
            Type = "slider",
            Min = 0.1f,
            Max = 10f,
            FloatValue = 1f
        },
        ["temperature"] = new EffectParam {
            Label = "Temperature (°C)",
            Type = "slider",
            Min = -50,
            Max = 200,
            FloatValue = 20f
        },
        ["pressure"] = new EffectParam {
            Label = "Pressure (atm)",
            Type = "slider",
            Min = 0.1f,
            Max = 10f,
            FloatValue = 1f
        },
        ["complexity"] = new EffectParam {
            Label = "Pattern Complexity",
            Type = "slider",
            Min = 0.1f,
            Max = 3f,
            FloatValue = 1f
        },
        ["animation"] = new EffectParam {
            Label = "Animation Speed",
            Type = "slider",
            Min = 0.1f,
            Max = 5f,
            FloatValue = 1f
        },
        ["harmonics"] = new EffectParam {
            Label = "Show Harmonic Series",
            Type = "checkbox",
            BoolValue = true
        },
        ["solfeggio"] = new EffectParam {
            Label = "Show Solfeggio Overlay",
            Type = "checkbox",
            BoolValue = true
        },
        ["baseColor"] = new EffectParam {
            Label = "Base Color",
            Type = "color",
            ColorValue = "#0066CC"
        }
    };

    public void Render(float[] waveform, float[] spectrum, RenderContext ctx)
    {
        UpdateParameters();
        var pattern = GenerateCymaticPattern(ctx);
        RenderPattern(pattern, ctx);
        
        if (_showHarmonicSeries)
            RenderHarmonicSeries(ctx);
        
        if (_showSolfeggioOverlay)
            RenderSolfeggioOverlay(ctx);
    }

    private void UpdateParameters()
    {
        _selectedFrequency = Params["frequency"].StringValue;
        _currentMaterial = ParseMaterial(Params["material"].StringValue);
        _materialDensity = Params["density"].FloatValue;
        _temperature = Params["temperature"].FloatValue;
        _pressure = Params["pressure"].FloatValue;
        _patternComplexity = Params["complexity"].FloatValue;
        _animationSpeed = Params["animation"].FloatValue;
        _showHarmonicSeries = Params["harmonics"].BoolValue;
        _showSolfeggioOverlay = Params["solfeggio"].BoolValue;

        // Parse frequency
        if (_selectedFrequency == "custom")
        {
            _currentFrequency = Params["customFreq"].FloatValue;
        }
        else if (float.TryParse(_selectedFrequency, out float freq))
        {
            _currentFrequency = freq;
        }
        else
        {
            _currentFrequency = 432f; // Default to A 432 Hz
        }
    }

    private MaterialType ParseMaterial(string material)
    {
        return material switch
        {
            "water" => MaterialType.Water,
            "sand" => MaterialType.Sand,
            "salt" => MaterialType.Salt,
            "metal" => MaterialType.Metal,
            "air" => MaterialType.Air,
            "plasma" => MaterialType.Plasma,
            _ => MaterialType.Water
        };
    }

    private CymaticPattern GenerateCymaticPattern(RenderContext ctx)
    {
        var pattern = new CymaticPattern
        {
            Frequency = _currentFrequency,
            Material = _currentMaterial,
            Width = ctx.Width,
            Height = ctx.Height,
            Time = ctx.Time * _animationSpeed
        };

        // Calculate wavelength based on material properties
        float wavelength = CalculateWavelength(_currentFrequency, _currentMaterial, _materialDensity, _temperature, _pressure);
        pattern.Wavelength = wavelength;

        // Generate nodal points (points of maximum displacement)
        pattern.NodalPoints = GenerateNodalPoints(ctx, wavelength, _patternComplexity);

        // Generate antinodal lines (lines of maximum displacement)
        pattern.AntinodalLines = GenerateAntinodalLines(ctx, wavelength, _patternComplexity);

        // Generate material-specific patterns
        switch (_currentMaterial)
        {
            case MaterialType.Water:
                pattern.FluidPatterns = GenerateWaterPatterns(ctx, wavelength, _patternComplexity);
                break;
            case MaterialType.Sand:
                pattern.GranularPatterns = GenerateSandPatterns(ctx, wavelength, _patternComplexity);
                break;
            case MaterialType.Salt:
                pattern.CrystallinePatterns = GenerateSaltPatterns(ctx, wavelength, _patternComplexity);
                break;
            case MaterialType.Metal:
                pattern.ElectromagneticPatterns = GenerateMetalPatterns(ctx, wavelength, _patternComplexity);
                break;
            case MaterialType.Air:
                pattern.WaveInterference = GenerateAirPatterns(ctx, wavelength, _patternComplexity);
                break;
            case MaterialType.Plasma:
                pattern.PlasmaFields = GeneratePlasmaPatterns(ctx, wavelength, _patternComplexity);
                break;
        }

        return pattern;
    }

    private float CalculateWavelength(float frequency, MaterialType material, float density, float temperature, float pressure)
    {
        // Speed of sound in different materials at given conditions
        float speedOfSound = material switch
        {
            MaterialType.Water => 1482f + (temperature - 20f) * 2.5f, // m/s
            MaterialType.Sand => 200f + density * 100f, // Granular medium
            MaterialType.Salt => 4600f, // Crystalline solid
            MaterialType.Metal => 5000f + density * 1000f, // Varies by metal
            MaterialType.Air => 331.3f + (temperature * 0.6f), // m/s
            MaterialType.Plasma => 10000f + pressure * 1000f, // Ionized gas
            _ => 343f // Default to air
        };

        // Adjust for pressure and density effects
        speedOfSound *= (float)Math.Sqrt(pressure / density);
        
        // Wavelength = speed / frequency
        return speedOfSound / frequency;
    }

    private List<Vector2> GenerateNodalPoints(RenderContext ctx, float wavelength, float complexity)
    {
        var points = new List<Vector2>();
        
        // Calculate grid spacing based on wavelength
        float gridSpacing = wavelength * complexity;
        
        // Generate nodal points in a grid pattern
        for (float x = 0; x < ctx.Width; x += gridSpacing)
        {
            for (float y = 0; y < ctx.Height; y += gridSpacing)
            {
                // Add some randomness based on complexity
                float offsetX = (float)(Math.Sin(x * 0.01f) * complexity * 10);
                float offsetY = (float)(Math.Cos(y * 0.01f) * complexity * 10);
                
                points.Add(new Vector2(x + offsetX, y + offsetY));
            }
        }
        
        return points;
    }

    private List<Vector2[]> GenerateAntinodalLines(RenderContext ctx, float wavelength, float complexity)
    {
        var lines = new List<Vector2[]>();
        
        // Generate antinodal lines (lines of maximum displacement)
        float lineSpacing = wavelength * complexity * 0.5f;
        
        // Horizontal lines
        for (float y = 0; y < ctx.Height; y += lineSpacing)
        {
            lines.Add(new Vector2[] { new(0, y), new(ctx.Width, y) });
        }
        
        // Vertical lines
        for (float x = 0; x < ctx.Width; x += lineSpacing)
        {
            lines.Add(new Vector2[] { new(x, 0), new(x, ctx.Height) });
        }
        
        // Diagonal lines for complexity
        if (complexity > 1.5f)
        {
            for (int i = 0; i < 5; i++)
            {
                float angle = i * MathF.PI / 5;
                float x1 = 0, y1 = 0, x2 = ctx.Width, y2 = ctx.Height;
                
                if (angle > MathF.PI / 2)
                {
                    x1 = ctx.Width;
                    x2 = 0;
                }
                
                lines.Add(new Vector2[] { new(x1, y1), new(x2, y2) });
            }
        }
        
        return lines;
    }

    private List<FluidPattern> GenerateWaterPatterns(RenderContext ctx, float wavelength, float complexity)
    {
        var patterns = new List<FluidPattern>();
        
        // Generate Chladni plate patterns for water
        float time = ctx.Time;
        
        for (int i = 0; i < (int)(complexity * 10); i++)
        {
            float radius = wavelength * (i + 1) * 0.5f;
            float centerX = ctx.Width * 0.5f + (float)(Math.Sin(time + i) * 20);
            float centerY = ctx.Height * 0.5f + (float)(Math.Cos(time + i) * 20);
            
            patterns.Add(new FluidPattern
            {
                Type = "ripple",
                Center = new Vector2(centerX, centerY),
                Radius = radius,
                Amplitude = (float)(Math.Sin(time * 2 + i) * 0.5 + 0.5),
                Frequency = _currentFrequency * (i + 1)
            });
        }
        
        return patterns;
    }

    private List<GranularPattern> GenerateSandPatterns(RenderContext ctx, float wavelength, float complexity)
    {
        var patterns = new List<GranularPattern>();
        
        // Generate geometric patterns for granular materials
        float time = ctx.Time;
        
        for (int i = 0; i < (int)(complexity * 8); i++)
        {
            float size = wavelength * (i + 1) * 0.3f;
            float x = ctx.Width * 0.5f + (float)(Math.Sin(time * 0.5f + i) * 100);
            float y = ctx.Height * 0.5f + (float)(Math.Cos(time * 0.5f + i) * 100);
            
            patterns.Add(new GranularPattern
            {
                Type = "geometric",
                Position = new Vector2(x, y),
                Size = size,
                Rotation = time + i,
                Sides = 3 + (i % 5) // 3 to 7 sides
            });
        }
        
        return patterns;
    }

    private List<CrystallinePattern> GenerateSaltPatterns(RenderContext ctx, float wavelength, float complexity)
    {
        var patterns = new List<CrystallinePattern>();
        
        // Generate crystalline patterns
        float time = ctx.Time;
        
        for (int i = 0; i < (int)(complexity * 6); i++)
        {
            float size = wavelength * (i + 1) * 0.4f;
            float x = ctx.Width * 0.5f + (float)(Math.Sin(time * 0.3f + i) * 80);
            float y = ctx.Height * 0.5f + (float)(Math.Cos(time * 0.3f + i) * 80);
            
            patterns.Add(new CrystallinePattern
            {
                Type = "crystal",
                Position = new Vector2(x, y),
                Size = size,
                Rotation = time * 0.5f + i,
                Symmetry = 4 + (i % 4) // 4 to 7 fold symmetry
            });
        }
        
        return patterns;
    }

    private List<ElectromagneticPattern> GenerateMetalPatterns(RenderContext ctx, float wavelength, float complexity)
    {
        var patterns = new List<ElectromagneticPattern>();
        
        // Generate electromagnetic field patterns
        float time = ctx.Time;
        
        for (int i = 0; i < (int)(complexity * 5); i++)
        {
            float radius = wavelength * (i + 1) * 0.6f;
            float x = ctx.Width * 0.5f + (float)(Math.Sin(time * 0.4f + i) * 60);
            float y = ctx.Height * 0.5f + (float)(Math.Cos(time * 0.4f + i) * 60);
            
            patterns.Add(new ElectromagneticPattern
            {
                Type = "field",
                Center = new Vector2(x, y),
                Radius = radius,
                Strength = (float)(Math.Sin(time * 3 + i) * 0.5 + 0.5),
                Polarity = i % 2 == 0 ? "positive" : "negative"
            });
        }
        
        return patterns;
    }

    private List<WaveInterference> GenerateAirPatterns(RenderContext ctx, float wavelength, float complexity)
    {
        var patterns = new List<WaveInterference>();
        
        // Generate wave interference patterns
        float time = ctx.Time;
        
        for (int i = 0; i < (int)(complexity * 4); i++)
        {
            float amplitude = wavelength * (i + 1) * 0.2f;
            float x = ctx.Width * 0.5f + (float)(Math.Sin(time * 0.6f + i) * 120);
            float y = ctx.Height * 0.5f + (float)(Math.Cos(time * 0.6f + i) * 120);
            
            patterns.Add(new WaveInterference
            {
                Type = "interference",
                Position = new Vector2(x, y),
                Amplitude = amplitude,
                Phase = time + i,
                Frequency = _currentFrequency * (0.5f + i * 0.1f)
            });
        }
        
        return patterns;
    }

    private List<PlasmaField> GeneratePlasmaPatterns(RenderContext ctx, float wavelength, float complexity)
    {
        var patterns = new List<PlasmaField>();
        
        // Generate plasma field patterns
        float time = ctx.Time;
        
        for (int i = 0; i < (int)(complexity * 3); i++)
        {
            float radius = wavelength * (i + 1) * 0.8f;
            float x = ctx.Width * 0.5f + (float)(Math.Sin(time * 0.2f + i) * 90);
            float y = ctx.Height * 0.5f + (float)(Math.Cos(time * 0.2f + i) * 90);
            
            patterns.Add(new PlasmaField
            {
                Type = "plasma",
                Center = new Vector2(x, y),
                Radius = radius,
                Intensity = (float)(Math.Sin(time * 4 + i) * 0.5 + 0.5),
                Ionization = 0.3f + (i * 0.1f)
            });
        }
        
        return patterns;
    }

    private void RenderPattern(CymaticPattern pattern, RenderContext ctx)
    {
        // TODO: Implement SkiaSharp rendering for the cymatic patterns
        // This would include:
        // - Drawing nodal points as circles
        // - Drawing antinodal lines
        // - Rendering material-specific patterns
        // - Applying color gradients based on displacement
        // - Adding animation effects
    }

    private void RenderHarmonicSeries(RenderContext ctx)
    {
        // TODO: Render harmonic series overlay
        // Show fundamental frequency and its harmonics
        // Display frequency ratios and musical intervals
    }

    private void RenderSolfeggioOverlay(RenderContext ctx)
    {
        // TODO: Render Solfeggio frequency overlay
        // Show which frequencies correspond to Solfeggio tones
        // Display the meaning and significance of each frequency
    }

    // Data structures for cymatic patterns
    private class CymaticPattern
    {
        public float Frequency { get; set; }
        public MaterialType Material { get; set; }
        public int Width { get; set; }
        public int Height { get; set; }
        public float Time { get; set; }
        public float Wavelength { get; set; }
        public List<Vector2> NodalPoints { get; set; } = new();
        public List<Vector2[]> AntinodalLines { get; set; } = new();
        public List<FluidPattern> FluidPatterns { get; set; } = new();
        public List<GranularPattern> GranularPatterns { get; set; } = new();
        public List<CrystallinePattern> CrystallinePatterns { get; set; } = new();
        public List<ElectromagneticPattern> ElectromagneticPatterns { get; set; } = new();
        public List<WaveInterference> WaveInterference { get; set; } = new();
        public List<PlasmaField> PlasmaFields { get; set; } = new();
    }

    private class FluidPattern
    {
        public string Type { get; set; } = "";
        public Vector2 Center { get; set; }
        public float Radius { get; set; }
        public float Amplitude { get; set; }
        public float Frequency { get; set; }
    }

    private class GranularPattern
    {
        public string Type { get; set; } = "";
        public Vector2 Position { get; set; }
        public float Size { get; set; }
        public float Rotation { get; set; }
        public int Sides { get; set; }
    }

    private class CrystallinePattern
    {
        public string Type { get; set; } = "";
        public Vector2 Position { get; set; }
        public float Size { get; set; }
        public float Rotation { get; set; }
        public int Symmetry { get; set; }
    }

    private class ElectromagneticPattern
    {
        public string Type { get; set; } = "";
        public Vector2 Center { get; set; }
        public float Radius { get; set; }
        public float Strength { get; set; }
        public string Polarity { get; set; } = "";
    }

    private class WaveInterference
    {
        public string Type { get; set; } = "";
        public Vector2 Position { get; set; }
        public float Amplitude { get; set; }
        public float Phase { get; set; }
        public float Frequency { get; set; }
    }

    private class PlasmaField
    {
        public string Type { get; set; } = "";
        public Vector2 Center { get; set; }
        public float Radius { get; set; }
        public float Intensity { get; set; }
        public float Ionization { get; set; }
    }
}
