using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace PhoenixVisualizer.Core.Nodes;

/// <summary>
/// AVS Converter - Handles loading and converting legacy Winamp AVS preset files
/// Supports binary format parsing and conversion to Phoenix JSON schema
/// </summary>
public static class AvsConverter
{
    /// <summary>
    /// Load and convert an AVS preset file to PHX JSON format
    /// </summary>
    public static string LoadAvs(string path)
    {
        using var fs = new FileStream(path, FileMode.Open, FileAccess.Read);
        using var br = new BinaryReader(fs);

        try
        {
            return ParseAvsPreset(br);
        }
        catch (Exception ex)
        {
            // Return error information in PHX format
            return CreateErrorPhx($"Error loading AVS preset: {ex.Message}");
        }
    }

    /// <summary>
    /// Save PHX JSON as AVS binary format (reverse conversion)
    /// </summary>
    public static void SaveAvs(string path, string phxJson)
    {
        var doc = JsonDocument.Parse(phxJson);
        using var fs = new FileStream(path, FileMode.Create, FileAccess.Write);
        using var bw = new BinaryWriter(fs);

        WriteAvsHeader(bw);
        WritePhxContent(bw, doc.RootElement);
    }

    private static string ParseAvsPreset(BinaryReader br)
    {
        // Read and verify AVS header
        var header = ReadAvsHeader(br);
        if (!IsValidAvsHeader(header))
        {
            throw new InvalidDataException("Invalid AVS preset file header");
        }

        // Parse effect configuration blocks
        var effects = ParseAvsEffects(br);

        // Extract code blocks
        var codeBlocks = ExtractCodeBlocks(effects);

        // Build PHX JSON structure
        var phxStructure = new
        {
            version = "1.0",
            name = "Imported AVS Preset",
            description = $"Imported from AVS preset with {effects.Count} effects",
            init = codeBlocks.Init,
            frame = codeBlocks.Frame,
            point = codeBlocks.Point,
            beat = codeBlocks.Beat,
            clearEveryFrame = codeBlocks.ClearEveryFrame,
            effects = effects
        };

        return JsonSerializer.Serialize(phxStructure, new JsonSerializerOptions
        {
            WriteIndented = true
        });
    }

    private static string ReadAvsHeader(BinaryReader br)
    {
        // AVS headers are typically 32 bytes, null-terminated
        var headerBytes = br.ReadBytes(32);
        var header = System.Text.Encoding.ASCII.GetString(headerBytes).TrimEnd('\0');
        return header;
    }

    private static bool IsValidAvsHeader(string header)
    {
        // Common AVS header patterns
        return header.Contains("Nullsoft AVS") ||
               header.Contains("avs") ||
               header.Contains("AVS");
    }

    private static List<AvsEffect> ParseAvsEffects(BinaryReader br)
    {
        var effects = new List<AvsEffect>();

        try
        {
            // Read effect count (usually first 4 bytes after header)
            int effectCount = br.ReadInt32();

            for (int i = 0; i < effectCount; i++)
            {
                var effect = ParseAvsEffect(br);
                if (effect != null)
                {
                    effects.Add(effect);
                }
            }
        }
        catch (EndOfStreamException)
        {
            // File ended unexpectedly, return what we have
        }

        return effects;
    }

    private static AvsEffect? ParseAvsEffect(BinaryReader br)
    {
        try
        {
            // Read effect ID and size
            int effectId = br.ReadInt32();
            int effectSize = br.ReadInt32();

            if (effectSize < 0 || effectSize > 1024 * 1024) // Sanity check
            {
                // Skip invalid effect
                br.BaseStream.Seek(effectSize, SeekOrigin.Current);
                return null;
            }

            // Read effect data
            byte[] effectData = br.ReadBytes(effectSize);

            return new AvsEffect
            {
                Id = effectId,
                Size = effectSize,
                Data = effectData,
                Type = MapAvsEffectToPhx(effectId),
                IsMapped = IsKnownAvsEffect(effectId)
            };
        }
        catch
        {
            return null;
        }
    }

