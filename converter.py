"""
Nano Banana 2 JSON Prompt Converter
Converts a plain-text image description into a structured JSON prompt.
No LLMs, no API calls — pure keyword matching.

Usage:
    python converter.py "a woman with red hair in a coffee shop, warm lighting"
    python converter.py --pretty "portrait of a dog on a beach at golden hour"
"""

import json
import re
import sys
import argparse

# ---------------------------------------------------------------------------
# Keyword maps
# Keys are sorted longest-first at runtime so "mirror selfie" matches before "selfie".
# ---------------------------------------------------------------------------

LIGHTING_MAP = {
    "golden hour":      {"type": "golden hour",         "direction": "horizontal",   "color_temperature": "3200K", "intensity": 0.70},
    "hard direct flash":{"type": "hard direct flash",   "direction": "front",        "color_temperature": "5500K", "intensity": 0.90},
    "ring light":       {"type": "ring light",           "direction": "front-on",     "color_temperature": "5000K", "intensity": 0.75},
    "soft box":         {"type": "studio softbox",       "direction": "45-degree",    "color_temperature": "5000K", "intensity": 0.80},
    "softbox":          {"type": "studio softbox",       "direction": "45-degree",    "color_temperature": "5000K", "intensity": 0.80},
    "candlelight":      {"type": "candlelight",          "direction": "ambient",      "color_temperature": "2200K", "intensity": 0.40},
    "firelight":        {"type": "firelight",            "direction": "front-low",    "color_temperature": "2200K", "intensity": 0.50},
    "backlit":          {"type": "backlit",              "direction": "back",         "color_temperature": "5600K", "intensity": 0.70},
    "silhouette":       {"type": "strong backlit",       "direction": "back",         "color_temperature": "4000K", "intensity": 0.90},
    "overcast":         {"type": "overcast diffused",    "direction": "overhead",     "color_temperature": "6500K", "intensity": 0.50},
    "diffused":         {"type": "soft diffused",        "direction": "ambient",      "color_temperature": "4500K", "intensity": 0.60},
    "dramatic":         {"type": "dramatic chiaroscuro", "direction": "side",         "color_temperature": "3500K", "intensity": 0.40},
    "sunrise":          {"type": "sunrise",              "direction": "horizontal",   "color_temperature": "3400K", "intensity": 0.65},
    "sunset":           {"type": "sunset",               "direction": "horizontal",   "color_temperature": "3200K", "intensity": 0.65},
    "studio":           {"type": "studio softbox",       "direction": "45-degree",    "color_temperature": "5000K", "intensity": 0.80},
    "neon":             {"type": "neon ambient",         "direction": "ambient",      "color_temperature": "6500K", "intensity": 0.60},
    "harsh":            {"type": "hard direct",          "direction": "top-down",     "color_temperature": "5000K", "intensity": 0.85},
    "flash":            {"type": "hard direct flash",    "direction": "front",        "color_temperature": "5500K", "intensity": 0.90},
    "moody":            {"type": "low-key dramatic",     "direction": "side",         "color_temperature": "3000K", "intensity": 0.35},
    "dark":             {"type": "low-key",              "direction": "side",         "color_temperature": "3000K", "intensity": 0.30},
    "warm":             {"type": "warm ambient",         "direction": "ambient",      "color_temperature": "3200K", "intensity": 0.70},
    "cool":             {"type": "cool ambient",         "direction": "ambient",      "color_temperature": "7000K", "intensity": 0.65},
    "soft":             {"type": "soft diffused",        "direction": "ambient",      "color_temperature": "4500K", "intensity": 0.60},
    "natural":          {"type": "natural daylight",     "direction": "ambient",      "color_temperature": "5600K", "intensity": 0.65},
}

