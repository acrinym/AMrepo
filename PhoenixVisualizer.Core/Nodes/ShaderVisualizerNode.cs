using System;
using System.Numerics;

namespace PhoenixVisualizer.Core.Nodes;

/// <summary>
/// Shader Visualizer Node - GLSL Shader Emulation in C#
/// Implements complex ray-marching 3D scenes with lighting and geometry
/// Based on advanced GLSL shader techniques
/// </summary>
public class ShaderVisualizerNode : IEffectNode
{
    // Shader constants (from the GLSL code)
    private const int ITR = 150;      // Ray marching iterations
    private const float DST = 90.0f;  // Maximum ray distance
    private const float SRF = 0.001f; // Surface threshold
    private const int NSO = 7;        // Number of scene objects
    private const float PI = (float)Math.PI;

    // Shader uniforms
    private Vector3 _iResolution;      // Viewport resolution
    private float _iTime;             // Shader playback time
    private float _iTimeDelta;        // Render time delta
    private float _iFrameRate;        // Frame rate
    private int _iFrame;              // Current frame
    private Vector4 _iMouse;          // Mouse coordinates
    private Vector4 _iDate;           // Date/time

    // Scene state variables (equivalent to GLSL globals)
    private float _globalGlow = 0.0f;
    private float _time = 0.0f;
    private float _time1 = 0.0f;

    public string Name => "Shader Visualizer";
    public Dictionary<string, EffectParam> Params { get; } = new()
    {
        ["resolution"] = new EffectParam {
            Label = "Resolution Scale",
            Type = "slider",
            Min = 0.1f,
            Max = 2.0f,
            FloatValue = 1.0f
        },
        ["timeSpeed"] = new EffectParam {
            Label = "Time Speed",
            Type = "slider",
            Min = 0.1f,
            Max = 5.0f,
            FloatValue = 1.0f
        },
        ["cameraDistance"] = new EffectParam {
            Label = "Camera Distance",
            Type = "slider",
            Min = 5f,
            Max = 50f,
            FloatValue = 15f
        },
        ["glowIntensity"] = new EffectParam {
            Label = "Glow Intensity",
            Type = "slider",
            Min = 0f,
            Max = 2f,
            FloatValue = 1f
        },
        ["reflectionBounces"] = new EffectParam {
            Label = "Reflection Bounces",
            Type = "slider",
            Min = 0,
            Max = 5,
            FloatValue = 1
        },
        ["colorScheme"] = new EffectParam {
            Label = "Color Scheme",
            Type = "dropdown",
            StringValue = "dynamic",
            Options = new() { "dynamic", "mono", "spectrum", "neon" }
        },
        ["enablePostFX"] = new EffectParam {
            Label = "Post Processing",
            Type = "checkbox",
            BoolValue = true
        },
        ["enableGlow"] = new EffectParam {
            Label = "Object Glow",
            Type = "checkbox",
            BoolValue = true
        }
    };

    public void Render(float[] waveform, float[] spectrum, RenderContext ctx)
    {
        UpdateParameters(ctx);
        UpdateShaderUniforms(ctx);

        // Render the shader for each pixel
        for (int y = 0; y < ctx.Height; y++)
        {
            for (int x = 0; x < ctx.Width; x++)
            {
                Vector2 uv = GetUVCoordinates(x, y, ctx.Width, ctx.Height);
                Vector4 color = MainImage(uv);
                // TODO: Set pixel color in canvas
                // ctx.Canvas.SetPixel(x, y, color);
            }
        }
    }

