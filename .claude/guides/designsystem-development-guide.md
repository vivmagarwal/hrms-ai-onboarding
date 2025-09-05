# LLM Instructions — Create a Simple, Original Design Guide (Inspiration-Led)

## 0) Use One Source Heavily

From the reference table below, **pick exactly one** source (at random or by fit) and **draw heavily from its ideas** (tokens, spacing, motion, component anatomy) while keeping the final guide **simple, original, and minimal**.

---

## 1) Reference Catalog (Design Systems & Webflow Themes)

| Category      | Name                               | Special qualities                                      | Color vibe (most-used)                       | Short description                                        | More info                                                                                                                                                |
| ------------- | ---------------------------------- | ------------------------------------------------------ | -------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Design system | Airbnb (new design guide preview)  | Founder-led refresh; new font/nav; color & icon revamp | Warm coral/red accents, soft neutrals        | Public preview of an upcoming system-wide visual update. | `https://x.com/bchesky/status/1937335063051714835` ([Design Compass][1])                                                                                 |
| Design system | Apple Human Interface Guidelines   | Platform guidance; clarity/deference/depth; patterns   | Grays/whites, semantic accents               | Canonical product guidance across Apple platforms.       | `https://developer.apple.com/design/human-interface-guidelines/` ([Apple Developer][2])                                                                  |
| Design system | Material Design 3                  | Dynamic color (Material You); tonal palettes; tools    | Adaptive palettes; neutrals + derived accent | Google’s latest open-source system and components.       | `https://m3.material.io/` ([Material Design][3])                                                                                                         |
| Design system | Fluent 2 (Microsoft)               | Cross-platform tokens; UI kits; dev frameworks         | Neutral grays, blues/teals                   | Microsoft’s modernized system + Fluent UI.               | `https://fluent2.microsoft.design/` ([Fluent 2 Design System][4])                                                                                        |
| Design system | Adobe Spectrum                     | Tokens, components; Spectrum 2 roadmap                 | Neutral grays, blue/purple accents           | Adobe’s cohesive, tokenized system.                      | `https://spectrum.adobe.com/` ([Spectrum][5])                                                                                                            |
| Design system | IBM Carbon                         | Open source; robust components; IBM Plex type          | Cool grays, blues/teals                      | Enterprise system with foundations, code, and kits.      | `https://carbondesignsystem.com/` ([Carbon Design System][6])                                                                                            |
| Design system | Salesforce SLDS 2 + Cosmos         | Global styling hooks; theme opt-in; validator          | Salesforce blues, neutrals                   | Newer theming via CSS custom properties.                 | `https://trailhead.salesforce.com/.../salesforce-lightning-design-system-2-for-developers/explore-salesforce-lightning-design-system-2` ([Trailhead][7]) |
| Design system | SAP Fiori (Web)                    | Enterprise patterns; Fiori web UI kit                  | SAP blues, grays, yellow accents             | Official portal for Fiori Web guidelines & kits.         | `https://www.sap.com/design-system/fiori-design-web/` ([SAP][8])                                                                                         |
| Design system | Shopify Polaris                    | Admin-first patterns; tokens; web components           | Neutrals with Shopify green                  | Design + dev system for Shopify admin/apps.              | `https://polaris-react.shopify.com/` ([Polaris React][9])                                                                                                |
| Design system | Atlassian Design System            | Extensive components; content standards; primitives    | Atlassian blues, grays                       | Product-ready components & foundations.                  | `https://atlassian.design/` ([Atlassian Design System][10])                                                                                              |
| Design system | GitHub Primer                      | Open-source; Octicons; React + CSS                     | Cool grays, blue links, green status         | GitHub’s design system & tooling.                        | `https://primer.style/` ([Primer][11])                                                                                                                   |
| Design system | Vercel Geist                       | Minimal, crisp components; strong typography           | Refined grayscale with subtle accents        | System for consistent, delightful web experiences.       | `https://vercel.com/geist/introduction` ([Vercel][12])                                                                                                   |
| Design system | Zendesk Garden                     | Clear foundations; voice & tone; production code       | Zendesk green + neutrals                     | System for product UI with docs & components.            | `https://garden.zendesk.com/` ([Zendesk Garden][13])                                                                                                     |
| Design system | GOV.UK Design System               | Research-backed; highly accessible; community          | Black/white, GOV.UK yellow/blue              | Government service design system & patterns.             | `https://design-system.service.gov.uk/` ([GOV.UK Design System][14])                                                                                     |
| Design system | USWDS                              | Federal standard; accessibility; Public Sans           | Navy/blue, red, gold, cool grays             | U.S. government design system + code.                    | `https://designsystem.digital.gov/` ([U.S. Web Design System (USWDS)][15])                                                                               |
| Design system | Uber — Base (language)             | Unified foundations across Uber                        | Black/white brand, subtle green              | Core design language & patterns.                         | `https://base.uber.com/` ([Uber Base][16])                                                                                                               |
| Design system | Base Web (React)                   | React implementation of Base                           | Dark/light themes, neutrals                  | Open-source component library for Base.                  | `https://baseweb.design/` ([baseweb.design][17])                                                                                                         |
| Design system | Audi UI (React)                    | Brand-authentic components; Storybook docs             | Audi red accents, black/white                | Official product library and guidance.                   | `https://react.ui.audi/` ([react.ui.audi][18])                                                                                                           |
| Design system | Elastic UI (EUI)                   | React components; theming; a11y focus                  | Navy/blue, teal, grays                       | Elastic’s framework with strong docs.                    | `https://eui.elastic.co/` ([eui.elastic.co][19])                                                                                                         |
| Design system | Ant Design                         | Enterprise React library; rich ecosystem               | Blues, neutrals                              | Full-stack components + design language.                 | `https://ant.design/` ([Ant Design][20])                                                                                                                 |
| Design system | Chakra UI                          | Accessibility-first; tokens; composable props          | Teal/cyan accents, neutrals                  | Simple, modular React component system.                  | `https://www.chakra-ui.com/` ([Chakra UI][21])                                                                                                           |
| Design system | Mozilla Protocol                   | Web components + guidelines                            | Deep grays, Mozilla red, white               | Mozilla’s marketing/web design system.                   | `https://protocol.mozilla.org/` ([Mozilla Protocol][22])                                                                                                 |
| Design system | Washington Post — WPDS             | Token-led; newsroom-grade components                   | Inky blacks, grays, blue/red accents         | Reader-facing system & docs.                             | `https://wpds-docs-7ky0cg37i.preview.now.washingtonpost.com/` ([Washington Post][23])                                                                    |
| Design system | Dynatrace — Barista                | Angular components; scalable patterns                  | Dark neutrals, bright green                  | Dynatrace’s design system (OSS).                         | `https://github.com/dynatrace-oss/barista` ([GitHub][24])                                                                                                |
| Design system | SEEK — Braid                       | Themeable; Playroom prototyping                        | SEEK blue, neutrals                          | Themeable system for SEEK Group.                         | `https://www.npmjs.com/package/braid-design-system` ([Npm][25])                                                                                          |
| Design system | Spotify — Encore                   | “System of systems”; distributed ownership             | Spotify green + dark UI                      | Multi-layered system across platforms.                   | `https://spotify.design/article/can-i-get-an-encore-spotifys-design-system-three-years-on` ([Spotify Design][26])                                        |
| Webflow theme | Flowbase — Radar                   | Huge component set; SaaS/fintech layouts               | Light/dark variants; gradient accents        | Multipurpose SaaS/finance UI kit.                        | `https://www.flowbase.co/templates/radar` ([Flowbase][27])                                                                                               |
| Webflow theme | Flowbase — Corpex                  | Dark-mode SaaS; futuristic details                     | Near-black, neon accents                     | Sleek SaaS marketing template.                           | `https://webflow.com/templates/html/corpex-saas-website-template` ([Webflow][28])                                                                        |
| Webflow theme | Flowbase — Atlantio                | Logistics vertical; interactions/forms                 | Blues/teals, neutral grays                   | Vertical template for logistics.                         | `https://webflow.com/templates/html/atlantio-logistics-website-template` ([Webflow][29])                                                                 |
| Webflow theme | Flowbase — Willow                  | Agency/studio starter; easy theming                    | Light neutrals, pastels                      | Polished agency template.                                | `https://webflow.com/templates/html/willow-agency-website-template` ([Webflow][30])                                                                      |
| Webflow theme | Flowbase — Onyx                    | Dark SaaS aesthetic; modern type                       | Deep grays/black; cool accents               | Elegant dark template for tech/SaaS.                     | `https://webflow.com/templates/html/onyx-saas-website-template` ([Webflow][31])                                                                          |
| Webflow theme | BRIX — Dashly X (Dashboard UI Kit) | Large dashboard kit; many pages                        | Dark/light UI; brandable accents             | Data-heavy admin UI kit.                                 | `https://brixtemplates.com/templates/dashboard-webflow-template-ui-kit` ([Flowbase][27])                                                                 |
| Webflow theme | BRIX — Portfolix X                 | Creator portfolio; CMS + shop                          | Light neutrals; bold accents                 | Interactive portfolio system.                            | `https://webflow.com/templates/html/portfolixx-website-template` ([Brix Templates][32])                                                                  |
| Webflow theme | BRIX — Capital X                   | Venture capital vertical                               | Dark navy/black; gold/blue                   | VC/finance template set.                                 | `https://webflow.com/templates/html/capital-x-website-template` ([Webflow][29])                                                                          |
| Webflow theme | BRIX — Fincoin X                   | Crypto/DeFi vertical; 26+ pages                        | Dark backgrounds; neon greens/blues          | Fintech/crypto template.                                 | `https://webflow.com/templates/html/fincoinx-website-template` ([Flowbase][33])                                                                          |
| Webflow theme | Elastic Themes — Bella             | Conversion-minded shop patterns                        | Clean light UI; black text + accent          | Stylish e-commerce template.                             | `https://www.elasticthemes.com/templates/bella` ([Elastic Themes][34])                                                                                   |
| Webflow theme | Elastic Themes — Legend            | Dark stylish UI kit; unique layouts                    | Dark neutrals; vivid accent                  | Agency-friendly UI kit.                                  | `https://www.elasticthemes.com/templates/legend` ([Elastic Themes][35])                                                                                  |
| Webflow theme | Elastic Themes — Persona           | Personal/portfolio kit; many variants                  | Light/dark; personal accent                  | Flexible personal/creative template.                     | `https://www.elasticthemes.com/templates/persona` ([Elastic Themes][36])                                                                                 |