CAMERA_MAP = {
    "extreme close-up": {"lens": "100mm macro", "aperture": "f/2.8",  "height": "eye-level"},
    "bird's eye":       {"lens": "35mm",         "aperture": "f/5.6",  "height": "bird's-eye"},
    "birds eye":        {"lens": "35mm",         "aperture": "f/5.6",  "height": "bird's-eye"},
    "wide angle":       {"lens": "24mm",         "aperture": "f/8",    "height": "eye-level"},
    "mirror selfie":    {"lens": "28mm",         "aperture": "f/2.0",  "height": "eye-level"},
    "low angle":        {"lens": "24mm",         "aperture": "f/5.6",  "height": "low-angle"},
    "full body":        {"lens": "35mm",         "aperture": "f/4",    "height": "eye-level"},
    "full-body":        {"lens": "35mm",         "aperture": "f/4",    "height": "eye-level"},
    "head shot":        {"lens": "85mm",         "aperture": "f/1.8",  "height": "eye-level"},
    "headshot":         {"lens": "85mm",         "aperture": "f/1.8",  "height": "eye-level"},
    "close-up":         {"lens": "100mm",        "aperture": "f/2.8",  "height": "eye-level"},
    "closeup":          {"lens": "100mm",        "aperture": "f/2.8",  "height": "eye-level"},
    "telephoto":        {"lens": "135mm",        "aperture": "f/2.8",  "height": "eye-level"},
    "overhead":         {"lens": "35mm",         "aperture": "f/5.6",  "height": "overhead"},
    "editorial":        {"lens": "85mm",         "aperture": "f/2.8",  "height": "eye-level"},
    "portrait":         {"lens": "85mm",         "aperture": "f/1.8",  "height": "eye-level"},
    "landscape":        {"lens": "24mm",         "aperture": "f/11",   "height": "eye-level"},
    "fashion":          {"lens": "85mm",         "aperture": "f/2.8",  "height": "eye-level"},
    "candid":           {"lens": "35mm",         "aperture": "f/2.8",  "height": "eye-level"},
    "street":           {"lens": "35mm",         "aperture": "f/2.8",  "height": "eye-level"},
    "selfie":           {"lens": "28mm",         "aperture": "f/2.0",  "height": "arm-length"},
    "product":          {"lens": "85mm",         "aperture": "f/8",    "height": "eye-level"},
    "macro":            {"lens": "100mm macro",  "aperture": "f/4",    "height": "eye-level"},
    "aerial":           {"lens": "24mm",         "aperture": "f/8",    "height": "aerial"},
    "wide":             {"lens": "24mm",         "aperture": "f/8",    "height": "eye-level"},
}

STYLE_MAP = {
    "black and white":      {"aesthetic": "black and white photography",  "color_grade": "monochrome"},
    "oil painting":         {"aesthetic": "oil painting",                 "color_grade": "rich oil palette"},
    "hyper-realistic":      {"aesthetic": "hyperrealistic photography",   "color_grade": "natural accurate tones"},
    "hyper realistic":      {"aesthetic": "hyperrealistic photography",   "color_grade": "natural accurate tones"},
    "hyperrealistic":       {"aesthetic": "hyperrealistic photography",   "color_grade": "natural accurate tones"},
    "photorealistic":       {"aesthetic": "photorealistic",               "color_grade": "natural accurate tones"},
    "documentary":          {"aesthetic": "documentary",                   "color_grade": "natural tones"},
    "watercolor":           {"aesthetic": "watercolor",                    "color_grade": "soft watercolor washes"},
    "minimalist":           {"aesthetic": "minimalist",                    "color_grade": "clean neutral tones"},
    "minimalistic":         {"aesthetic": "minimalist",                    "color_grade": "clean neutral tones"},
    "cyberpunk":            {"aesthetic": "cyberpunk",                     "color_grade": "neon-saturated dark"},
    "cinematic":            {"aesthetic": "cinematic",                     "color_grade": "film-grade color"},
    "editorial":            {"aesthetic": "editorial",                     "color_grade": "high-contrast editorial"},
    "vintage":              {"aesthetic": "vintage film",                  "color_grade": "faded film grain"},
    "fashion":              {"aesthetic": "high-fashion editorial",        "color_grade": "desaturated editorial"},
    "surreal":              {"aesthetic": "surrealist",                    "color_grade": "dreamlike saturation"},
    "fantasy":              {"aesthetic": "fantasy art",                   "color_grade": "rich fantasy palette"},
    "painting":             {"aesthetic": "digital painting",              "color_grade": "painterly tones"},
    "illustration":         {"aesthetic": "digital illustration",          "color_grade": "vibrant illustration"},
    "sketch":               {"aesthetic": "pencil sketch",                 "color_grade": "monochrome sketch"},
    "anime":                {"aesthetic": "anime illustration",            "color_grade": "vibrant anime palette"},
    "realistic":            {"aesthetic": "realistic photography",         "color_grade": "natural tones"},
    "product":              {"aesthetic": "commercial product photography","color_grade": "clean commercial"},
    "noir":                 {"aesthetic": "film noir",                     "color_grade": "high-contrast monochrome"},
    "neon":                 {"aesthetic": "cyberpunk neon",                "color_grade": "neon-saturated dark"},
    "film":                 {"aesthetic": "analog film",                   "color_grade": "film grain with halation"},
    "b&w":                  {"aesthetic": "black and white photography",   "color_grade": "monochrome"},
    "ugc":                  {"aesthetic": "user-generated content",        "color_grade": "natural mobile camera"},
}

