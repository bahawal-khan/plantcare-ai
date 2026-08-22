# PlantCare AI — Frontend Specification

## Framework
Next.js + TypeScript.

## Design Direction
Premium AI + nature SaaS:
- emerald/deep-green accents
- clean white/light surfaces
- subtle gradients
- botanical imagery
- rounded cards
- tasteful glass effects
- strong typography
- whitespace
- subtle animations
- mobile-first responsiveness

Use `ui-references/` as visual guidance.

## Pages
1. `/` Home
2. `/diagnose` Diagnose
3. result state/route
4. `/diseases` Disease Library
5. `/diseases/[id]` Disease Detail
6. `/how-it-works`
7. `/about`

## Global
Navbar:
- logo
- Home
- Diseases
- How It Works
- About
- Diagnose CTA

Footer:
- brand
- quick links
- features
- support
- clickable GitHub
- clickable LinkedIn
- clickable email

Keep real URLs centralized in a configuration/constants layer.

## Diagnose
- drag/drop upload
- file picker
- image preview
- validation
- loading state
- scanning animation
- API call

## Result
- plant
- disease
- confidence
- top predictions
- original image
- Grad-CAM image
- disease information
- responsible-use disclaimer

## Disease Library
- search
- plant filter
- disease cards
- responsive grid

## Disease Detail
- disease image/content
- symptoms
- causes
- prevention
- general management
- affected plant
- disclaimer

## Rules
Do not invent accuracy statistics or user counts. Use verified/configured data or remove the metric.
