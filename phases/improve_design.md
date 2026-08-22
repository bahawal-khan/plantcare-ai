# PlantCare AI — Premium Frontend Redesign

## Goal

Redesign the existing frontend into a **premium, production-quality AI/SaaS website** with a strong **botanical + AI + scientific** identity.

The current UI feels generic and card-heavy. Replace it with a visually impressive, professional and responsive experience.

## Design References

Use these as **inspiration for layout, components, animations and visual quality**:

* https://ui.shadcn.com/
* https://magicui.design/
* https://ui.aceternity.com/components
* https://hyperui.dev/

Do not copy branding, code, text or proprietary assets. Create an original PlantCare AI design.

## Visual Direction

Use:

* Deep forest green
* Emerald
* Soft mint
* Warm off-white
* Dark forest backgrounds
* Subtle gradients
* Premium typography
* Strong whitespace
* Sophisticated shadows
* Restrained rounded corners

Avoid:

* Generic AI templates
* Excessive green
* Giant leaf icons
* Repetitive cards
* Huge empty spaces
* Childish illustrations
* Random gradients
* Static/boring layouts

---

## 1. Homepage

Create this visual flow:

**Hero → Model Stats → AI Features → How It Works → Disease Preview → CTA**

### Hero

Completely replace the current generic leaf illustration.

Create a premium visual combining:

**real plant leaf + AI scanning + Grad-CAM concept**

Include:

* Strong headline: **Healthy Plants. Better Future.**
* Short explanation of AI-powered plant disease detection
* `Diagnose My Plant` CTA
* `Explore Diseases` CTA
* Professional entrance animation
* Subtle scanning/AI visual effects

---


## 2. Model Statistics

Use **verified real project/model metrics only**.

Never fabricate statistics.

Present metrics through a premium bento-style section instead of identical statistic cards.

If a metric cannot be verified, do not display a fake value.

---

## 3. Disease Library

The Disease Library must use the real:

`/diseases`

API.

Do not hardcode fake disease data.

Include:

* Search
* Plant filter
* Real disease images
* Plant name
* Disease name
* Severity
* Short description
* Details action

Cards should be image-focused and visually rich.

Hover effects:

* Image zoom
* Gradient overlay
* Title movement
* Arrow reveal

Use botanical SVG fallback when an image is unavailable.

---

## 4. Disease Detail

Create a premium scientific reference page containing:

* Disease image
* Disease name
* Plant
* Severity
* Description
* Symptoms
* Causes
* Management
* Prevention
* Related diseases
* `Diagnose Your Plant` CTA

---

## 5. How It Works

Create a connected AI pipeline:

**Upload → Preprocess → EfficientNetB0 → Prediction → Grad-CAM**

Desktop: horizontal animated pipeline.

Mobile: vertical timeline.

Use subtle animated nodes and connecting lines.

---

## 6. Diagnose Flow

Make the upload experience feel like a professional AI product.

Include:

* Drag/drop upload
* Image preview
* Upload state
* Professional scanning animation
* Analysis state
* Explanation state

Do not fake numerical progress.

Use indeterminate animation when real progress is unavailable.

---

## 7. Prediction Result

Design the result as an **AI diagnostic report**.

Strong hierarchy:

* Diagnosis
* Confidence
* Severity
* Original image
* Grad-CAM

Use tabs:

**Diagnosis | Visual Explanation | Details**

Use the real backend prediction and real Grad-CAM data.

Do not fabricate results.

---

## 8. Animation

Add tasteful professional motion:

* Hero entrance
* Scroll reveal
* Card hover
* Image zoom
* Button micro-interactions
* Workflow animation
* Scanning animation
* Tab transitions
* Theme transition

Respect `prefers-reduced-motion`.

Do not over-animate.

---

## 9. Dark / Light Mode

Both themes must be intentionally designed.

Dark mode should use:

* Deep forest / near-black backgrounds
* Dark surfaces
* Subtle borders
* Muted green accents
* High contrast typography

Do not simply invert the light theme.

---

## 10. Typography

Use a professional font such as **Inter or Geist**.

Create a consistent hierarchy:

**Display → H1 → H2 → H3 → Body → Small → Labels → Metrics**

Avoid random font sizes.

---

## 11. Responsive Design

Test and optimize:

**320 / 375 / 414 / 768 / 1024 / 1280 / 1440px**

Must have:

* No horizontal overflow
* No clipped text
* No overlapping elements
* No broken cards
* Proper mobile navigation
* Intentional mobile layouts

Do not simply shrink the desktop design.

---

## 12. Hydration Fix

Fix the existing hydration mismatch in:

`src/components/ui/Reveal.tsx`

Server and initial client render must be deterministic.

IntersectionObserver should initialize only after mount.

There must be **no hydration error in the browser console**.

---

## 13. Preserve Existing System

Do NOT break:

* Backend
* ML model
* APIs
* Prediction logic
* Grad-CAM
* Disease API
* TypeScript types
* API client
* Real disease data

Do not replace real backend data with mocks.

Do not modify backend/ML unless absolutely necessary.

---

# Acceptance Criteria

* [ ] Premium AI/SaaS visual identity
* [ ] Completely redesigned hero
* [ ] Generic leaf hero removed
* [ ] Professional typography
* [ ] Strong visual flow
* [ ] Bento/asymmetric layouts
* [ ] Verified real model statistics
* [ ] Real Disease Library data
* [ ] Real disease images
* [ ] Premium disease cards
* [ ] Professional Disease Detail
* [ ] Connected AI workflow
* [ ] Premium diagnose experience
* [ ] Professional result report
* [ ] Real Grad-CAM preserved
* [ ] Professional animations
* [ ] Dark/light mode
* [ ] Responsive 320–1440px
* [ ] No hydration errors
* [ ] No console errors
* [ ] Tests pass
* [ ] Lint passes
* [ ] Production build passes

# Implementation Rule

Do not provide a design proposal first.

**Inspect the existing codebase → implement the redesign → test → fix → build.**

You have freedom to create, remove, restructure and improve frontend components/files when required.

Do not stop after changing colors or spacing. The final result must look substantially more premium and professionally designed.

After completion, report:

1. Files changed
2. UI improvements
3. Animations
4. Backend integration
5. Responsive verification
6. Tests/lint/build
7. Remaining issues
