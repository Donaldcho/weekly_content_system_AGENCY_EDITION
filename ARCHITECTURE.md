# 🏗️ System Architecture: Deviceterra / Weekly Content System

This document outlines the technical architecture of the automated marketing agency system.

## 1. High-Level Diagram

```mermaid
graph TD
    User([User / Browser]) <--> Streamlit[Streamlit UI]
    
    subgraph "Application Layer"
        Streamlit <--> ContentGen[ContentGenerator (Orchestrator)]
        Streamlit <--> NanoBanana[Nano Banana (Visual Engine)]
        Streamlit <--> Auth[Auth Manager (OAuth)]
    end
    
    subgraph "Agentic Layer (ADK)"
        ContentGen --> Agency[MarketingAgency (ADK Main)]
        Agency --> Strat[Strategist Agent]
        Agency --> Creator[Creator Agent]
        Agency --> Visual[Visual Design Agent]
        Variable[PromptRegistry] -.-> Strat & Creator & Visual
    end
    
    subgraph "Data Layer"
        ContentGen <--> DB[(SQLite Database)]
        ContentGen <--> RAG[RAG Engine (Vector DB)]
        RAG <--> Vault[Asset Vault]
    end
    
    subgraph "External Services"
        NanoBanana --> GoogleAI[Google Gemini / Imagen]
        Auth --> LinkedIn[LinkedIn API]
        Auth --> FB[Facebook Graph API]
    end
```

## 2. Core Components

### 🖥️ Frontend (Streamlit)
*   **Purpose**: Provides the interactive dashboard for the user.
*   **Key Files**:
    *   `app.py`: Main entry point and navigation.
    *   `ui/generate.py`: The "Mission Control" for creating content.
    *   `ui/brand.py`: Brand DNA and style management.

### 🧠 Backend Engines
*   **`backend/content_generator.py`**: The legacy monolith that attempts to coordinate everything. It is gradually offloading logic to the **ADK**.
*   **`backend/nano_banana.py`**: The dedicated **Image Generation Engine**.
    *   Features a **Universal Switch** to handle both `Gemini` (Multimodal) and `Imagen` (Standard) models transparently.
    *   Includes "Dream Mode" fallback for when APIs fail.
*   **`backend/prompt_registry.py`**: A new system that decouples **Prompt Logic** from **Code**. It loads system instructions from `assets/prompts.json`.

### 🕵️ The ADK (Agent Development Kit)
Located in `backend/adk/`, this is the modern, modular "brain" of the system.
*   **`MarketingAgency` (`adk/main.py`)**: The manager that hires specific agents for a task.
*   **`Strategist`**: Analyzes trends and plans the weekly calendar.
*   **`Creator`**: Writes the actual copy (LinkedIn posts, etc.).
*   **`Visual`**: acts as the Art Director, writing prompts for Nano Banana.

## 3. Data Flow Example: "Generate Weekly Plan"

1.  **User** clicks "Generate Week" in UI.
2.  **UI** calls `ContentGenerator.generate_weekly_plan()`.
3.  **ContentGenerator** spins up the `MarketingAgency`.
4.  **Agency** calls **Strategist** to create a 7-day plan based on `prompts.json` rules.
5.  **Agency** iterates through the plan:
    *   Calls **Creator** to write the text drafts.
    *   Calls **Visual** to write the image prompts.
6.  **UI** displays the drafts.
7.  **User** clicks "Visualize".
8.  **Nano Banana** takes the image prompt -> Calls Google Gemini -> Saves Image -> UI displays it.
9.  **User** clicks "Schedule".
10. **Backend** saves to `schedule` table in SQLite.

## 4. Key Configurations
*   **`assets/prompts.json`**: The "Personality File". Edit this to change how agents behave (e.g., "Be more funny", "Don't use neon colors").
*   **`.env`**: Stores API Keys (`GOOGLE_API_KEY`, `LINKEDIN_CLIENT_ID`).
