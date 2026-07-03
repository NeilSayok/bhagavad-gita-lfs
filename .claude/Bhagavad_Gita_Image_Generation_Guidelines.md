# Bhagavad Gita Image Generation Prompt Enhancements

## Global Consistency Rule

> All illustrations generated for the Bhagavad Gita app must share a
> unified visual language inspired by Indian classical painting
> traditions, as though they were created by the same master artist in a
> single illuminated manuscript. Every illustration should maintain
> consistency in color palette, brushwork, proportions, ornamentation,
> textures, and artistic style across all 700+ shlokas.

------------------------------------------------------------------------

## Updated `art_style` Section

``` json
{
  "art_style": {
    "primary_style": "Traditional Indian Classical Painting",
    "inspiration": [
      "Rajasthani Miniature Painting",
      "Pahari Miniature Painting",
      "Kangra School",
      "Tanjore Painting",
      "Mysore Painting",
      "Ajanta Cave Murals",
      "Traditional Temple Murals of Kerala"
    ],
    "overall_feel": "Sacred, timeless, elegant, devotional, historically authentic",
    "brushwork": "Fine hand-painted brush strokes with intricate detailing",
    "textures": "Natural handmade paper, parchment, cloth canvas, subtle pigment texture, gold leaf accents where appropriate",
    "color_palette": {
      "primary": [
        "Indian Red",
        "Ochre",
        "Saffron",
        "Deep Indigo",
        "Emerald Green",
        "Lotus Pink",
        "Turquoise",
        "Burnished Gold",
        "Ivory",
        "Natural Earth Browns"
      ],
      "avoid": [
        "Neon colors",
        "Artificial gradients",
        "Modern HDR saturation",
        "Synthetic lighting"
      ]
    },
    "lighting": "Soft natural illumination inspired by sunrise, sunset, oil lamps, and divine radiance",
    "composition": "Balanced classical Indian composition with ornamental framing and visual harmony",
    "ornamentation": [
      "Traditional floral borders",
      "Lotus motifs",
      "Temple architecture",
      "Mandala-inspired geometry",
      "Subtle Sanskrit decorative elements",
      "Traditional Indian textile patterns"
    ],
    "character_rendering": {
      "faces": "Graceful, serene, expressive, idealized according to Indian classical aesthetics",
      "eyes": "Large expressive eyes conveying spiritual emotion",
      "posture": "Elegant and symbolic rather than exaggerated realism",
      "proportions": "Inspired by classical Indian sculpture and miniature paintings"
    },
    "environment": "Historically authentic landscapes of ancient Bharat with forests, rivers, palaces, temples, mountains, and the Kurukshetra battlefield depicted according to classical Indian artistic traditions.",
    "quality": "Museum-quality masterpiece",
    "finish": "Hand-painted traditional Indian artwork rather than digital illustration"
  },

  "style_rules": [
    "The artwork should resemble a masterpiece painted by a classical Indian artist.",
    "Prioritize Indian artistic traditions over Western realism.",
    "Avoid Hollywood fantasy aesthetics.",
    "Avoid comic book styles.",
    "Avoid anime or manga influences.",
    "Avoid 3D CGI rendering.",
    "Avoid hyper-realistic photography.",
    "The final artwork should feel suitable for a sacred scripture.",
    "Maintain visual consistency across all generated images so the app feels like a single illustrated manuscript.",
    "Every image should look like it belongs in an illuminated ancient Indian manuscript."
  ],

  "negative_prompt": [
    "photorealistic",
    "3D render",
    "CGI",
    "Pixar",
    "Disney",
    "anime",
    "manga",
    "comic",
    "Marvel",
    "Hollywood fantasy",
    "science fiction",
    "cyberpunk",
    "modern clothing",
    "modern weapons",
    "guns",
    "cars",
    "electric lights",
    "glass skyscrapers",
    "western armor",
    "plastic textures",
    "HDR",
    "lens flare",
    "digital painting",
    "low quality",
    "text",
    "logo",
    "watermark"
  ]
}
```

------------------------------------------------------------------------

## Updated `output_format` Section

``` json
{
  "output_format": {
    "title": "Short descriptive title",
    "scene_summary": "A concise explanation of the scene being illustrated.",
    "philosophical_interpretation": "Explain how the artwork conveys the deeper meaning of the shloka.",
    "images": {
      "portrait_9_16": {
        "purpose": "Full-screen illustration for the Bhagavad Gita app reading experience.",
        "aspect_ratio": "9:16",
        "composition_rules": [
          "Use a strong vertical composition.",
          "The primary subject should occupy the middle third of the frame.",
          "Leave subtle breathing room at the top and bottom for UI overlays if needed.",
          "Ensure the focal point remains clearly visible on mobile screens.",
          "Create cinematic depth while maintaining classical Indian artistic balance."
        ],
        "image_prompt": "Generate one highly detailed AI image prompt (250–600 words) optimized for a vertical 9:16 composition."
      },
      "square_1_1": {
        "purpose": "Verse card, thumbnail, social sharing, chapter preview.",
        "aspect_ratio": "1:1",
        "composition_rules": [
          "Create a perfectly balanced centered composition.",
          "Ensure all important visual elements fit comfortably inside the square frame.",
          "Avoid cropping important symbols or characters.",
          "Maintain strong visual symmetry inspired by Indian miniature paintings."
        ],
        "image_prompt": "Generate one highly detailed AI image prompt (250–600 words) optimized for a square 1:1 composition."
      },
      "landscape_16_9": {
        "purpose": "Chapter banner, hero header, tablet/desktop background, wide cinematic scene.",
        "aspect_ratio": "16:9",
        "composition_rules": [
          "Use a strong horizontal composition with cinematic wide framing.",
          "Distribute key elements across the width while keeping a clear focal point.",
          "Use foreground, midground and background layers to create depth.",
          "Leave subtle breathing room at the sides for UI overlays if needed.",
          "Maintain classical Indian artistic balance across the wide frame."
        ],
        "image_prompt": "Generate one highly detailed AI image prompt (250–600 words) optimized for a wide landscape 16:9 composition."
      }
    },
    "shared_negative_prompt": "Comma-separated negative prompt shared by both images.",
    "style_tags": [
      "Traditional Indian Classical Painting",
      "Rajasthani Miniature",
      "Kangra School",
      "Pahari Painting",
      "Tanjore",
      "Ajanta Murals",
      "Bhagavad Gita",
      "Ancient Bharat",
      "Museum Quality",
      "Hand Painted"
    ]
  }
}
```

------------------------------------------------------------------------

## Recommended Workflow

``` text
Shloka
        │
        ▼
Understand Meaning
        │
        ▼
Create ONE Scene Concept
        │
 ┌──────┴────────┐
 ▼               ▼
9:16 Layout    1:1 Layout
Vertical       Square
Same characters
Same colors
Same symbolism
Same art style
Different framing
```

Generate one unified scene concept first, then compose it separately for
the 9:16 and 1:1 aspect ratios. This ensures both images represent the
same moment while being optimized for their intended use in the app.
