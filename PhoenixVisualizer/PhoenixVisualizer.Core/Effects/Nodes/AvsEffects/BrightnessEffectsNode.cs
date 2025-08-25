using System;
using System.Collections.Generic;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class BrightnessEffectsNode : BaseEffectNode
    {
        public bool Enabled { get; set; } = true;
        public float Brightness { get; set; } = 1.0f;

        public BrightnessEffectsNode()
        {
            Name = "Brightness Effects";
            Description = "Adjusts image brightness with configurable multiplier";
            Category = "Color Effects";
        }

        protected override void InitializePorts()
        {
            _inputPorts.Add(new EffectPort("Image", typeof(ImageBuffer), true, null, "Source image for brightness adjustment"));
            _outputPorts.Add(new EffectPort("Output", typeof(ImageBuffer), false, null, "Brightness-adjusted output image"));
        }

        protected override object ProcessCore(Dictionary<string, object> inputs, AudioFeatures audioFeatures)
        {
            if (!inputs.TryGetValue("Image", out var input) || input is not ImageBuffer imageBuffer)
            {
                return GetDefaultOutput();
            }

            if (!Enabled)
            {
                return imageBuffer;
            }

            var output = new ImageBuffer(imageBuffer.Width, imageBuffer.Height);
            for (int y = 0; y < imageBuffer.Height; y++)
            {
                for (int x = 0; x < imageBuffer.Width; x++)
                {
                    var c = imageBuffer.GetPixel(x, y);
                    int r = (int)Math.Clamp((c & 0xFF) * Brightness, 0, 255);
                    int g = (int)Math.Clamp(((c >> 8) & 0xFF) * Brightness, 0, 255);
                    int b = (int)Math.Clamp(((c >> 16) & 0xFF) * Brightness, 0, 255);
                    output.SetPixel(x, y, (b << 16) | (g << 8) | r);
                }
            }

            return output;
        }
    }
}