    private static bool IsKnownAvsEffect(int effectId)
    {
        // Known AVS effect IDs from various AVS versions
        int[] knownIds = {
            0x01, 0x02, 0x03, 0x04, 0x05, // Basic effects
            0x10, 0x11, 0x12, 0x13, 0x14, // Render effects
            0x20, 0x21, 0x22, 0x23, 0x24, // Trans effects
            0x30, 0x31, 0x32, 0x33, 0x34  // Misc effects
        };

        return Array.Exists(knownIds, id => id == effectId);
    }

    private static string MapAvsEffectToPhx(int effectId)
    {
        switch (effectId)
        {
            case 0x01:
                return "superscope"; // Superscope/point script
            case 0x02:
                return "trans"; // Trans/per frame
            case 0x03:
                return "init"; // Init code
            case 0x04:
                return "beat"; // On beat
            case 0x05:
                return "clear"; // Clear every frame toggle
            case 0x10:
                return "blur";
            case 0x11:
                return "mosaic";
            case 0x12:
                return "water";
            case 0x13:
                return "brightness";
            case 0x14:
                return "contrast";
            case 0x20:
                return "zoom";
            case 0x21:
                return "rotate";
            case 0x22:
                return "translate";
            case 0x23:
                return "scale";
            case 0x24:
                return "flip";
            default:
                return $"avs_raw_{effectId:X}"; // Unknown effect, preserve as raw
        }
    }

    private static CodeBlocks ExtractCodeBlocks(List<AvsEffect> effects)
    {
        var codeBlocks = new CodeBlocks();

        foreach (var effect in effects)
        {
            string code = ExtractStringFromData(effect.Data);

            switch (effect.Id)
            {
                case 0x01: // Superscope/point script
                    codeBlocks.Point = code;
                    break;
                case 0x02: // Trans/per frame
                    codeBlocks.Frame = code;
                    break;
                case 0x03: // Init code
                    codeBlocks.Init = code;
                    break;
                case 0x04: // On beat
                    codeBlocks.Beat = code;
                    break;
                case 0x05: // Clear every frame toggle
                    codeBlocks.ClearEveryFrame = effect.Data.Length > 0 && effect.Data[0] != 0;
                    break;
            }
        }

        return codeBlocks;
    }

    private static string ExtractStringFromData(byte[] data)
    {
        if (data == null || data.Length == 0)
            return "// No code";

        try
        {
            // Try to extract null-terminated string
            int nullIndex = Array.IndexOf(data, (byte)0);
            if (nullIndex >= 0)
            {
                return System.Text.Encoding.ASCII.GetString(data, 0, nullIndex);
            }
            else
            {
                // No null terminator, try to decode entire array
                return System.Text.Encoding.ASCII.GetString(data);
            }
        }
        catch
        {
            return "// Unable to decode code block";
        }
    }

    private static string CreateErrorPhx(string errorMessage)
    {
        var errorStructure = new
        {
            version = "1.0",
            name = "AVS Import Error",
            description = errorMessage,
            init = $"// {errorMessage}",
            frame = "// Error occurred during import",
            point = "// Please check the original AVS file",
            beat = "// Import failed",
            clearEveryFrame = true,
            effects = new[] {
                new {
                    type = "error",
                    error = errorMessage
                }
            }
        };

        return JsonSerializer.Serialize(errorStructure, new JsonSerializerOptions
        {
            WriteIndented = true
        });
    }

    private static void WriteAvsHeader(BinaryWriter bw)
    {
        // Write AVS header
        var header = "Nullsoft AVS Preset";
        var headerBytes = new byte[32];
        System.Text.Encoding.ASCII.GetBytes(header, 0, header.Length, headerBytes, 0);
        bw.Write(headerBytes);
    }

