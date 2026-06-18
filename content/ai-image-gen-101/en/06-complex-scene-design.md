---
title: "AI Image Generation 101 (6/10): Designing Complex Scenes"
series: ai-image-gen-101
episode: 6
language: en
status: draft
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: false
tags:
- AI
- ChatGPT
- Image Generation
- Prompt Engineering
seo_description: "Learn to compose multi-person scenes with layered depth, spatial division, and interaction — plus understand where AI fails and why."
---

# AI Image Generation 101 (6/10): Designing Complex Scenes

One person is easy. But ask for "two people having a conversation" and they merge, overlap, or stare in wrong directions. The more elements in a scene, the more AI decides arbitrarily — and the harder it gets to match your intent.

Today we scale from a single person to multi-person scenes, layered compositions, spatial division, and dynamic interactions. We'll also show what failure looks like when you push too hard.

This is post 6 in the AI Image Generation 101 series.

---

```mermaid
flowchart LR
    A["Complexity Levels"] --> B["1 Person"]
    B --> C["2 People + Interaction"]
    C --> D["Multi-person"]
    D --> E["Layer Arrangement"]
    E --> F["Spatial Division"]
    F --> G["Action + Interaction"]
```

*Stepwise approach to complex scenes*

## Questions to Keep in Mind

- Where does AI fail most often when placing multiple people?
- What changes when you specify foreground/midground/background layers?
- What prompt structure avoids chaos in complex scenes?

---

## Level 1: Single Person — Baseline

> A chef in a white coat standing alone in a modern kitchen, holding a knife, clean stainless steel counter, photorealistic, medium shot

![Single person](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/01-single-person.png)

*Single person: clear subject, simple background. The easiest difficulty level for AI.*

One person with a simple background is where AI performs most reliably. This is our baseline.

---

## Level 2: Two People Interacting

> A chef in a white coat teaching a young apprentice how to chop vegetables in a modern kitchen, both facing the cutting board, photorealistic, medium shot

![Two people](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/02-two-people.png)

*Two people: specifying their relationship and shared action produces natural interaction.*

**Key technique**: Define the **relationship** (teacher-student) and a **shared action** (both facing the cutting board).

**Two-person prompt checklist**:
- Distinguishing features for each (clothing, age, role)
- Relationship or interaction (teaching, talking, handing over)
- Gaze/body direction (both facing the cutting board)
- Spatial arrangement (side by side, facing each other, behind)

---

## Level 3: Multi-Person Scene (5+)

> A busy restaurant kitchen with five chefs working at different stations, one grilling, one plating, one chopping, steam rising from pots, organized chaos, photorealistic, wide shot

![Multi-person](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/03-busy-kitchen.png)

*Multi-person: assigning unique actions to each person makes them distinguishable.*

**Key technique**: Each of the 5 people gets a **unique action** (grilling, plating, chopping). Writing "five chefs" alone produces five people in identical poses.

**Multi-person principles**:

| Principle | Bad | Good |
|-----------|-----|------|
| Unique actions | "five people working" | "one grilling, one plating, one chopping" |
| Spatial distribution | "chefs in a kitchen" | "each at a different station" |
| Atmosphere keywords | (none) | "organized chaos, steam rising" |

---

## Level 4: Foreground/Midground/Background Layers

> foreground shows a beautifully plated dish in sharp focus... midground shows a chef garnishing... background shows the rest of the kitchen team with soft bokeh

![Layer arrangement](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/04-foreground-mid-back.png)

*Layered depth: foreground (dish), midground (chef), background (team). Focus differences guide the viewer's eye.*

**Key technique**: Explicitly name `foreground`, `midground`, `background` and specify what occupies each. Add `shallow depth of field` to create focus graduation.

**Layer prompt structure**:

```
[Foreground: subject + sharp focus] + 
[Midground: subject + slightly blurred] + 
[Background: subject + soft bokeh] + 
shallow depth of field
```

This transforms "a scene with many things" into a **depth-guided composition** where the viewer's eye follows your intent.

---

## Level 5: Spatial Division

> on the left side a traditional wooden ramen stall with a Japanese chef, on the right side a modern fusion taco stand with a Mexican chef, both sides connected by a shared counter

![Spatial division](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/05-spatial-left-right.png)

*Spatial division: explicitly splitting left/right creates a symmetric, balanced composition.*

**Key technique**: `on the left side... on the right side...` explicitly divides the canvas. Effective for comparison images, before/after, or two-world contrasts.

