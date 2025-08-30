using System;
using System.Collections.Generic;
using System.Numerics;
using System.Linq; // Added for GroupBy and OrderBy

namespace PhoenixVisualizer.Core.Nodes;

/// <summary>
/// Sacred Geometry Node - Implements mathematical relationships from Earth harmonics research
/// Based on the "Tree of Frequency" and "Earth harmonics in Brainwave Ranges" diagrams
/// </summary>
public class SacredGeometryNode : IEffectNode
{
    // Mathematical constants from the research
    private const float PHI = 1.618033988749f; // Golden ratio
    private const float PI = MathF.PI;
    private const float E = 2.718281828459f; // Euler's number
    
    // Earth rotation constants
    private const float EARTH_ROTATION_24H = 360f; // degrees
    private const float HARMONIC_MULTIPLIER_5_4 = 5f / 4f; // x5/4 relationship
    private const float HARMONIC_MULTIPLIER_3_2 = 3f / 2f; // x3/2 relationship
    private const float HARMONIC_MULTIPLIER_11_8 = 11f / 8f; // x11/8 for Solfeggio
    private const float HARMONIC_MULTIPLIER_4_5 = 4f / 5f; // x4/5 relationship
    private const float HARMONIC_MULTIPLIER_2_3 = 2f / 3f; // x2/3 relationship

    // Frequency domains from the research
    private enum FrequencyDomain
    {
        Physical,      // Physical/Gravity/Spin
        Electromagnetic, // Electro-Magnetic
        Emotional,     // Emotional/Astral
        Mental,        // Mental
        Archetypal,    // Archetypal
        Spiritual,     // Spiritual
        Divine         // Divine
    }

    // Current visualization state
    private FrequencyDomain _currentDomain = FrequencyDomain.Physical;
    private float _baseFrequency = 388.8f; // G fundamental from research
    private float _harmonicDepth = 5;
    private bool _showMathematicalRelationships = true;
    private bool _showCymaticPatterns = true;
    private bool _showFrequencyTree = true;
    private float _animationSpeed = 1.0f;
    private bool _useRecurringDecimals = true;
    private float _patternComplexity = 1.0f;
    private float _time = 0f; // Added for animation phase

