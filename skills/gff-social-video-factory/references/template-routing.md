# Template routing

Choose the smallest format that expresses the learning interaction.

| Source and intent | GFF family | Motion building blocks |
| --- | --- | --- |
| Guided Communication preview | `dialogue-pop` | `hero-title`, `chat-bubbles` |
| Simplified Guided Communication with per-turn audio timestamps | `spoken-dialogue` | `hero-title`, `quote-card` |
| Listen-and-repeat with aligned audio | `shadowing` | `speaker-card`, `caption-classic`, progress |
| Scenario challenge | `scenario-pov` | `hero-title`, `prompt-box`, `countdown` |
| Vocabulary recall | `vocab-flash` | `hero-title`, cards, `countdown` |
| Mission sequence | `mission-steps` | `numbered-steps`, `checklist-steps` |
| Long dialogue lesson | `dialogue-lesson` | chapter cards, dialogue, captions, recap |
| Reading: natural two-listen lesson (default) | `reading-teacher` | `reading-coach`, treatment `paper`, brief audio-first teaching then uninterrupted listen |
| Reading: Pause & notice | `reading-teacher` / `pause-and-notice` | `reading-coach`, treatment `paper` |
| Reading: Story first | `reading-teacher` / `story-first` | `reading-coach`, treatment `cinema` |
| Reading: Think & answer | `reading-teacher` / `think-and-answer` | `reading-coach`, treatment `workshop` |

For the three reading-teacher variants, read [long reading videos](long-reading-videos.md).
They use horizontal 1920x1080 at 30 FPS by default, with lesson-length pacing.
The short-video hook/duration guidance below does not constrain these lessons.

Default to `dialogue-pop` for a first Guided Communication preview. Use vertical
1080x1920 at 30 FPS unless the user requests a different platform or aspect
ratio.

Keep the hook under three seconds. Target one meaningful learner action per
short video. Avoid stacking decorative effects that compete with dialogue.
