# Reading video → website → app

## Contract and implementation

All three `reading-coach` treatments share one canonical content URL:
`https://getfluentfast.app/reading/<reading-id>/`.
QR images encode that HTTPS URL, never a custom app scheme. This allows a TV
viewer to scan with a phone and a desktop viewer to see the same content page.
The page's explicit Open in GetFluentFast button uses
`getfluentfast://reading/<reading-id>`. No automatic redirects, guessed app
installation detection, login tokens, or private pedagogy enter the QR.

The iOS parser accepts the HTTPS and custom-scheme forms, validates their host
and ID, and retains the destination in AppState while sign-in and onboarding
complete. RootView opens the existing ReadingPracticeView with the exact ID.
Existing API loading/error/access behavior remains authoritative; a missing
reading must show its actual error, not silently substitute another reading.
The link follows the current reading at that ID, not an immutable revision.
Video provenance continues to retain the exact source revision separately.

The web-first flow intentionally does not add `applinks:getfluentfast.app`:
universal links could skip the requested landing page. HTTPS parsing is ready
if a future approved universal-link configuration is added. The explicit
custom-scheme button works only after this iOS change reaches the installed app.
No Android app route or App Store listing URL has been verified; do not invent
an install destination or claim deferred deep linking through App Store install.
For now, the page tells new users to retain/reopen the page after installation.

## Build and preview

Install `qrcode[pil]==8.2` in a task-specific Python environment. Run
`scripts/gff_reading_links.py --content-id ID --title TITLE --excerpt TEXT
--output renders/reading-links-site` using an explicitly selected public source.
It emits the content page, QR PNG/SVG and a link manifest. Only the supplied
public excerpt is exported; the generator does not copy entire source bundles.
Serve the output directory with a local static server to inspect the page.

The Reading Coach optional `readingLink` props specify canonical URL, QR image,
localized label/instruction and end-card start time. Keep the original reading
and speech timeline intact. Append ten seconds to the spec/overlay duration
for a stationary end card with a 600px QR and four-module white quiet zone.
The small 168px header QR is supplementary; the end card is the TV scan target.
No QR animation, colored modules, logos within the code or fades affect scanning.
Decode the rendered end-card QR and compare it with the manifest URL before
publication. A decoded code proves its payload, not DNS, app installation or
real-TV scanning distance.

For the preserved hotel variants use `scripts/prepare-hotel-reading-links.py`,
then `tsx scripts/render-reading-pilot.mts stills --qr` and `render --qr`.
QR versions have separate work/render directories with `-qr`; originals remain.
Template: `reading-coach`. No caption or narration timing changes are intended.
Validate specs and inspect frames before full renders, and remeasure decoded
audio against the original WAV after export.

## Deployment gate and acceptance

As observed on 2026-09-14, getfluentfast.app did not resolve from the local
runtime. Website hosting/repository is awaiting identification. This package
is local, not a functioning public destination. Do not publish QR videos until:

1. Hosting serves these exact `/reading/<id>/` pages over HTTPS, with assets and
   a real unavailable-content/404 response for unknown IDs (not the home page).
2. The released iOS build routes this ID after cold/warm launch and sign-in.
3. A phone scans the final compressed video on a television and reaches the
   correct page and reading; check both installed and not-installed behavior.
4. Any App Store installation CTA uses a verified listing, and clearly requires
   returning to the same web page after installation unless deferred links are
   separately implemented and tested.

Deploying the website and distributing the iOS build are separate release steps.
No DNS, hosting, canonical content, internal feed or social publication changes
are made by the local generator/render workflow.

## Local verification on 2026-09-14

- iOS `LanguageApp` Simulator build: **BUILD SUCCEEDED**.
- Production URL parser: 11 valid/invalid cases passed, including foreign hosts,
  credentials, ports, extra segments and encoded slash rejection.
- Authenticated Simulator: custom-scheme link opened the exact live hotel
  reading with five sentences and Turkish pedagogy.
- Mobile Safari localhost landing page → explicit app button → OS Open prompt
  → cold app launch: the same live hotel reading was visibly verified.
- Signed-out/onboarding replay is implemented but has not been exercised with
  a fresh account. Actual television/phone scanning and public DNS are untested.
- Landing page tested in browser and mobile Safari; app CTA is above the text.
- Three end-card stills decoded to the exact canonical URL with Apple Vision.
- Final encoded-media measurements are in the QR gallery's `delivery-qa.json`.
