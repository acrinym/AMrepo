using System.Collections.Generic;

namespace PhoenixVisualizer.Core.Nodes;

/// <summary>
/// Godrays effect node - Creates volumetric light rays radiating from a central source
/// Perfect for dramatic lighting effects and desert scenes
/// </summary>
public class GodraysNode : IEffectNode
{
    public string Name => "Godrays";
    public Dictionary<string, EffectParam> Params { get; } = new()
    {
        ["intensity"] = new EffectParam {
            Label = "Intensity",
            Type = "slider",
            Min = 0,
            Max = 5,
            FloatValue = 1f
        },
        ["rayCount"] = new EffectParam {
            Label = "Ray Count",
            Type = "slider",
            Min = 4,
            Max = 32,
            FloatValue = 12
        },
        ["rayLength"] = new EffectParam {
            Label = "Ray Length",
            Type = "slider",
            Min = 50,
            Max = 300,
            FloatValue = 150f
        },
        ["color"] = new EffectParam {
            Label = "Color",
            Type = "color",
            ColorValue = "#FFD700"
        },
        ["centerX"] = new EffectParam {
            Label = "Center X",
            Type = "slider",
            Min = 0,
            Max = 1,
            FloatValue = 0.5f
        },
        ["centerY"] = new EffectParam {
            Label = "Center Y",
            Type = "slider",
            Min = 0,
            Max = 1,
            FloatValue = 0.5f
        },
        ["animate"] = new EffectParam {
            Label = "Animate",
            Type = "checkbox",
            BoolValue = true
        }
    };

    public void Render(float[] waveform, float[] spectrum, RenderContext ctx)
    {
        // TODO: Implement GLSL-style radial blur and scattering
        // For now, create a simple radial ray pattern

        float centerX = ctx.Width * Params["centerX"].FloatValue;
        float centerY = ctx.Height * Params["centerY"].FloatValue;
        float intensity = Params["intensity"].FloatValue;
        int rayCount = (int)Params["rayCount"].FloatValue;
        float rayLength = Params["rayLength"].FloatValue;
        bool animate = Params["animate"].BoolValue;

        // Parse color
        string colorHex = Params["color"].ColorValue;
        uint color = ParseHexColor(colorHex);

        // Apply audio-reactive modifications
        if (spectrum.Length > 0)
        {
            // Use bass frequencies to modulate ray intensity
            float bassEnergy = spectrum.Length > 10 ? spectrum[5] : 0;
            intensity *= (1f + bassEnergy * 0.5f);
        }

        // Draw radial rays
        for (int i = 0; i < rayCount; i++)
        {
            float angle = (i / (float)rayCount) * MathF.PI * 2;
            if (animate)
            {
                angle += ctx.Time * 0.5f; // Rotate rays over time
            }

            // Calculate ray endpoints
            float endX = centerX + MathF.Cos(angle) * rayLength;
            float endY = centerY + MathF.Sin(angle) * rayLength;

            // Draw ray with intensity-based alpha
            uint rayColor = (color & 0x00FFFFFF) | ((uint)(intensity * 127) << 24);

            // TODO: Replace with proper SkiaSharp drawing
            // ctx.Canvas.DrawLine(centerX, centerY, endX, endY, rayColor, 2f);

            // For now, just mark that this effect would render
            // Console.WriteLine($"Godrays: Ray {i} from ({centerX}, {centerY}) to ({endX}, {endY})");
        }
    }

    private uint ParseHexColor(string hexColor)
    {
        if (string.IsNullOrEmpty(hexColor) || !hexColor.StartsWith("#"))
            return 0xFFFFFFFF; // Default white

        try
        {
            // Remove # and parse
            string hex = hexColor.Substring(1);
            if (hex.Length == 6)
            {
                uint r = Convert.ToUInt32(hex.Substring(0, 2), 16);
                uint g = Convert.ToUInt32(hex.Substring(2, 2), 16);
                uint b = Convert.ToUInt32(hex.Substring(4, 2), 16);
                return 0xFF000000 | (r << 16) | (g << 8) | b;
            }
        }
        catch
        {
            // Fall back to white on parsing error
        }

        return 0xFFFFFFFF;
    }
}
