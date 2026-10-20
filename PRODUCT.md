# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Enterprise, tactical security administrators, and corporate clients procuring and managing security hardware, network appliances, and surveillance operations.

## Product Purpose
Unified tactical security operations platform: combining an equipment catalog/store with a high-control operations center (inventory, telemetry, logistics, reports, and role-based access).

## Positioning
An integrated tactical security operations portal delivering end-to-end hardware procurement and operational telemetry under an authoritative, high-precision security interface.

## Operating Context
Web-based tactical operations suite serving two core roles (`administrador` and `cliente`). Covers public storefront browsing, order lifecycle tracking, inventory audit reports (PDF/Excel), automated activity logging, and logistics monitoring.

## Capabilities and Constraints
- Python 3 / Flask web stack with Jinja2 templating.
- Dark high-contrast tactical design system (Tailwind CSS CDN + custom design tokens).
- Local JSON datastore architecture (`data/`).
- Standard local server execution on `http://localhost:5000`.

## Brand Commitments
- Brand name: Lycaon Security / Lycaon Software (Control Sys).
- Visual language: Tactical engineering, obsidian/charcoal surfaces (`#09090B`, `#121216`), metallic gold (`#D4AF37`) and telemetry cyan (`#00F0FF`) accents.
- Typography: Inter for UI/display, JetBrains Mono for telemetry/monospaced data.
- Geometric precision: 12px engineering radius, subtle gold-translucent borders (`rgba(212, 175, 55, 0.15)`).

## Evidence on Hand
- Full Flask routing in [app.py](file:///c:/Users/SENA/Desktop/Fundamentos_Flask/app.py).
- Base layouts and UI shells in [templates/base.html](file:///c:/Users/SENA/Desktop/Fundamentos_Flask/templates/base.html) and [templates/dashboard/layout.html](file:///c:/Users/SENA/Desktop/Fundamentos_Flask/templates/dashboard/layout.html).
- Product catalog in [data/inventory.json](file:///c:/Users/SENA/Desktop/Fundamentos_Flask/data/inventory.json) and active user registry in [data/users.json](file:///c:/Users/SENA/Desktop/Fundamentos_Flask/data/users.json).

## Product Principles
- **Tactical Precision**: Instant scanability, high-contrast operational status, and zero visual clutter in critical control views.
- **Unified Command**: Seamless transition between equipment procurement and operational fleet management.
- **Authoritative Identity**: Deep obsidian and metallic gold aesthetic projecting elite defense-grade engineering.