    private void UpdateParameters(RenderContext ctx)
    {
        // Update shader uniforms based on parameters and context
        _iResolution = new Vector3(
            ctx.Width * Params["resolution"].FloatValue,
            ctx.Height * Params["resolution"].FloatValue,
            0
        );

        _iTime += ctx.Time * Params["timeSpeed"].FloatValue;
        _time = _iTime % (PI * 4.0f);
        _time1 = Math.Clamp(2.0f - _time, 0.0f, 1.0f);

        _iFrameRate = 60f; // Assume 60 FPS
        _iFrame = (int)(_iTime * _iFrameRate);

        // Mouse position (simulated)
        _iMouse = new Vector4(ctx.Width * 0.5f, ctx.Height * 0.5f, 0, 0);

        // Date/time
        DateTime now = DateTime.Now;
        _iDate = new Vector4(
            now.Year,
            now.Month,
            now.Day,
            (float)now.TimeOfDay.TotalSeconds
        );
    }

    private void UpdateShaderUniforms(RenderContext ctx)
    {
        // Additional uniform updates based on audio data
        if (ctx.Volume > 0)
        {
            // Modulate time based on volume
            _iTime += ctx.Volume * 0.1f;
        }

        // Update based on beat detection
        if (ctx.Beat)
        {
            // Add beat-based modulation
            _globalGlow = Math.Min(_globalGlow + 0.1f, 1.0f);
        }
        else
        {
            _globalGlow = Math.Max(_globalGlow - 0.02f, 0.0f);
        }
    }

    private Vector2 GetUVCoordinates(int x, int y, int width, int height)
    {
        // Convert pixel coordinates to UV coordinates (-1 to 1)
        float u = (2.0f * x - width) / height;
        float v = (2.0f * y - height) / height;
        return new Vector2(u, v);
    }

    private Vector4 MainImage(Vector2 uv)
    {
        // Main shader function - equivalent to mainImage in GLSL
        Vector3 color = Vector3.Zero;

        // Camera setup
        Vector3 cameraOrigin = CalculateCameraOrigin();
        Vector3 rayDirection = CalculateRayDirection(uv, cameraOrigin);

        // Ray marching
        color = RayMarchScene(cameraOrigin, rayDirection);

        // Apply glow effect
        if (Params["enableGlow"].BoolValue)
        {
            color += _globalGlow * new Vector3(0, 1, 0.4f) * Params["glowIntensity"].FloatValue;
        }

        // Post-processing effects
        if (Params["enablePostFX"].BoolValue)
        {
            color = ApplyPostProcessing(uv, color);
        }

        // Gamma correction
        color = new Vector3(
            (float)Math.Pow(color.X, 0.4545),
            (float)Math.Pow(color.Y, 0.4545),
            (float)Math.Pow(color.Z, 0.4545)
        );

        return new Vector4(color, 1.0f);
    }

    private Vector3 CalculateCameraOrigin()
    {
        // Camera animation based on time
        Vector3 c1 = new Vector3(23, 23, -11);
        Vector3 c2 = VectorExtensions.Lerp(c1, new Vector3(0, 0, -11), Math.Clamp(_time - 1.0f, 0.0f, 1.0f));

        float t2 = Math.Clamp(_time, 0.0f, 7.9f);
        Vector3 c3 = VectorExtensions.Lerp(c2,
            new Vector3((float)Math.Cos(t2) * 51.0f, 0, (float)Math.Sin(t2) * 51.0f),
            Math.Clamp(t2 - 4.0f, 0.0f, 1.0f));

        return VectorExtensions.Lerp(c3,
            new Vector3((float)Math.Sin(_time) * 6.0f, 3, (float)Math.Cos(_time) * 6.0f),
            Math.Clamp(_time - 9.0f, 0.0f, 1.0f));
    }

    private Vector3 CalculateRayDirection(Vector2 uv, Vector3 cameraOrigin)
    {
        // Calculate view direction
        Vector3 forward = Vector3.Normalize(-cameraOrigin);
        Vector3 right = Vector3.Normalize(Vector3.Cross(forward, Vector3.UnitY));
        Vector3 up = Vector3.Normalize(Vector3.Cross(right, forward));

        // Create ray direction from UV coordinates
        return Vector3.Normalize(forward + uv.X * right + uv.Y * up);
    }

