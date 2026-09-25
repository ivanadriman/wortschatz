# 🇩🇪 Wortschatz — German Flashcards for Windows 11

A clean, modern Windows 11 desktop app to explore, learn, and master German vocabulary (*Wortschatz*), conversational phrases (*Small Talk*), and situational expressions (*Redemittel*) using interactive flashcards, high-fidelity neural German speech, in-line grammar, and active retention tracking.

---

## 🚀 How to Run

### Method 1: Double-Click (Recommended)
Simply double-click **`run.bat`** in the project folder.
It automatically verifies Python and launches the app without keeping a terminal window open.

### Method 2: Command Line
```powershell
python -m pip install -r requirements.txt
python wortschatz_app.py
```

---

## 🧭 Controls & Keyboard Shortcuts

### 📖 Explore Mode (Casual Reading & Discovery)
*Dedicated to comfortable browsing, listening, and vocabulary discovery without test scoring or clutter.*

| Action | Keyboard Shortcut | Mouse Action |
| :--- | :--- | :--- |
| **Flip Card** | `Space` / `Enter` / `Up` / `Down` | Click anywhere on the card or `🔄 Flip Card (Space)` button |
| **Previous Card** | `←` (Left Arrow) or `1` | Click `◀ Previous (← / 1)` button |
| **Next Card** | `→` (Right Arrow) or `2` | Click `Next (→ / 2) ▶` button |
| **Listen to German** | `V` or `A` | Click `🔊 Listen (V)` button on card |
| **Restart Category** | `R` | Click `↺ Restart` in toolbar |
| **Toggle Shuffle** | `S` | Click `🔀 Shuffle` in toolbar |
| **Reverse (DE ⇄ EN)** | *Click button* | Toggle German ➔ English or English ➔ German |

### 🎯 Quiz Mode (Active Recall & Testing)
*Dedicated to testing your memory, rating card retention, and tracking study streaks.*

| Action | Keyboard Shortcut | Mouse Action |
| :--- | :--- | :--- |
| **Reveal Answer** | `Space` / `Enter` | Click `👁 Reveal Answer (Space)` button |
| **Rate: Needs Practice** | `←` (Left) or `1` *(when revealed)* | Click `🔴 Needs Practice (← / 1)` button |
| **Rate: Mastered** | `→` (Right) or `2` *(when revealed)* | Click `🟢 Mastered (→ / 2) ▶` button |
| **Flip Back** | `Space` *(when revealed)* | Click `🔄 Flip Back (Space)` button |
| **Skip Card** | `←` or `→` *(before reveal)* | Click `⏭ Skip (←)` or `⏭ Skip (→)` |
| **Filter Cards** | *Select dropdown* | Filter by: *All Cards*, *🔴 Needs Practice Only*, *🟢 Mastered Only*, *⚪ Unseen Only* |

### 🛠 Global Shortcuts (Always Available)
| Action | Shortcut | Description |
| :--- | :--- | :--- |
| **Search All Decks** | `Ctrl + F` | Instant live search across all 11+ decks |
| **Quick-Add Card** | `Ctrl + N` | Rapidly add new flashcards to any deck file |
| **Dark / Light Theme** | Click `☀️ Theme` | Toggle Windows 11 Dark / Light appearance |
| **Reset Metrics** | Click `↺ Reset Metrics` | Reset streak, reviews, and card statuses with confirmation modal |
| **Preload Audio** | Click `⬇ Preload Audio` | Pre-cache all audio for 100% offline study |

---

## ✨ Mode Separation: Explore vs. Quiz

| Feature | 📖 Explore Mode | 🎯 Quiz Mode |
| :--- | :---: | :---: |
| **Goal** | Casual reading, preview, and listening | Active recall testing & retention |
| **Action Buttons** | `Previous`, `Flip Card`, `Next` | `Reveal Answer`, `Needs Practice`, `Mastered` |
| **Keys `1` & `2`** | Always Navigate: `1 = Prev`, `2 = Next` | Always Rate Recall: `1 = Needs Practice`, `2 = Mastered` |
| **Card Mastery Badges** | ❌ Hidden (clean dictionary card) | ✅ Visible (`🟢 Mastered`, `🔴 Needs Practice`, `⚪ Unseen`) |
| **Retention Scoring** | ❌ No scoring pressure | ✅ Live session score & streak tracker |
| **Difficult Cards Filter**| ❌ Shows complete deck | ✅ Filter by *Needs Practice*, *Mastered*, *Unseen* |
- **📚 Smart In-Line Grammar & Plural Badges**:
  - Automatically parses natural dictionary plural notations (e.g. `das Buch, die Bücher`, `das Auto, -s`, `der Student, -en`).
  - Displays base noun prominent and places plural in a dedicated subtitle badge (`📖 Plural: die Bücher`).
  - Renders parenthetical hints (e.g. `sprechen (spricht, sprach)`, `die Bank (Geldinstitut)`) in subtle italicized secondary typography.
  - Leaves conversational phrases and dialogue sentences with commas completely untouched.
- **🎨 Color-Coded Article Badges**:
  - **`der`** (Masculine — Blue)
  - **`die`** (Feminine / Plural — Rose/Red)
  - **`das`** (Neuter — Green)
- **🔍 Quick Search (`Ctrl + F`)**:
  - Instant live search modal querying across all 11+ categories simultaneously. Click any result to jump immediately to that card.
- **➕ In-App Quick-Add (`Ctrl + N`)**:
  - Rapidly append new flashcards to any deck file without opening Notepad or Excel.