    public string Name => "Sacred Geometry";
    public Dictionary<string, EffectParam> Params { get; } = new()
    {
        ["domain"] = new EffectParam {
            Label = "Frequency Domain",
            Type = "dropdown",
            StringValue = "physical",
            Options = new() { 
                "physical", "electromagnetic", "emotional", "mental", 
                "archetypal", "spiritual", "divine" 
            }
        },
        ["baseFreq"] = new EffectParam {
            Label = "Base Frequency (Hz)",
            Type = "slider",
            Min = 1,
            Max = 1000,
            FloatValue = 388.8f
        },
        ["harmonicDepth"] = new EffectParam {
            Label = "Harmonic Depth",
            Type = "slider",
            Min = 1,
            Max = 10,
            FloatValue = 5f
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
        ["mathRelations"] = new EffectParam {
            Label = "Show Math Relationships",
            Type = "checkbox",
            BoolValue = true
        },
        ["cymaticPatterns"] = new EffectParam {
            Label = "Show Cymatic Patterns",
            Type = "checkbox",
            BoolValue = true
        },
        ["frequencyTree"] = new EffectParam {
            Label = "Show Frequency Tree",
            Type = "checkbox",
            BoolValue = true
        },
        ["recurringDecimals"] = new EffectParam {
            Label = "Use Recurring Decimals",
            Type = "checkbox",
            BoolValue = true
        },
        ["baseColor"] = new EffectParam {
            Label = "Base Color",
            Type = "color",
            ColorValue = "#FFD700"
        }
    };

    public void Render(float[] waveform, float[] spectrum, RenderContext ctx)
    {
        UpdateParameters();
        _time += ctx.DeltaTime * _animationSpeed; // Update animation time
        
        var frequencyTree = GenerateFrequencyTree();
        var mathematicalRelations = GenerateMathematicalRelations();
        var cymaticPatterns = GenerateCymaticPatterns(ctx);
        
        if (_showFrequencyTree)
            RenderFrequencyTree(frequencyTree, ctx);
        
        if (_showMathematicalRelationships)
            RenderMathematicalRelations(mathematicalRelations, ctx);
        
        if (_showCymaticPatterns)
            RenderCymaticPatterns(cymaticPatterns, ctx);
        
        RenderDomainInfo(ctx);
    }

    private void UpdateParameters()
    {
        _currentDomain = ParseDomain(Params["domain"].StringValue);
        _baseFrequency = Params["baseFreq"].FloatValue;
        _harmonicDepth = Params["harmonicDepth"].FloatValue;
        _patternComplexity = Params["complexity"].FloatValue;
        _animationSpeed = Params["animation"].FloatValue;
        _showMathematicalRelationships = Params["mathRelations"].BoolValue;
        _showCymaticPatterns = Params["cymaticPatterns"].BoolValue;
        _showFrequencyTree = Params["frequencyTree"].BoolValue;
        _useRecurringDecimals = Params["recurringDecimals"].BoolValue;
    }

    private FrequencyDomain ParseDomain(string domain)
    {
        return domain switch
        {
            "physical" => FrequencyDomain.Physical,
            "electromagnetic" => FrequencyDomain.Electromagnetic,
            "emotional" => FrequencyDomain.Emotional,
            "mental" => FrequencyDomain.Mental,
            "archetypal" => FrequencyDomain.Archetypal,
            "spiritual" => FrequencyDomain.Spiritual,
            "divine" => FrequencyDomain.Divine,
            _ => FrequencyDomain.Physical
        };
    }

    private List<FrequencyNode> GenerateFrequencyTree()
    {
        var tree = new List<FrequencyNode>();
        
        // Start with base frequency
        var root = new FrequencyNode
        {
            Frequency = _baseFrequency,
            Note = GetNoteFromFrequency(_baseFrequency),
            Domain = _currentDomain,
            Level = 0,
            MathematicalOperation = "Fundamental"
        };
        tree.Add(root);
        
        // Generate harmonic series based on research relationships
        for (int i = 1; i <= _harmonicDepth; i++)
        {
            var node = GenerateHarmonicNode(root, i);
            tree.Add(node);
        }
        
        // Generate cross-domain relationships
        GenerateCrossDomainRelationships(tree);
        
        return tree;
    }

    private FrequencyNode GenerateHarmonicNode(FrequencyNode parent, int level)
    {
        // Apply mathematical relationships from research
        float frequency;
        string operation;
        
        switch (level % 4)
        {
            case 1: // x5/4 relationship
                frequency = parent.Frequency * HARMONIC_MULTIPLIER_5_4;
                operation = "×5/4";
                break;
            case 2: // x3/2 relationship
                frequency = parent.Frequency * HARMONIC_MULTIPLIER_3_2;
                operation = "×3/2";
                break;
            case 3: // x4/5 relationship
                frequency = parent.Frequency * HARMONIC_MULTIPLIER_4_5;
                operation = "×4/5";
                break;
            default: // x2/3 relationship
                frequency = parent.Frequency * HARMONIC_MULTIPLIER_2_3;
                operation = "×2/3";
                break;
        }
        
        // Apply domain-specific modifications
        frequency = ApplyDomainModifications(frequency, level);
        
        return new FrequencyNode
        {
            Frequency = frequency,
            Note = GetNoteFromFrequency(frequency),
            Domain = GetNextDomain(parent.Domain),
            Level = level,
            MathematicalOperation = operation,
            ParentFrequency = parent.Frequency,
            ParentOperation = parent.MathematicalOperation
        };
    }

    private float ApplyDomainModifications(float frequency, int level)
    {
        // Apply domain-specific mathematical transformations
        switch (_currentDomain)
        {
            case FrequencyDomain.Physical:
                // Physical domain uses natural logarithms
                frequency *= (float)Math.Log(1 + level);
                break;
            case FrequencyDomain.Electromagnetic:
                // EM domain uses exponential relationships
                frequency *= (float)Math.Exp(level * 0.1f);
                break;
            case FrequencyDomain.Emotional:
                // Emotional domain uses sine wave modulation
                frequency *= 1 + (float)Math.Sin(level * PI / 6) * 0.2f;
                break;
            case FrequencyDomain.Mental:
                // Mental domain uses Fibonacci-like relationships
                frequency *= GetFibonacciRatio(level);
                break;
            case FrequencyDomain.Archetypal:
                // Archetypal domain uses golden ratio
                frequency *= (float)Math.Pow(PHI, level * 0.3f);
                break;
            case FrequencyDomain.Spiritual:
                // Spiritual domain uses pi relationships
                frequency *= 1 + (float)Math.Sin(level * PI / 4) * 0.15f;
                break;
            case FrequencyDomain.Divine:
                // Divine domain uses e (Euler's number)
                frequency *= (float)Math.Pow(E, level * 0.1f);
                break;
        }
        
        return frequency;
    }

    private float GetFibonacciRatio(int n)
    {
        if (n <= 1) return 1f;
        if (n == 2) return 1f;
        
        float prev = 1f, curr = 1f;
        for (int i = 3; i <= n; i++)
        {
            float next = prev + curr;
            prev = curr;
            curr = next;
        }
        
        return curr / prev; // Approximate golden ratio
    }

    private FrequencyDomain GetNextDomain(FrequencyDomain current)
    {
        // Cycle through domains
        return (FrequencyDomain)(((int)current + 1) % 7);
    }

    private string GetNoteFromFrequency(float frequency)
    {
        // Simple frequency to note mapping
        // A4 = 440 Hz, using equal temperament
        float a4 = 440f;
        float semitones = 12f * (float)Math.Log2(frequency / a4);
        int noteIndex = (int)Math.Round(semitones) % 12;
        
        string[] notes = { "A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#" };
        return notes[(noteIndex + 9) % 12]; // Adjust for A4 reference
    }

    private void GenerateCrossDomainRelationships(List<FrequencyNode> tree)
    {
        // Generate Solfeggio relationships (x11/8)
        for (int i = 0; i < tree.Count; i++)
        {
            var node = tree[i];
            if (node.Level > 0) // Skip root
            {
                float solfeggioFreq = node.Frequency * HARMONIC_MULTIPLIER_11_8;
                var solfeggioNode = new FrequencyNode
                {
                    Frequency = solfeggioFreq,
                    Note = GetNoteFromFrequency(solfeggioFreq),
                    Domain = FrequencyDomain.Spiritual, // Solfeggio is spiritual
                    Level = node.Level + 100, // Mark as special
                    MathematicalOperation = "×11/8 (Solfeggio)",
                    ParentFrequency = node.Frequency,
                    ParentOperation = node.MathematicalOperation
                };
                tree.Add(solfeggioNode);
            }
        }
    }

    private List<MathematicalRelationship> GenerateMathematicalRelations()
    {
        var relationships = new List<MathematicalRelationship>();
        
        // Generate relationships based on research diagrams
        relationships.Add(new MathematicalRelationship
        {
            Type = "Harmonic Series",
            Description = "Fundamental frequency and its harmonics",
            Formula = $"f_n = f_1 × n",
            Example = $"{_baseFrequency:F2} Hz × 2 = {_baseFrequency * 2:F2} Hz"
        });
        
        relationships.Add(new MathematicalRelationship
        {
            Type = "Golden Ratio",
            Description = "Phi-based frequency relationships",
            Formula = $"f_n = f_1 × φ^n",
            Example = $"{_baseFrequency:F2} Hz × {PHI:F3} = {_baseFrequency * PHI:F2} Hz"
        });
        
        relationships.Add(new MathematicalRelationship
        {
            Type = "Solfeggio Generation",
            Description = "11th harmonic of Earth frequencies",
            Formula = $"f_solfeggio = f_earth × 11/8",
            Example = $"14.4 Hz × 11/8 = 19.8 Hz"
        });
        
        relationships.Add(new MathematicalRelationship
        {
            Type = "Domain Transition",
            Description = "Cross-domain frequency relationships",
            Formula = $"f_{_currentDomain} = f_physical × k_domain",
            Example = $"Physical to {_currentDomain} transformation"
        });
        
        return relationships;
    }

    private List<CymaticPattern> GenerateCymaticPatterns(RenderContext ctx)
    {
        var patterns = new List<CymaticPattern>();
        
        // Generate patterns based on current domain and frequency
        float time = ctx.Time * _animationSpeed;
        
        for (int i = 0; i < (int)(_patternComplexity * 8); i++)
        {
            float frequency = _baseFrequency * (i + 1) * 0.5f;
            float wavelength = 343f / frequency; // Speed of sound in air
            
            var pattern = new CymaticPattern
            {
                Frequency = frequency,
                Wavelength = wavelength,
                Center = new Vector2(
                    ctx.Width * 0.5f + (float)(Math.Sin(time + i) * 50),
                    ctx.Height * 0.5f + (float)(Math.Cos(time + i) * 50)
                ),
                Radius = wavelength * _patternComplexity,
                Symmetry = GetDomainSymmetry(_currentDomain),
                Color = GetDomainColor(_currentDomain, i),
                AnimationPhase = time + i
            };
            
            patterns.Add(pattern);
        }
        
        return patterns;
    }

    private int GetDomainSymmetry(FrequencyDomain domain)
    {
        return domain switch
        {
            FrequencyDomain.Physical => 4,      // Square symmetry
            FrequencyDomain.Electromagnetic => 6, // Hexagonal symmetry
            FrequencyDomain.Emotional => 5,      // Pentagonal symmetry
            FrequencyDomain.Mental => 8,         // Octagonal symmetry
            FrequencyDomain.Archetypal => 7,     // Heptagonal symmetry
            FrequencyDomain.Spiritual => 12,     // Dodecagonal symmetry
            FrequencyDomain.Divine => 10,        // Decagonal symmetry
            _ => 4
        };
    }

    private uint GetDomainColor(FrequencyDomain domain, int index)
    {
        // Generate colors based on domain and index
        float hue = ((int)domain * 51.4f + index * 30f) % 360f;
        return HsvToRgb(hue / 360f, 0.8f, 0.9f);
    }

    private uint HsvToRgb(float hue, float saturation, float brightness)
    {
        float c = brightness * saturation;
        float x = c * (1 - Math.Abs((hue * 6) % 2 - 1));
        float m = brightness - c;

        float r, g, b;
        if (hue < 1f/6f) { r = c; g = x; b = 0; }
        else if (hue < 2f/6f) { r = x; g = c; b = 0; }
        else if (hue < 3f/6f) { r = 0; g = c; b = x; }
        else if (hue < 4f/6f) { r = 0; g = x; b = c; }
        else if (hue < 5f/6f) { r = x; g = 0; b = c; }
        else { r = c; g = 0; b = x; }

        byte red = (byte)((r + m) * 255);
        byte green = (byte)((g + m) * 255);
        byte blue = (byte)((b + m) * 255);

        return 0xFF000000 | ((uint)red << 16) | ((uint)green << 8) | blue;
    }

    private void RenderFrequencyTree(List<FrequencyNode> tree, RenderContext ctx)
    {
        if (ctx.Canvas == null || tree.Count == 0) return;
        
        float centerX = ctx.Width / 2f;
        float centerY = ctx.Height / 2f;
        float maxRadius = Math.Min(centerX, centerY) * 0.7f;
        
        // Group nodes by level
        var nodesByLevel = tree.GroupBy(n => n.Level).OrderBy(g => g.Key).ToList();
        
        for (int level = 0; level < nodesByLevel.Count; level++)
        {
            var levelNodes = nodesByLevel[level].ToList();
            float levelRadius = maxRadius * (0.2f + level * 0.15f);
            
            for (int i = 0; i < levelNodes.Count; i++)
            {
                var node = levelNodes[i];
                float angle = i * 2f * MathF.PI / levelNodes.Count;
                
                float x = centerX + levelRadius * MathF.Cos(angle);
                float y = centerY + levelRadius * MathF.Sin(angle);
                
                // Draw node
                uint nodeColor = GetDomainColor(node.Domain, i);
                ctx.Canvas.FillCircle(x, y, 20f, nodeColor);
                ctx.Canvas.DrawCircle(x, y, 20f, 0xFFFFFFFF, 2f);
                
                // Draw connections to parent nodes
                if (level > 0)
                {
                    var parentLevel = nodesByLevel[level - 1].ToList();
                    if (parentLevel.Count > 0)
                    {
                        int parentIndex = i % parentLevel.Count;
                        var parent = parentLevel[parentIndex];
                        float parentAngle = parentIndex * 2f * MathF.PI / parentLevel.Count;
                        float parentRadius = maxRadius * (0.2f + (level - 1) * 0.15f);
                        
                        float parentX = centerX + parentRadius * MathF.Cos(parentAngle);
                        float parentY = centerY + parentRadius * MathF.Sin(parentAngle);
                        
                        // Draw connection line
                        ctx.Canvas.DrawLine(parentX, parentY, x, y, 0x80FFFFFF, 1f);
                        
                        // Draw mathematical operation label
                        float midX = (parentX + x) / 2f;
                        float midY = (parentY + y) / 2f;
                        
                        // Draw operation indicator
                        ctx.Canvas.FillCircle(midX, midY, 8f, 0xFF6B6BFF);
                    }
                }
            }
        }
    }

    private void RenderMathematicalRelations(List<MathematicalRelationship> relationships, RenderContext ctx)
    {
        if (ctx.Canvas == null || relationships.Count == 0) return;
        
        // Draw mathematical relationship overlay in top-right corner
        float startX = ctx.Width - 320f;
        float startY = 20f;
        float lineHeight = 30f;
        
        // Background rectangle
        ctx.Canvas.FillRectangle(startX - 10f, startY - 10f, 300f, relationships.Count * lineHeight + 20f, 0x80000000);
        
        for (int i = 0; i < relationships.Count && i < 8; i++)
        {
            var relation = relationships[i];
            float y = startY + i * lineHeight;
            
            // Draw relationship type header
            ctx.Canvas.FillRectangle(startX, y, 280f, 20f, GetDomainColor(FrequencyDomain.Physical, i));
            
            // Draw description area
            ctx.Canvas.FillRectangle(startX, y + 20f, 280f, 8f, 0xFF6B6BFF);
            
            // Note: SkiaSharp text rendering would go here for formulas and examples
        }
    }

    private void RenderCymaticPatterns(List<CymaticPattern> patterns, RenderContext ctx)
    {
        if (ctx.Canvas == null || patterns.Count == 0) return;
        
        float centerX = ctx.Width / 2f;
        float centerY = ctx.Height / 2f;
        
        foreach (var pattern in patterns)
        {
            // Calculate animated position
            float animOffset = MathF.Sin(_time + pattern.AnimationPhase) * 10f;
            float x = pattern.Center.X + animOffset;
            float y = pattern.Center.Y + animOffset;
            
            // Draw nodal pattern based on symmetry
            DrawSymmetricalPattern(x, y, pattern.Radius, pattern.Symmetry, pattern.Color, ctx);
            
            // Draw wavelength rings
            float wavelength = pattern.Wavelength;
            for (int ring = 1; ring <= 3; ring++)
            {
                float ringRadius = pattern.Radius + ring * wavelength * 0.1f;
                uint ringColor = ApplyAlpha(pattern.Color, 0.3f - ring * 0.1f);
                ctx.Canvas.DrawCircle(x, y, ringRadius, ringColor, 1f);
            }
        }
    }

    private void RenderDomainInfo(RenderContext ctx)
    {
        if (ctx.Canvas == null) return;
        
        // Draw domain information overlay in bottom-left corner
        float startX = 20f;
        float startY = ctx.Height - 120f;
        
        // Background rectangle
        ctx.Canvas.FillRectangle(startX - 10f, startY - 10f, 300f, 100f, 0x80000000);
        
        // Current domain display
        var currentDomain = FrequencyDomain.Physical; // This would come from current state
        uint domainColor = GetDomainColor(currentDomain, 0);
        
        // Draw domain header
        ctx.Canvas.FillRectangle(startX, startY, 280f, 25f, domainColor);
        
        // Draw domain characteristics
        ctx.Canvas.FillRectangle(startX, startY + 30f, 280f, 15f, 0xFF6BFF6B);
        ctx.Canvas.FillRectangle(startX, startY + 50f, 280f, 15f, 0xFF6B6BFF);
        ctx.Canvas.FillRectangle(startX, startY + 70f, 280f, 15f, 0xFFFFFF6B);
        
        // Note: SkiaSharp text rendering would go here for domain names and characteristics
    }

    private void DrawSymmetricalPattern(float x, float y, float radius, int symmetry, uint color, RenderContext ctx)
    {
        if (ctx.Canvas == null) return;
        
        // Draw symmetry-based nodal pattern
        for (int i = 0; i < symmetry; i++)
        {
            float angle = i * 2f * MathF.PI / symmetry + _time * 0.5f;
            float nodalRadius = radius * (0.3f + 0.2f * MathF.Sin(_time * 2f + i));
            
            float nodalX = x + nodalRadius * MathF.Cos(angle);
            float nodalY = y + nodalRadius * MathF.Sin(angle);
            
            // Draw nodal point
            ctx.Canvas.FillCircle(nodalX, nodalY, 5f, color);
            
            // Draw connecting lines between nodal points
            if (i > 0)
            {
                float prevAngle = (i - 1) * 2f * MathF.PI / symmetry + _time * 0.5f;
                float prevRadius = radius * (0.3f + 0.2f * MathF.Sin(_time * 2f + (i - 1)));
                float prevX = x + prevRadius * MathF.Cos(prevAngle);
                float prevY = y + prevRadius * MathF.Sin(prevAngle);
                
                ctx.Canvas.DrawLine(prevX, prevY, nodalX, nodalY, ApplyAlpha(color, 0.6f), 1f);
            }
        }
        
        // Connect last to first
        if (symmetry > 1)
        {
            float firstAngle = _time * 0.5f;
            float firstRadius = radius * (0.3f + 0.2f * MathF.Sin(_time * 2f));
            float firstX = x + firstRadius * MathF.Cos(firstAngle);
            float firstY = y + firstRadius * MathF.Sin(firstAngle);
            
            float lastAngle = (symmetry - 1) * 2f * MathF.PI / symmetry + _time * 0.5f;
            float lastRadius = radius * (0.3f + 0.2f * MathF.Sin(_time * 2f + (symmetry - 1)));
            float lastX = x + lastRadius * MathF.Cos(lastAngle);
            float lastY = y + lastRadius * MathF.Sin(lastAngle);
            
            ctx.Canvas.DrawLine(lastX, lastY, firstX, firstY, ApplyAlpha(color, 0.6f), 1f);
        }
    }

    private uint ApplyAlpha(uint color, float alpha)
    {
        byte r = (byte)(color >> 16);
        byte g = (byte)(color >> 8);
        byte b = (byte)color;
        byte a = (byte)(alpha * 255);
        
        return (uint)((a << 24) | (r << 16) | (g << 8) | b);
    }

    // Data structures
    private class FrequencyNode
    {
        public float Frequency { get; set; }
        public string Note { get; set; } = "";
        public FrequencyDomain Domain { get; set; }
        public int Level { get; set; }
        public string MathematicalOperation { get; set; } = "";
        public float ParentFrequency { get; set; }
        public string ParentOperation { get; set; } = "";
    }

    private class MathematicalRelationship
    {
        public string Type { get; set; } = "";
        public string Description { get; set; } = "";
        public string Formula { get; set; } = "";
        public string Example { get; set; } = "";
    }

    private class CymaticPattern
    {
        public float Frequency { get; set; }
        public float Wavelength { get; set; }
        public Vector2 Center { get; set; }
        public float Radius { get; set; }
        public int Symmetry { get; set; }
        public uint Color { get; set; }
        public float AnimationPhase { get; set; }
    }
}