    private Vector3 RayMarchScene(Vector3 ro, Vector3 rd)
    {
        Vector3 color = Vector3.Zero;
        Vector3 lightPos = new Vector3(0.20f, 2.15f, -4.0f);

        // Object colors (equivalent to obj_clrs array in GLSL)
        Vector3[] objectColors = new Vector3[NSO]
        {
            new Vector3(1, 1, 1),      // Default/white
            new Vector3(0, 0, 0),      // Black
            new Vector3(0.2f, 0.2f, 0.2f), // Gray
            new Vector3(0, 1, 0.4f),   // Green-cyan
            new Vector3(0, 1, 0.4f),   // Green-cyan
            new Vector3(0, 1, 0.4f),   // Green-cyan
            new Vector3(0.1f, 0.1f, 0.1f) // Dark gray
        };

        Vector3 accumulation = Vector3.One;
        Vector3 backgroundColor = new Vector3(0.001f, 0.001f, 0.001f);

        color = backgroundColor;

        int maxReflections = (int)Params["reflectionBounces"].FloatValue;
        for (int reflection = 0; reflection <= maxReflections; reflection++)
        {
            Vector2 hit = RayMarch(ro, rd);
            float distance = hit.X;
            int objectId = (int)hit.Y;

            if (distance > 0 && distance < DST)
            {
                Vector3 hitPoint = ro + rd * distance;
                Vector3 normal = CalculateNormal(hitPoint);
                Vector3 lightDir = Vector3.Normalize(lightPos - hitPoint);

                // Lighting calculations
                float diffuse = Math.Max(0.0f, Vector3.Dot(normal, lightDir));
                float ambientOcclusion = Math.Clamp(Map(hitPoint + normal * 0.5f).X / 0.5f, 0.0f, 1.0f);
                float specular = (float)Math.Pow(Math.Max(Vector3.Dot(Vector3.Reflect(-lightDir, normal), -rd), 0.0), 20.0);

                Vector3 ambient = objectColors[objectId];
                Vector3 finalColor = ambient * ambientOcclusion * diffuse + new Vector3(specular);

                // Distance fog
                float fogAmount = 1.0f - (float)Math.Exp(-0.000011 * Math.Pow(distance, 3.0));
                finalColor = Vector3.Lerp(finalColor, backgroundColor, fogAmount);

                color += finalColor * accumulation;

                // Prepare for next reflection
                rd = Vector3.Reflect(rd, normal);
                accumulation *= 0.5f;
                ro = hitPoint + 0.01f * rd;
            }
            else
            {
                break;
            }
        }

        return color;
    }

    private Vector2 RayMarch(Vector3 ro, Vector3 rd)
    {
        float distance = 0.0f;
        float objectId = 0.0f;

        for (int i = 0; i < ITR; i++)
        {
            Vector3 position = ro + rd * distance;
            Vector2 sceneData = Map(position);

            if (distance > DST || Math.Abs(sceneData.X) < SRF)
                break;

            distance += sceneData.X;
            objectId = sceneData.Y;
        }

        if (distance > DST)
            distance = DST;

        return new Vector2(distance, objectId);
    }