> When you pick a source, **cite** the corresponding URL in your guide’s “References” section.

---

## 2) Research (lightweight)

* If tools are available (e.g., headless browser, Playwright MCP, MCP, fetch), **skim 1–2 pages** from the chosen source to confirm: token names (color/type/space), 1–3 exemplar components, any a11y or motion guidance.
* Capture only what’s needed; **don’t copy visuals or wording**.

---

## 3) Premise (two lines)

* **Feel:** 3 adjectives (e.g., calm, helpful, precise).
* **Promise:** one user benefit (e.g., “fast to scan, delightful to act”).

---

## 4) One Signature (make it yours)

* Define **one subtle, consistent signature** (e.g., 12px inner corner cut, dotted divider rhythm, focus halo shape, a motion curve).
* Use it sparingly across key surfaces (Button, Card, Banner) so the look is **recognizable but not busy**.

---

## 5) Minimal Token Set

Define only what’s essential; defaults > variants.

* **Color:** 1 neutral ramp (\~7 steps), 1 primary, 1 accent, statuses (success/warning/error). Optional concise dark mode.
* **Type:** 1 text family, 1 display style; **3 sizes** (body, section, hero) with line-height/letter-spacing.
* **Space:** short scale (4/8/12/16/24/32).
* **Shape:** 1 small radius + **signature** radius/shape.
* **Elevation:** 2 levels (rest/hover).
* **Motion:** 1 duration-in, 1 duration-out, 1 easing; define focus/entry behavior.
* **Iconography:** 1 grid (box + stroke).

