🧱 Projektarchitektur (High Level)
/Raiders_of_the_north_sea
│
├── game/
│   ├── state.py          # kompletter Spielzustand
│   ├── rules.py          # Regel-Engine
│   ├── actions.py        # formale Aktionsdefinitionen
│   ├── cards.py          # Townsfolk, Crew, Offerings
│   ├── board.py          # Village + Raids
│   └── engine.py         # Turn-Loop, Endbedingungen
│
├── agents/
│   ├── random_agent.py
│   ├── heuristic_agent.py
│   ├── rl_agent.py
│
├── rl_env/
│   └── raiders_env.py
│
├── training/
│   ├── selfplay.py
│   ├── train.py
│
├── analytics/
│   ├── logger.py
│   ├── stats.py
│   └── visualization.py
│
├── ui/
│   └── gui.py
│
└── README.md

⚙️ Phase 1 – Spiel-Engine (deterministisch + simulativ)
Ziel

Eine vollständig regelkonforme Simulation ohne UI.

Kernkonzepte
Spielzustand (GameState)

Enthält u.a.:

Spieler:

Ressourcen (Silber, Provisions, Plunder)

Handkarten

Crew

Armour

Valkyrie-Track

VP

Worker in Hand

Board:

Village-Gebäude + belegte Worker

Raiding-Spaces inkl. Plunder

Kartenstapel

Offering Tiles

Rundenzähler + Endbedingungen

Aktionen

Formalisieren als diskrete Aktionen:

Work-Phase

PlaceWorker(building)

PickupWorker(building)

PlayCard(card)

HireCrew(card)

BuyArmour(...)

TakeResources(...)

Raid-Phase

Raid(settlement, worker_color)

Alle Aktionen müssen:

✔ legalitätsgeprüft werden
✔ den GameState transformieren

Wichtige Designentscheidung

👉 Trenne strikt:

Regellogik (pure functions)

State (immutable oder kontrolliert mutierend)

Das ist extrem wichtig für RL + Replays + Debugging.

🤖 Phase 2 – Reinforcement Learning Environment
Ziel

Kompatibel zu Gymnasium/OpenAI Gym Stil.

obs, reward, done, info = env.step(action)

Beobachtungsraum (Observation Space)

Empfohlen: Vektorisiert + normalisiert.

Beispiel:

Eigene Ressourcen

Gegner-Ressourcen (aggregiert oder einzeln)

Crew-Komposition

verfügbare Worker-Plätze

verbleibende Plunder

Offering Tiles

Spielphase

Optional:
➡️ separate Feature-Gruppen (Board, Player, Global)

Aktionsraum

Diskret, z.B.:

0-20   Work-Aktionen
21-40  Raid-Aktionen
...


Oder hierarchisch (Advanced):

Erst Phase wählen

dann konkrete Aktion

Reward-Design

Minimalstart:

✅ + Endgame VP Differenz

Später shaping:

VP während Spiel

effiziente Raids

Offering completion

Vermeide zu starkes shaping → sonst lernt KI falsche Strategien.

🔁 Phase 3 – Self Play Training
Ablauf

KI spielt tausende Spiele gegen sich selbst

Policy wird nach jedem Batch verbessert

Optional:

Elo-Ranking der Agenten

Population Based Training

Algorithmen (empfohlen)

Start einfach:

PPO (stable-baselines3)

später evtl.:

AlphaZero-Style (MCTS + NN)

📊 Phase 4 – Statistik & Analyse
Erfasste Daten pro Spiel
Nach Spieleranzahl getrennt:
Aktionen

Häufigkeit:

Worker platzieren (Gebäude)

Worker aufnehmen

Raid-Typen

Karten

Gespielte Townsfolk

Gehirete Crew

Kombinationen

Aktion A → Aktion B

Karte + folgende Aktion

Crew-Kombinationen

Erfolgsmessung

Winrate pro Aktion

Winrate pro Karte

Winrate pro Kombi

Beispiel:

Raid Monastery mit >=20 Stärke → 63% Winrate
Sage + Offering Rush → 71% Winrate

Tools

pandas

matplotlib / seaborn

optional: Jupyter notebooks

🎮 Phase 5 – Mensch gegen KI Modus
Funktionen

✅ Anzeige:

aktueller Spielstand

Ressourcen

Crew

✅ KI:

berechnet:

Sieg-Wahrscheinlichkeit (Value Network)

beste Aktion (Policy)

Beispiel:

Win chance:
You: 42%
AI: 58%

Recommended move:
Place worker at Silversmith → Pickup Town Hall
(Expected value +1.7 VP)

🖥 UI (bewusst einfach halten)

Optionen:

pygame

Wichtig:
➡️ UI darf niemals Kernlogik enthalten

Nur State visualisieren + Inputs weiterreichen.

📈 Erweiterungen (optional später)

Erweiterungen vom Brettspiel

Menschliche Heuristik-Agenten

Explainable AI (warum Zug empfohlen?)

Replay Viewer

🧪 Testing

Unbedingt:

Unit Tests für Regeln

deterministische Seeds

Replaybarkeit

Beispiele:

Ressourcen nie negativ

illegale Züge blockiert

Endbedingungen korrekt

🗓 Grober Zeitplan (realistisch)
Phase	Aufwand
Spiel-Engine	2–4 Wochen
RL-Env	1 Woche
Training	1–3 Wochen
Statistik	1 Woche
UI	2–4 Tage
📌 Zentrale Erfolgsfaktoren

✅ Saubere Zustandsrepräsentation
✅ Trennung von Logik & Darstellung
✅ Einfach starten, dann iterativ verfeinern
✅ Erst random + heuristics → dann RL