FRAMING_MAP = {
    "extreme close-up": "extreme close-up",
    "medium close-up":  "medium close-up",
    "head and shoulders": "head and shoulders",
    "full body":        "full body",
    "full-body":        "full body",
    "half body":        "half-body",
    "waist up":         "waist-up",
    "wide shot":        "wide shot",
    "close-up":         "close-up",
    "closeup":          "close-up",
    "headshot":         "headshot",
    "medium shot":      "medium shot",
    "medium":           "medium shot",
    "bust":             "bust shot",
}

TIME_OF_DAY_MAP = {
    "golden hour": "golden hour",
    "blue hour":   "blue hour",
    "sunrise":     "sunrise",
    "sunset":      "sunset",
    "midday":      "midday",
    "midnight":    "midnight",
    "morning":     "early morning",
    "afternoon":   "afternoon",
    "evening":     "evening",
    "nighttime":   "nighttime",
    "night":       "nighttime",
    "dawn":        "dawn",
    "dusk":        "dusk",
    "daytime":     "daytime",
}

ASPECT_RATIO_MAP = {
    "widescreen":  "21:9",
    "cinematic":   "2.35:1",
    "landscape":   "16:9",
    "vertical":    "9:16",
    "portrait":    "4:5",
    "story":       "9:16",
    "square":      "1:1",
    "wide":        "16:9",
}

LOCATION_HINTS = [
    "coffee shop", "cafe", "forest", "jungle", "beach", "ocean", "city",
    "urban", "studio", "park", "mountain", "desert", "rain", "snow",
    "office", "bedroom", "kitchen", "restaurant", "bar", "gym", "rooftop",
    "field", "garden", "airport", "subway", "alley", "warehouse", "mansion",
    "castle", "ruins", "abandoned building", "neon city", "street",
    "flower field", "cliffside", "lakeside", "riverbank",
]

DEFAULT_NEGATIVES = [
    "plastic skin",
    "smoothing filters",
    "beautification",
    "AI artifacts",
    "anatomy normalization",
    "oversaturated",
    "watermark",
    "text overlay",
]