---

## 6) Core Components (defaults first)

Document **five** components clearly with usage + states + a11y notes:

1. **Button** (default/hover/disabled/loading)
2. **Input** (rest/focus/error/help text)
3. **Card** (rest/hover/selected; show the signature)
4. **Table Row / List Item** (rest/hover/selected/overflow)
5. **Banner / Toast** (info/success/warning/error)

---

## 7) Content & Tone

* Voice: **clear, warm, concise**.
* Patterns: headlines, helper text, error copy, empty states.
* Do/Don’t: 2–3 short examples.
* Inclusive language: simple rules.

---

## 8) Layout & Density

* Grid: columns, gutters, margins for desktop/tablet/phone (keep tidy).
* Density: one **comfortable default**; optional **compact** for data views.
* Page templates (brief): landing, form page, data table.

---

## 9) Accessibility (non-negotiable)

* Contrast targets (text, icons, interactive).
* Focus visible (non-color cues).
* Hit-area sizes and spacing.
* Keyboard paths + basic screen-reader semantics.

---

## 10) Originality Guardrails

* **Never copy** verbatim visuals, names, or proprietary illustrations.
* Borrow principles; translate into **your own tokens/behaviors**.
* List **3 explicit differences** from the inspiration (e.g., spacing rhythm, radii, motion curve).

---

## 11) Deliverables

* **Markdown Design Guide** (this doc).
* **Token export** (JSON and/or CSS variables).
* **Mini demo** (static mock or small HTML snippet) showing tokens on Button, Input, Card.

---

## 12) Optional Exploration

* If browsing tools exist, validate assumptions by scanning the chosen source’s **Foundations** and **Components** pages; include **links only** (no long excerpts). Stop when you have enough.

---

## 13) Simplicity Checks (before finishing)

* One-sentence signature?
* ≤ 6 active color tokens in examples?
* ≤ 3 text sizes?
* ≤ 2 elevations?
* Defaults look solid **without** variants?

---

## 14) Output Structure (use exactly this)

1. **Premise** (2 lines)
2. **Inspiration Source** (name + URL)
3. **Signature** (what it is; where it appears)
4. **Foundations / Tokens** (color, type, space, shape, elevation, motion, icon grid)
5. **Components** (Button, Input, Card, Table Row/List Item, Banner/Toast)
6. **Content & Tone**
7. **Layout & Density**
8. **Accessibility**
9. **Divergences from Source** (3 bullets)
10. **Token Export** (JSON/CSS)
11. **Demo Section** (brief snippet)
12. **References** (URLs used)

---

## 15) Randomization (if no preferences given)

* Randomly select the inspiration source **from the table**, a neutral ramp family, and the **signature** detail.
* Keep randomness bounded by the Simplicity Checks.
* Announce what was randomized at the top of the guide.

## 16) Apapt to your preferred CSS framework
* if the website would prefer to use tailwind css, adapt the instruction for tailwind.