- **📊 Streaks & Retention Tracking**:
  - First-class parity for both **🔴 Needs Practice** and **🟢 Mastered** counters across the app.
  - Live stats chip in the toolbar: `🔥 Streak  •  🔴 Practice: X  •  🟢 Mastered: Y  •  Today: Z`.
  - Live session score counter during quizzes: `Session: 🟢 X  🔴 Y (Z%)`.
  - Dynamic deck breakdown in Quiz filters: `All Cards (34)`, `🔴 Needs Practice (4)`, `🟢 Mastered (12)`, `⚪ Unseen (18)`.
  - Tracks consecutive daily study streaks and card review history saved locally in `user_progress.json`.

---

## 📁 Included Decks (`decks/` folder)

All flashcard decks are stored inside the **`decks/`** directory. Click **`📂 Decks`** inside the app to jump directly to the files in Windows Explorer.

### 📚 Wortschatz (Vocabulary & Nouns with Articles)
- `decks/Wortschatz - Beruf & Arbeit.txt` → Category **Wortschatz - Beruf & Arbeit** (35 cards)
- `decks/Wortschatz - Gesundheit.txt` → Category **Wortschatz - Gesundheit** (34 cards)
- `decks/Wortschatz - Wohnen & Finanzen.txt` → Category **Wortschatz - Wohnen & Finanzen** (30 cards)

### 💬 Small Talk (Contextual Dialogues)
- `decks/Small Talk - Auf dem Amt & Behörden.txt` → Category **Small Talk - Auf dem Amt & Behörden** (20 cards)
- `decks/Small Talk - Beim Arzt & Apotheke.txt` → Category **Small Talk - Beim Arzt & Apotheke** (20 cards)
- `decks/Small Talk - Beruf & Arbeit.txt` → Category **Small Talk - Beruf & Arbeit** (20 cards)
- `decks/Small Talk - Gesundheit.txt` → Category **Small Talk - Gesundheit** (22 cards)
- `decks/Small Talk - Im Büro.txt` → Category **Small Talk - Im Büro** (20 cards)
- `decks/Small Talk - Im Café.txt` → Category **Small Talk - Im Café** (20 cards)
- `decks/Small Talk - Nachbarschaft.txt` → Category **Small Talk - Nachbarschaft** (18 cards)
- `decks/Small Talk - Party & Event.txt` → Category **Small Talk - Party & Event** (18 cards)
- `decks/Small Talk - Unterwegs & Reisen.txt` → Category **Small Talk - Unterwegs & Reisen** (20 cards)

### ✍️ Redemittel (Situational Formulaic Expressions)
- `decks/Redemittel - Alltag & Redewendungen.txt` → Category **Redemittel - Alltag & Redewendungen** (20 cards)
- `decks/Redemittel - Formal Email.txt` → Category **Redemittel - Formal Email** (22 cards)
- `decks/Redemittel - Verkaufen and Einkaufen.txt` → Category **Redemittel - Verkaufen and Einkaufen** (23 cards)

### 🎯 CEFR Curated Levels (B1, B2, C1)
- **Niveau B1 (Intermediate)**:
  - `decks/B1/B1_Wortschatz_Alltag_und_Wohnen.txt` (25 cards: Daily life, renting, household)
  - `decks/B1/B1_Grammatik_Verben_mit_Praepositionen.txt` (30 cards: Essential verb-preposition combinations)
  - `decks/B1/B1_Behoerden_und_Buerokratie.txt` (25 cards: Civil registration, forms, deadlines, residency)
- **Niveau B2 (Vantage / Professional)**:
  - `decks/B2/B2_NVR_Nomen_Verb_Verbindungen.txt` (25 cards: Noun-Verb collocations like *in Betracht ziehen*, *zur Verfügung stehen*)
  - `decks/B2/B2_Redemittel_Diskussion_und_Argumentation.txt` (15 cards: Debate, argumentation, structured viewpoints)
  - `decks/B2/B2_Vorstellungsgespraech_und_Karriere.txt` (17 cards: Job interviews, salary, probation)
  - `decks/B2/B2_Grammatik_Zweiteilige_Konnektoren.txt` (18 cards: Two-part connectors like *je...desto*, *nicht nur...sondern auch*)
- **Niveau C1 (Effective Operational Proficiency)**:
  - `decks/C1/C1_Wortschatz_Gehobene_Sprache_und_Diskurs.txt` (25 cards: High register vocabulary like *eklatant*, *unabdingbar*, *frappierend*)
  - `decks/C1/C1_Redemittel_Rhetorische_Feinheiten.txt` (15 cards: Academic reasoning, subtle nuance, precision discourse)
  - `decks/C1/C1_Modalpartikeln_und_Gespraechsnuancen.txt` (15 cards: Real-life pragmatic particles like *halt, eben, bloß, doch, wohl*)

---

## 🛠️ Adding Custom Decks & Cards

You can add cards using **`Ctrl + N`** inside the app, or manually add files to `decks/` (including subdirectories like `decks/B1/`, `decks/B2/`, `decks/C1/`):

1. **File Name & Hierarchy**: The filename automatically becomes the category name, and subfolder names (`B1`, `B2`, `C1`) automatically set the CEFR level.
2. **Format**: Exactly two columns per row:
   - **Column 1**: German word or sentence (can include plurals or hints like `das Brot, -e` or `fahren (fährt, fuhr)`)
   - **Column 2**: English meaning
3. **Delimiter**: Semicolon (`;`), comma (`,`), tab (`\t`), pipe (`|`), or dash (` - `).