**Spatial keywords**:
- Left/Right: `on the left`, `on the right`, `left half`, `right half`
- Top/Bottom: `top portion`, `bottom portion`, `upper half`, `lower half`
- Connection: `connected by`, `shared`, `between them`

---

## Level 6: Action and Interaction

> a chef tossing a flaming pan high in the air... a wide-eyed apprentice jumps back in surprise... another chef in the background calmly plates food

![Action and interaction](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/06-action-interaction.png)

*Action scene: giving each person a different reaction to the same moment creates drama.*

**Key technique**: Three people showing **contrasting reactions** to the same moment. One acts (tossing fire), one reacts (jumping back in surprise), one ignores (calmly working). This contrast creates narrative tension.

---

## Failure Case: Overcrowding

> A confusing overcrowded scene with too many elements: ten different people doing ten different activities, dogs, cats, children...

![Overcrowded](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/07-bad-overcrowded.png)

*Overcrowded: too many elements causes AI to merge, drop, or distort elements.*

**Why it fails**: AI has a complexity ceiling. Requesting 10+ people with animals, furniture, and props simultaneously causes elements to be omitted or unnaturally merged.

**Complexity limits**:

| Element Count | Stability | Strategy |
|---------------|-----------|----------|
| 1-3 people + simple BG | Very stable | Use directly |
| 4-6 people + medium BG | Mostly stable | Give each a unique action |
| 7+ people | Unstable | Describe as groups |
| 10+ simultaneous elements | High failure rate | Generate separately, composite |

---

## Success Case: Organized Complex Scene

> A well-organized complex family dinner scene: a large rectangular table with eight family members of different ages, grandmother at the head serving roast turkey...

![Organized complex scene](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/08-good-organized.png)

*Organized complexity: an anchor structure (table) plus clearly defined positions and actions keeps 8 people stable.*

**Why it works**: A central structure (large rectangular table) anchors the layout. Every person is defined by their **relationship to this structure** (grandmother at the head, children reaching for rolls, parents pouring wine).

---

## Complex Scene Prompt Formula

```
1. Define central structure/setting (table, stage, street)
2. Each person: role + action + position
3. Relationships/interactions between people
4. Atmosphere/lighting
5. Composition (wide shot mandatory)
```

**Core principles**:
- Place the anchor structure first, then arrange people around it
- Give each person distinguishable traits and actions
- Beyond 7 people, describe in groups rather than individually
- Use `wide shot` to ensure all elements are visible

---

## Key Takeaway

Building complex scenes step by step:

- 1→2 people: specify relationship and interaction
- Multi-person: each person needs a unique action
- Foreground/midground/background layers create guided depth
- Overcrowding fails — use anchor structures and relationship-based placement

In the next post, we'll explore maintaining consistency — generating the same character repeatedly across multiple images.

---

## Answering the Opening Questions

**Where does AI fail most when placing multiple people?**

At 7+ people without specific actions, figures merge or disappear. The fix: give each person a unique action and position, and use a central structure (table, counter) as a spatial anchor.

**What changes with foreground/midground/background layers?**

A flat "scene with many things" becomes a depth-guided composition where the viewer's eye follows your chosen focal point. AI applies focus differences that naturally prioritize the most important element.

**What prompt structure avoids chaos?**

Central structure definition, then per-person role/action/position, then relationships, then atmosphere, then composition. When everyone is defined by their relationship to the anchor structure, AI's placement decisions become reliable.

---

<!-- toc:begin -->
## Series Index

- [AI Image Generation 101 (1/10): Creating Your First Image](./01-first-image-generation.md)
- [AI Image Generation 101 (2/10): The Structure of a Good Prompt](./02-prompt-structure.md)
- [AI Image Generation 101 (3/10): Mastering Styles](./03-mastering-styles.md)
- [AI Image Generation 101 (4/10): Composition and Perspective](./04-composition-and-perspective.md)
- [AI Image Generation 101 (5/10): Color and Lighting](./05-color-and-lighting.md)
- **AI Image Generation 101 (6/10): Designing Complex Scenes (current)**
- AI Image Generation 101 (7/10): Maintaining Consistency (upcoming)
- AI Image Generation 101 (8/10): Text and Typography (upcoming)
- AI Image Generation 101 (9/10): Working with Reference Images (upcoming)
- AI Image Generation 101 (10/10): Production Workflows (upcoming)
<!-- toc:end -->

## References

- [OpenAI Image Generation Guide](https://platform.openai.com/docs/guides/images)
- [god-tibo-imagen GitHub Repository](https://github.com/NomaDamas/god-tibo-imagen)

Tags: AI, ChatGPT, Image Generation, Prompt Engineering