# Prepositions used to split subject from environment
SPLIT_TOKENS = [
    "in front of", "on top of", "next to", "inside", "outside",
    "beside", "behind", "against", "near", "with", "wearing",
    "holding", "sitting", "standing", "lying", "leaning",
    " in ", " at ", " on ", " by ", " under ", " over ",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _match(prompt_lower: str, keyword_map: dict):
    """Return the first matching key-value pair, longest key wins."""
    for key in sorted(keyword_map, key=len, reverse=True):
        if key in prompt_lower:
            return key, keyword_map[key]
    return None, None


def _extract_subject(prompt: str) -> str:
    """Best-effort subject extraction without NLP."""
    text = prompt.strip()
    for token in sorted(SPLIT_TOKENS, key=len, reverse=True):
        idx = text.lower().find(token)
        if idx > 0:
            text = text[:idx].strip()
            break

    # Strip leading style/mood adjectives that belong in other fields
    noise = [
        "cinematic", "dramatic", "moody", "vintage", "editorial",
        "fashion", "beautiful", "stunning", "epic", "hyper-realistic",
    ]
    for word in noise:
        text = re.sub(r"\b" + re.escape(word) + r"\b", "", text, flags=re.IGNORECASE)

    text = re.sub(r"\s{2,}", " ", text).strip(" ,.")
    return text if text else prompt.strip()


def _extract_location(prompt_lower: str) -> str:
    for loc in sorted(LOCATION_HINTS, key=len, reverse=True):
        if loc in prompt_lower:
            return loc
    return ""


def _extract_appearance(prompt: str) -> list[str]:
    """Pull out likely physical descriptors (color + noun pairs, adjectives before body parts)."""
    color_pattern = re.compile(
        r"\b(red|blonde|brown|black|white|silver|gray|blue|green|purple|pink|auburn|dark|light|curly|straight|long|short|wavy)\s+(hair|eyes|skin|beard|freckles|tattoo)\b",
        re.IGNORECASE,
    )
    matches = color_pattern.findall(prompt)
    return [f"{adj} {noun}" for adj, noun in matches]


# ---------------------------------------------------------------------------
# Main converter
# ---------------------------------------------------------------------------

def convert(prompt: str) -> dict:
    pl = prompt.lower()

    # Task
    edit_words = {"edit", "change", "replace", "modify", "transform", "remove", "add to"}
    task = "edit_image" if any(w in pl for w in edit_words) else "generate_image"

    # Lighting
    _, lighting = _match(pl, LIGHTING_MAP)
    if not lighting:
        lighting = {"type": "natural daylight", "direction": "ambient",
                    "color_temperature": "5600K", "intensity": 0.65}

    # Camera
    _, camera = _match(pl, CAMERA_MAP)
    if not camera:
        camera = {"lens": "50mm", "aperture": "f/2.0", "height": "eye-level"}

    # Style
    _, style = _match(pl, STYLE_MAP)
    if not style:
        style = {"aesthetic": "realistic photography", "color_grade": "natural tones"}

    # Composition
    _, framing_val = _match(pl, FRAMING_MAP)
    framing = framing_val if framing_val else "medium shot"
    aperture = camera.get("aperture", "f/2.0")
    shallow_apertures = {"f/1.4", "f/1.8", "f/2.0", "f/2.8"}
    depth = "shallow" if aperture in shallow_apertures else "deep"

    # Environment
    location = _extract_location(pl)
    _, time_of_day = _match(pl, TIME_OF_DAY_MAP)
    if not time_of_day:
        time_of_day = "daytime"

    # Aspect ratio
    _, aspect_ratio = _match(pl, ASPECT_RATIO_MAP)
    if not aspect_ratio:
        aspect_ratio = "1:1"

    # Subject
    subject_desc = _extract_subject(prompt)
    appearance = _extract_appearance(prompt)

    return {
        "task": task,
        "Objective": prompt.strip(),
        "subject": {
            "description": subject_desc,
            "appearance": ", ".join(appearance) if appearance else "",
            "expression": "natural",
            "clothing": "",
        },
        "lighting": lighting,
        "camera": camera,
        "composition": {
            "framing": framing,
            "depth": depth,
        },
        "style": style,
        "environment": {
            "location": location,
            "time_of_day": time_of_day,
            "weather": "",
        },
        "negative_constraints": DEFAULT_NEGATIVES,
        "settings": {
            "resolution": "2048x2048",
            "aspect_ratio": aspect_ratio,
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert a plain-text image description to a Nano Banana 2 JSON prompt."
    )
    parser.add_argument("prompt", nargs="?", help="The image description to convert")
    parser.add_argument(
        "--pretty", action="store_true", default=True, help="Pretty-print JSON (default: on)"
    )
    parser.add_argument(
        "--compact", action="store_true", help="Output compact JSON (overrides --pretty)"
    )
    args = parser.parse_args()

    if not args.prompt:
        print("Usage: python converter.py \"your image description here\"")
        sys.exit(1)

    result = convert(args.prompt)
    indent = None if args.compact else 2
    print(json.dumps(result, indent=indent))


if __name__ == "__main__":
    main()
