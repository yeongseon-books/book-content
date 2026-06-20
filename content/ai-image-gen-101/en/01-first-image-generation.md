---
title: "AI Image Generation 101 (1/10): Creating Your First Image"
series: ai-image-gen-101
episode: 1
language: en
last_reviewed: '2026-06-18'
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
seo_description: "Want to create images with ChatGPT but unsure where to start? This guide walks you through your first prompt."
---

# AI Image Generation 101 (1/10): Creating Your First Image

You need a blog thumbnail but don't have budget for a designer. You want an eye-catching social media image but stock photos feel generic. You need a presentation illustration but can't find the right one on free image sites.

ChatGPT's image generation is built for exactly these moments. Describe what you want in plain text, and AI creates an image matching your description. But here's the thing: the same tool produces wildly different results depending on how you describe what you want.

This is the first post in the AI Image Generation 101 series. Here, we'll create our first images with ChatGPT and directly compare how small changes in our prompts lead to dramatically different outcomes.

---

![AI Image Generation 101 (1/10): Creating Your First Image](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/01-01-ai-image-generation-101-1-10-creating-yo.en.png)
*The image generation flow from prompt to final result*

## Questions to Keep in Mind

- When asking ChatGPT to generate an image, how detailed should your description be to get what you actually want?
- If you just say "draw me a cat," what kind of cat will you get? Will it match what you imagined?
- Every time you change your prompt the results differ — which elements have the biggest impact?

---

## What Is ChatGPT Image Generation?

ChatGPT's image generation takes a text description and produces an image from it. You don't need to know professional design tools — just describe the scene you want in plain language.

There are two ways to use this capability:

| Method | Description | Best For |
|--------|-------------|----------|
| ChatGPT Web/App | Request directly in the chat window | Everyone |
| Open-source tool (god-tibo-imagen) | Automate via code | People with repetitive tasks |

This series covers both approaches. The prompt-writing techniques are identical regardless of the tool — only the interface differs.

---

## First Experiment: Simple Prompt vs Detailed Prompt

Let's make two images of the same subject and compare.

### Experiment 1: A Cat

**Prompt A** (2 words):

> a cat

**Prompt B** (detailed description):

> A fluffy orange tabby cat sitting on a windowsill at golden hour, soft warm sunlight streaming through the window, bokeh background of a cozy living room, photorealistic style, shallow depth of field

Compare the results:

| Prompt A: "a cat" | Prompt B: Detailed description |
|:---:|:---:|
| ![a cat prompt result](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/01-simple-prompt.png) | ![detailed cat prompt result](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/02-detailed-prompt.png) |

*Left: AI decided everything about the cat. Right: orange tabby, windowsill, golden hour lighting — all specified in the prompt.*

Notice the key difference. With just "a cat," the AI arbitrarily decides the breed, color, pose, background, and lighting. It's like rolling dice. The detailed prompt, on the other hand, guides the AI toward what you actually had in mind.

### Experiment 2: A Mountain

**Prompt A** (2 words):

> a mountain

**Prompt B** (detailed description):

> A snow-capped mountain peak at sunrise, dramatic pink and orange clouds reflecting in a crystal-clear alpine lake in the foreground, pine trees framing the edges, landscape photography style, wide-angle lens

| Prompt A: "a mountain" | Prompt B: Detailed description |
|:---:|:---:|
| ![a mountain prompt result](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/03-vague-landscape.png) | ![detailed mountain prompt result](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/04-detailed-landscape.png) |

*Left: AI's arbitrary mountain. Right: sunrise, lake reflection, pine tree framing — all specified.*

See the pattern? A simple prompt delegates almost every creative decision to the AI. A detailed prompt is you directing the AI toward your vision.

---

## The 5 Core Elements of a Prompt

We've confirmed that detailed prompts produce better results. So what exactly should you include?

| Element | Description | Example |
|---------|-------------|---------|
| **Subject** | What to draw | Orange tabby cat |
| **Style** | What mood/medium | Photorealistic, watercolor |
| **Composition** | What angle/framing | Close-up, overhead shot |
| **Lighting** | How light behaves | Warm afternoon sun, neon glow |
| **Background** | What's behind the subject | Cozy living room, city skyline |

You don't need all five every time. A subject alone will produce an image. But the more elements you specify, the closer the result matches your intent.

### Experiment 3: A Coffee Cup

