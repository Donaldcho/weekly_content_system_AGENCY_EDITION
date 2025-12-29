# 📘 Deviceterra User Manual

Welcome to **Deviceterra**, your automated AI Marketing Agency. This guide will help you produce weeks of high-quality social media content in minutes.

---

## 🚀 Getting Started

### 1. Dashboard Overview
Upon logging in, you will see the **Mission Control**.
*   **Generate**: The primary workspace for creating content.
*   **Schedule**: view your calendar grid.
*   **Brand DNA**: Configure your company's voice and style.
*   **Vault**: Your asset library (saved visuals).

---

## 🎨 Step 1: Define Your Brand
Before generating content, teach the AI who you are.

1.  Navigate to **Brand DNA** in the sidebar.
2.  **Basic Info**: Enter your Company Name and Industry.
3.  **Target Audience**: Describe who you are talking to (e.g., "CTOs of Series A startups").
4.  **Brand Voice**: Choose a tone (e.g., "Professional", "Witty") or paste a sample of your writing for analysis.
5.  **Visual Identity**: Define your color palette and preferred art style (e.g., "Minimalist Tech", "Cyberpunk").
    *   *Tip: Use the "Visualize" preview to see how your style looks.*

---

## ⚡ Step 2: Generate a Weekly Plan
The **Strategist Agent** plans your week based on your brand and trends.

1.  Navigate to **Generate**.
2.  **Campaign Topic**: Enter a main theme (e.g., "The Future of AI Agents").
3.  **Trend Data**: (Optional) Paste links or keywords about current news.
4.  Click **✨ Generate Weekly Plan**.
5.  **Review**: The Agents will produce 5-7 drafts (LinkedIn/Facebook post pairs).
    *   Read the drafts.
    *   Click **Edit** on any text to tweak the copy.

---

## 🍌 Step 3: Nano Banana Vision (Images)
Bring your posts to life with the integrated image engine.

1.  Scroll to the **Visuals** section of a post draft.
2.  **Source**:
    *   **Smart Style**: AI automatically dreams up a prompt based on the post text.
    *   **Prompt**: Write your own description.
    *   **Vault**: Pick a pre-saved image.
3.  **Engine Class**:
    *   **Nano Pro**: Highest quality (slower). Best for final assets.
    *   **Nano**: Faster, good for drafting.
4.  Click **✨ Summon Nano Banana**.
5.  The image will appear. If you don't like it, click **Re-roll**.

---

## 📅 Step 4: Schedule & Publish
1.  Once happy with text and image, click **📅 Schedule**.
2.  Navigate to the **Schedule** page to see your calendar.
3.  (Future Feature) Automated posting to LinkedIn via API is configured in the **Connections** tab.

---

## 🧠 Advanced: Customizing the AI Personality
Want the "Creative Director" to think differently?

1.  Open the file `assets/prompts.json` in your project folder.
2.  Edit the **System Instructions** for `visual_agent_system` or `smart_style_generator`.
3.  Save the file. The agents update instantly—no restart required.

---

## ❓ FAQ

**Q: Why do my images look like neon sci-fi?**
A: Check your `prompts.json`. Ensure you haven't told the AI to always use "Futuristic" styles. You can tone it down by adding "Realistic, corporate photography" to your Brand DNA.

**Q: I get a "Quota Exceeded" error.**
A: You may have hit the free tier limit of the Google Gemini API. Wait a few minutes or upgrade your API key quotas.