    private Vector2 Map(Vector3 sp)
    {
        float[] distances = new float[NSO];

        // Transform coordinates based on time
        for (int i = 0; i < 2 * (int)_time1; i++)
        {
            sp = Vector3.Abs(sp) - new Vector3(10.2f);
            sp = RotateXZ(sp, 7.79f);
            sp = RotateXY(sp, _time);
        }

        // Create secondary world
        Vector3 spw = sp;
        for (int i = 0; i < 3; i++)
        {
            spw = Vector3.Abs(spw) - new Vector3(4.7f);
            spw = RotateXY(spw, 4.7f);
            spw = RotateYZ(spw, 4.7f);
        }

        // Blend between worlds
        sp = Vector3.Lerp(sp, spw, Math.Clamp(_time - 3.0f, 0.0f, 1.0f));

        // Ground plane with cylindrical features
        float plane = sp.Y + 5.0f;
        plane = Math.Min(plane, Cylinder(sp + new Vector3(0, 5.0f, 0), 0.25f, 4.0f));
        plane = Math.Min(plane, Cylinder(sp + new Vector3(0, 4.75f, 0), 0.25f, 3.0f));
        plane = Math.Min(plane, Cylinder(sp + new Vector3(0, 4.50f, 0), 0.25f, 2.0f));

        distances[0] = plane;

        // Structural elements
        distances[1] = Box(Vector3.Abs(sp + new Vector3(0, 5, 0)) - new Vector3(4, 0, 4),
                          new Vector3(0.2f, 5.0f, 0.2f));

        // Orbital/spherical elements
        Vector3 sp1 = sp;
        sp1.Y -= 2.0f;
        float scale = 1.9f;
        sp1 *= scale;
        sp1 = RotateXZ(sp1, _time);
        sp1 = RotateXY(sp1, _time);

        float orbit = DST;
        for (int i = 0; i < 4; i++)
        {
            sp1 = Vector3.Abs(sp1) - new Vector3(1.2f);
            sp1 = RotateXZ(sp1, 2.0f);
            orbit = SmoothMin(orbit, (sp1.Length() - 0.1f) / scale, 4.0f);
            scale *= 1.0f; // Maintain scale for next iteration
        }
        distances[2] = orbit;

        // Ring structures
        distances[3] = Math.Max(Cylinder(sp1 + new Vector3(0, 4.9f, 0), 0.01f, 4.1f),
                               -Cylinder(sp1 + new Vector3(0, 4.9f, 0), 0.1f, 4.0f));
        distances[4] = Math.Max(Cylinder(sp1 + new Vector3(0, 4.75f, 0), 0.15f, 3.1f),
                               -Cylinder(sp1 + new Vector3(0, 4.65f, 0), 0.2f, 3.0f));
        distances[5] = Math.Max(Cylinder(sp1 + new Vector3(0, 4.6f, 0), 0.25f, 2.1f),
                               -Cylinder(sp1 + new Vector3(0, 4.5f, 0), 0.2f, 2.0f));

        // Glow calculation for rings
        if (Params["enableGlow"].BoolValue)
        {
            _globalGlow += (float)Math.Pow(0.001 / Math.Max(distances[3], 0.001), 5.0);
            _globalGlow += (float)Math.Pow(0.001 / Math.Max(distances[4], 0.001), 5.0);
            _globalGlow += (float)Math.Pow(0.001 / Math.Max(distances[5], 0.001), 5.0);
        }

        // Additional geometric elements
        for (int i = 0; i < 3; i++)
        {
            sp1 = Vector3.Abs(sp1) - new Vector3(6.3f);
        }
        sp1 = RotateXY(sp1, 1.6f);
        sp1 = RotateYZ(sp1, 3.24f);
        distances[6] = Box(sp1, new Vector3(5.0f, 0.1f, 5.0f));

        // Find closest object
        float minDistance = distances[0];
        float objectId = 0.0f;
        for (int i = 1; i < NSO; i++)
        {
            if (distances[i] < minDistance)
            {
                minDistance = distances[i];
                objectId = i;
            }
        }

        return new Vector2(minDistance, objectId);
    }

    private Vector3 CalculateNormal(Vector3 sp)
    {
        Vector2 eps = new Vector2(0.0001f, -0.0001f);
        return Vector3.Normalize(
            eps.X * new Vector3(
                Map(sp + new Vector3(eps.X, 0, 0)).X,
                Map(sp + new Vector3(0, eps.X, 0)).X,
                Map(sp + new Vector3(0, 0, eps.X)).X
            ) + eps.Y * new Vector3(
                Map(sp + new Vector3(eps.Y, 0, 0)).X,
                Map(sp + new Vector3(0, eps.Y, 0)).X,
                Map(sp + new Vector3(0, 0, eps.Y)).X
            )
        );
    }