    private static void WritePhxContent(BinaryWriter bw, JsonElement root)
    {
        var effects = new List<object>();

        // Count effects and code blocks
        int effectCount = 0;

        if (root.TryGetProperty("effects", out var effectsArray))
        {
            effectCount += effectsArray.GetArrayLength();
        }

        // Add code blocks as effects
        effectCount += 4; // init, frame, point, beat

        // Write effect count
        bw.Write(effectCount);

        // Write code blocks
        WriteCodeEffect(bw, 0x03, root, "init");   // Init
        WriteCodeEffect(bw, 0x02, root, "frame");  // Frame
        WriteCodeEffect(bw, 0x01, root, "point");  // Point
        WriteCodeEffect(bw, 0x04, root, "beat");   // Beat

        // Write clear flag
        if (root.TryGetProperty("clearEveryFrame", out var clear))
        {
            WriteFlagEffect(bw, 0x05, clear.GetBoolean());
        }

        // Write actual effects
        if (root.TryGetProperty("effects", out effectsArray))
        {
            foreach (var effect in effectsArray.EnumerateArray())
            {
                WritePhxEffect(bw, effect);
            }
        }
    }

    private static void WriteCodeEffect(BinaryWriter bw, int effectId, JsonElement root, string propertyName)
    {
        if (root.TryGetProperty(propertyName, out var codeElement))
        {
            string code = codeElement.GetString() ?? "";
            var codeBytes = System.Text.Encoding.ASCII.GetBytes(code);

            bw.Write(effectId);
            bw.Write(codeBytes.Length);
            bw.Write(codeBytes);
        }
    }

    private static void WriteFlagEffect(BinaryWriter bw, int effectId, bool flag)
    {
        bw.Write(effectId);
        bw.Write(1);
        bw.Write(flag ? (byte)1 : (byte)0);
    }

    private static void WritePhxEffect(BinaryWriter bw, JsonElement effect)
    {
        if (effect.TryGetProperty("type", out var typeElement))
        {
            string type = typeElement.GetString() ?? "unknown";

            // Map PHX type back to AVS ID
            int avsId = MapPhxTypeToAvs(type);

            if (type.StartsWith("avs_raw_"))
            {
                // Raw AVS effect, extract original data
                if (effect.TryGetProperty("blob", out var blobElement))
                {
                    string blobStr = blobElement.GetString() ?? "";
                    var blobBytes = Convert.FromBase64String(blobStr);

                    bw.Write(avsId);
                    bw.Write(blobBytes.Length);
                    bw.Write(blobBytes);
                }
            }
            else
            {
                // Convert PHX effect to basic AVS representation
                string effectData = type;
                var dataBytes = System.Text.Encoding.ASCII.GetBytes(effectData);

                bw.Write(avsId);
                bw.Write(dataBytes.Length);
                bw.Write(dataBytes);
            }
        }
    }

    private static int MapPhxTypeToAvs(string phxType)
    {
        switch (phxType)
        {
            case "superscope": return 0x01;
            case "trans": return 0x02;
            case "init": return 0x03;
            case "beat": return 0x04;
            case "clear": return 0x05;
            case "blur": return 0x10;
            case "mosaic": return 0x11;
            case "water": return 0x12;
            case "brightness": return 0x13;
            case "contrast": return 0x14;
            default:
                // Try to parse raw AVS ID
                if (phxType.StartsWith("avs_raw_"))
                {
                    if (int.TryParse(phxType.Substring(8), System.Globalization.NumberStyles.HexNumber, null, out int id))
                    {
                        return id;
                    }
                }
                return 0x99; // Generic placeholder
        }
    }

    // Helper classes
    private class AvsEffect
    {
        public int Id { get; set; }
        public int Size { get; set; }
        public byte[] Data { get; set; } = Array.Empty<byte>();
        public string Type { get; set; } = "";
        public bool IsMapped { get; set; }
    }

    private class CodeBlocks
    {
        public string Init { get; set; } = "// Init code";
        public string Frame { get; set; } = "// Frame code";
        public string Point { get; set; } = "// Point code";
        public string Beat { get; set; } = "// Beat code";
        public bool ClearEveryFrame { get; set; } = true;
    }
}