Let's see the difference when adding elements incrementally.

**Prompt A** (subject only):

> a coffee cup on a table

**Prompt B** (all 5 elements):

> A steaming latte with beautiful latte art in a ceramic cup, sitting on a rustic wooden table in a cozy cafe, morning light coming through the window, warm tones, overhead shot, food photography style

| Subject only | All 5 elements |
|:---:|:---:|
| ![coffee basic prompt](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/05-coffee-basic.png) | ![coffee detailed prompt](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/06-coffee-detailed.png) |

*Left: subject only. Right: style (food photography), composition (overhead), lighting (morning light), background (cafe) all specified.*

The right image is ready for Instagram or a blog post. The only investment was 30 extra seconds writing a better prompt.

---

## Three Tips for Your First Prompts

Based on what we've observed across these experiments:

### 1. Be Specific

"A pretty flower" is vague. "Cherry blossom petals drifting down a tree-lined path on a spring morning" gives the AI something concrete to work with. AI can't see what's in your head — it only understands what you put into words.

### 2. Name the Style

Adding "photorealistic," "watercolor painting," "Pixar animation style," or "minimalist flat design" gives the AI a strong signal for the overall mood and rendering approach.

### 3. You Don't Need Perfection on the First Try

If the first result doesn't match your vision, revise the prompt and regenerate. Image generation is an iterative process, not a one-shot deal. You can also give follow-up instructions like "make it brighter," "simplify the background," or "shift the subject slightly left."

---

## Generating Images with the Open-Source Tool

Every example image in this series was generated using [god-tibo-imagen](https://github.com/NomaDamas/god-tibo-imagen), an open-source tool. It lets you automate ChatGPT's image generation from code.

```python
from gti import Client

client = Client()
result = client.generate_image(
    prompt="A fluffy orange tabby cat sitting on a windowsill at golden hour",
    output_path="my-cat.png"
)
print(f"Image saved to: {result.saved_path}")
```

With this tool, you can easily run experiments — generating the same prompt multiple times, or comparing slight variations side by side. We'll cover this in detail later in the series.

You can achieve the same results by typing the same prompt directly into ChatGPT's web interface. The prompt technique is what matters, not the tool.

---

## Summary: What We Learned Creating Our First Images

Three experiments, one clear lesson:

- Simple prompts delegate almost all creative decisions to the AI
- Detailed prompts guide the AI toward your specific vision
- Five elements — subject, style, composition, lighting, background — determine the output

In the next post, we'll dive deeper into prompt structure: the specific formula for combining these elements effectively.

---

## Answering the Opening Questions

**When asking ChatGPT to generate an image, how detailed should your description be?**

Specify as many of the five elements (subject, style, composition, lighting, background) as you can. You don't need all five, but the more you include, the closer the result gets to your intent.

**If you just say "draw me a cat," what kind of cat will you get?**

You'll get whatever the AI decides — breed, color, pose, background, lighting all chosen arbitrarily. The chance it matches what you imagined is low.

**Which elements have the biggest impact when changing prompts?**

Style and lighting shift the overall mood most dramatically. The same cat rendered "photorealistic" versus "watercolor" produces completely different images. We'll explore style in depth in post 3.

---

<!-- toc:begin -->
## Series Index

- **AI Image Generation 101 (1/10): Creating Your First Image (current)**
- AI Image Generation 101 (2/10): The Structure of a Good Prompt (upcoming)
- AI Image Generation 101 (3/10): Mastering Styles (upcoming)
- AI Image Generation 101 (4/10): Composition and Perspective (upcoming)
- AI Image Generation 101 (5/10): Color and Lighting (upcoming)
- AI Image Generation 101 (6/10): Designing Complex Scenes (upcoming)
- AI Image Generation 101 (7/10): Maintaining Consistency (upcoming)
- AI Image Generation 101 (8/10): Text and Typography (upcoming)
- AI Image Generation 101 (9/10): Working with Reference Images (upcoming)
- AI Image Generation 101 (10/10): Production Workflows (upcoming)
<!-- toc:end -->

## References

- [ChatGPT Image Generation Official Guide](https://help.openai.com/en/articles/9055440-using-dall-e-and-browsing-in-chatgpt)
- [god-tibo-imagen GitHub Repository](https://github.com/NomaDamas/god-tibo-imagen)

Tags: AI, ChatGPT, Image Generation, Prompt Engineering