    private Vector3 ApplyPostProcessing(Vector2 uv, Vector3 color)
    {
        // Kaleidoscope effect
        for (int i = 0; i < 3; i++)
        {
            uv = Vector2.Abs(uv) - new Vector2(0.1f);
            uv = Rotate(uv, _time);
            uv *= 1.23f;
        }

        // Pattern overlay
        float pattern = (float)Math.Sin(uv.X * 4.0f + _time) * 0.5f;
        float mask = SmoothStep(uv.Y - 0.1f, uv.Y, pattern) -
                    SmoothStep(uv.Y, uv.Y + 0.1f, pattern);

        // Apply pattern to color
        return VectorExtensions.Lerp(color, Vector3.One - color, mask);
    }

    // Mathematical helper functions
    private float Cylinder(Vector3 sp, float height, float radius)
    {
        Vector2 d = Vector2.Abs(new Vector2(sp.XZ().Length(), sp.Y)) - new Vector2(radius, height);
        return Math.Min(Math.Max(d.X, d.Y), 0.0f) + VectorExtensions.Max(d, new Vector2(0, 0)).Length();
    }

    private float Box(Vector3 sp, Vector3 dimensions)
    {
        Vector3 d = Vector3.Abs(sp) - dimensions;
        return Math.Max(Math.Max(d.X, d.Y), d.Z);
    }

    private float SmoothMin(float a, float b, float k)
    {
        float h = Math.Clamp(0.5f + 0.5f * (b - a) / k, 0.0f, 1.0f);
        return a * (1 - h) + b * h - k * h * (1 - h);
    }

    private float SmoothStep(float edge0, float edge1, float x)
    {
        float t = Math.Clamp((x - edge0) / (edge1 - edge0), 0.0f, 1.0f);
        return t * t * (3.0f - 2.0f * t);
    }

    private Vector3 RotateXY(Vector3 v, float angle)
    {
        float s = (float)Math.Sin(angle);
        float c = (float)Math.Cos(angle);
        return new Vector3(
            v.X * c - v.Y * s,
            v.X * s + v.Y * c,
            v.Z
        );
    }

    private Vector3 RotateXZ(Vector3 v, float angle)
    {
        float s = (float)Math.Sin(angle);
        float c = (float)Math.Cos(angle);
        return new Vector3(
            v.X * c - v.Z * s,
            v.Y,
            v.X * s + v.Z * c
        );
    }

    private Vector3 RotateYZ(Vector3 v, float angle)
    {
        float s = (float)Math.Sin(angle);
        float c = (float)Math.Cos(angle);
        return new Vector3(
            v.X,
            v.Y * c - v.Z * s,
            v.Y * s + v.Z * c
        );
    }

    private Vector2 Rotate(Vector2 v, float angle)
    {
        float s = (float)Math.Sin(angle);
        float c = (float)Math.Cos(angle);
        return new Vector2(
            v.X * c - v.Y * s,
            v.X * s + v.Y * c
        );
    }
}

// Extension methods for Vector3 to Vector2 conversion
public static class VectorExtensions
{
    public static Vector2 XZ(this Vector3 v) => new Vector2(v.X, v.Z);
    public static Vector2 Max(Vector2 a, Vector2 b) =>
        new Vector2(Math.Max(a.X, b.X), Math.Max(a.Y, b.Y));

    // Additional vector helper methods
    public static Vector3 Lerp(Vector3 a, Vector3 b, float t) =>
        new Vector3(
            a.X + (b.X - a.X) * t,
            a.Y + (b.Y - a.Y) * t,
            a.Z + (b.Z - a.Z) * t
        );
}
