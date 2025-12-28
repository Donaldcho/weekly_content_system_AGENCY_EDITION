# Agency Edition: Deviceterra Platform Guide 🏢

## Overview
The **Agency Edition** transforms Deviceterra from a single-user tool into a robust **Multi-Tenant Agency Platform**. This allows a single installation to manage content, brand identity, and schedules for multiple distinct clients (e.g., "Coca-Cola", "Nike", "Local Bakery") with strict data isolation.

## Key Features

### 1. Multi-Client Architecture 🔐
*   **Data Isolation**: Every post, visual asset, and brand setting is strictly scoped to a specific `client_id`.
*   **Context Switching**: The new "Agency Dashboard" allows admins to instantly switch context between clients. The entire application (Brand, Generate, Scheduler) updates to reflect the active client.

### 2. Agency Dashboard 📊
*   **Central Command**: A high-level view of all managed clients.
*   **Client Onboarding**: Easily add new clients with their logo, industry, and initial settings.
*   **Usage Tracking**: Monitor token usage and costs per client to facilitate billing.

### 3. Client-Specific Brand Identity 🎨
*   **Unique Voices**: Each client has their own "Brand Voice", "Mission", and "Visual Style" settings.
*   **Visual Vaults**: Assets uploaded to the Vault are private to the active client. Client A never sees Client B's images.

### 4. Isolated Scheduling 📅
*   **Dedicated Calendars**: The Scheduler view is filtered by the active calendar. Switching clients wipes the calendar clean and loads the new client's schedule.
*   **Draft Queues**: Drafts are also isolated, ensuring content doesn't get mixed up.

### 5. Smart Visual Templates 🖼️
*   **Style Extraction**: Upload a reference image, and the system automatically extracts its artistic style using computer vision.
*   **Tailored Generation**: The extracted style is fused with the post's topic to generate on-brand visuals automatically.

## Getting Started

1.  **Login** as an Agency Admin.
2.  Navigate to **Agency Dashboard**.
3.  Click **"Add Client"** to onboard a new brand.
4.  Select the client from the **"Active Client"** dropdown.
5.  Go to **Brand Identity** to configure their unique voice and upload their logo.
6.  Start generating content!

## Technical Implementation
*   **Database**: SQLite with Foreign Key constraints on `client_id`.
*   **Session Management**: `st.session_state.current_client_id` tracks the active context.
*   **Security**: All data access layers (`get_all_posts`, `get_assets`) enforce client filtering.

---
*Deviceterra Agency Edition - Built for Scale.*
