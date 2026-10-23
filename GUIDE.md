# Using Le_SensVisual

**A practical guide to creating, reviewing and improving visual communication.**  
By TH_Ng

Le_SensVisual helps an AI turn a brief into a visual experience that belongs to its subject. Use it for images, presentations, teaching material, posters, editorial pages, charts and interfaces.

You describe the audience, message and required result. The skill guides the visual decisions and appropriate production process. You can then request focused improvements in ordinary language or with the specialist actions below.

[Quick start](#quick-start) · [Write a useful brief](#write-a-useful-brief) · [How it works](#how-it-works) · [Micro commands](#micro-commands) · [Improve a result](#improve-a-result) · [Access and tools](#access-and-tools)

## Quick start

### Coding agents

Run the Skills CLI in a terminal and select your supported agent:

```bash
npx skills add zacqual-sudoGit/Le_SensVisual --skill le-sensvisual
```

Add `-g` for installation across projects. This installer requires Node.js 22.20 or later. Alternatively, use the included Python installer described in [Installation](le-sensvisual/INSTALL.md).

Once your agent recognises the skill, select it through the host's skill mechanism or ask:

> Use Le_SensVisual to create a one-page welcome guide for customers moving into their first HDB home. Help them prepare for moving week and understand moving day. Produce one image in English. Use the facts below and choose the remaining design decisions yourself.

Add your required facts after the brief. Command syntax varies by host; ordinary wording is useful when a slash command is unavailable.

### Claude chat with custom Skills

1. Download **Le_SensVisual-v0.4.0-rc.23.zip** from [Releases](https://github.com/zacqual-sudoGit/Le_SensVisual/releases/tag/v0.4.0-rc.23).
2. Enable Code execution and file creation in Claude's capability settings.
3. Open **Customize → Skills**, choose **Create skill → Upload a skill**, upload the ZIP and enable it.
4. Start a new chat and ask Claude to use Le_SensVisual with your brief.

Use the complete native ZIP for this route. [Claude's official Skills guide](https://support.claude.com/en/articles/12512180-use-skills-in-claude) describes current availability and controls.

### ChatGPT, Gemini and other ordinary chats

For apps without native skill installation, attach the **chat-guidance ZIP** from the release. First send:

> Read the attached Le_SensVisual guidance, starting with SKILL.md. Follow the references relevant to my next task and inspect the relevant visual example. Confirm which text and images you could actually access. Report anything unreadable before proceeding.

Send your task after access is confirmed. If ZIP reading fails, attach the **complete-guidance TXT** and the four [reference images](le-sensvisual/examples/INDEX.md) separately. The TXT contains the written library, not the image pixels.

This loads guidance into a conversation; it does not create a permanent installation or add tools. A GitHub URL alone is not a dependable full-package loading route: a browsing service may miss files or fail to view images even when the repository is public.

## Write a useful brief

Include what matters. A short brief can be sufficient:

> **Create [deliverable] for [audience]. Help them understand or do [goal]. Include [required content]. Deliver [format]. Respect [important constraints].**

Useful details include supplied facts, required wording, brand assets, language, intended display size and any editing requirements. If the format is open, ask the agent to choose a suitable supported format.

**Example — teaching**

> Use Le_SensVisual to explain how a seed becomes a young plant to primary-school students. Include the roles of water, warmth and air, then show why a growing seedling needs light. Create one classroom poster in English. Use age-appropriate explanations and check the science.

**Example — editable presentation**

> Use Le_SensVisual to create a three-slide proposal for a workplace reusable-container programme. Explain the employee experience, the collection-and-return process, and a small trial we could evaluate. Deliver a PPTX with editable headings and body text. Use the supplied operating facts; label proposed trial settings clearly.

**Example — review**

> Use Le_SensVisual to review this guide. Assess the subject world, supporting visual opportunities, relationships and readability. Explain the most consequential improvements before changing the file.

You do not need to prescribe every illustration, tool call or assembly step. When an exact method or editable element matters, state it explicitly.

## How it works

TYY is the visual foundation. Its purpose is to make the subject recognisable and the message understandable through a coherent world, meaningful imagery and readable composition.

| Stage | What the skill guides |
|---|---|
| Understand the job | Establish the audience, message, facts, output and constraints. |
| Resolve the visual experience | Decide what the viewer should see and understand, including supporting sections. |
| Choose suitable tools | Select a supported production route for the design and requested output. |
| Coordinate production | Generate or source contributions where useful, transfer actual assets, assemble where needed and harmonise the result. |
| Review and deliver | Inspect the artifact, restore missing meaning, check readability and facts, and disclose material limitations. |

An illustrated opening can establish the world. Supporting scenes, objects, symbols, relationships and quiet reading areas carry it through the rest of the work. More assets are not automatically better; each visual contribution should serve the audience and composition.

For example, a moving guide might show a measurement at a doorway, fragile items being packed and a first-night bag with its contents. These make the instructions tangible. A large arrival image alone does not resolve those supporting opportunities.

The skill can guide a complete generated image or a composition assembled through multiple tools. HTML, PowerPoint and image generation are production options, selected for the job. None is the universal default.

Explore the [four visual references and their provenance](le-sensvisual/examples/INDEX.md). They teach transferable decisions rather than fixed layouts or reusable factual claims.

## Micro commands

These **24 named actions are agent playbooks**, adapted into Le_SensVisual's TYY workflow. They are not separately registered slash commands in every app. Use ordinary language:

> Use Le_SensVisual: **layout**. Improve the reading order of this page while preserving its illustrated identity.

### Review and visual refinement

| Action | Use it to… |
|---|---|
| `critique` | Assess the actual design against TYY, audience needs and relevant interface considerations. |
| `polish` | Refine the requested scope, addressing missing visual meaning before incidental details. |
| `bolder` | Increase emphasis, character and impact. |
| `quieter` | Reduce visual intensity and competition while retaining useful meaning. |
| `distill` | Remove redundancy while preserving the subject world and required information. |
| `layout` | Improve structure, hierarchy, spacing and rhythm. |
| `typeset` | Improve font choices, scale, hierarchy and readability. |
| `colorize` | Use colour purposefully for emphasis, distinction and expression. |

The specialist playbooks focus on interfaces. Their relevant visual decisions can inform other media without turning a poster or slide into a website.

### Planning and reusable systems

| Action | Use it to… |
|---|---|
| `shape` | Resolve a design brief and consequential direction. |
| `init` | Capture missing durable product facts and constraints. |
| `craft` | Start new interface work through the parent TYY workflow. |
| `document` | Record an implemented visual system in DESIGN.md and its supporting data. |
| `extract` | Consolidate repeated interface patterns into reusable components and tokens. |

### Interface experience and quality

| Action | Use it to… |
|---|---|
| `audit` | Report relevant accessibility, performance, theming and responsive issues. |
| `clarify` | Improve labels, instructions, error messages and other interface copy. |
| `adapt` | Adapt a design for different screens, devices, contexts or platforms. |
| `harden` | Address error states, localisation, overflow and content extremes. |
| `onboard` | Help first-time users reach value through onboarding and useful empty states. |
| `optimize` | Diagnose and improve loading or rendering performance. |
| `animate` | Add purposeful motion and interaction feedback. |
| `delight` | Add appropriate personality and memorable touches. |
| `overdrive` | Develop ambitious interface effects and interactions where they serve the experience. |

### Live interface exploration

| Action | Use it to… |
|---|---|
| `live` | Explore browser variants, adjust parameters and accept or discard changes. |
| `generate` | Produce variants of a named interface element in a requested direction. |

`generate` means interface variants here, not a general image-generation command. These two workflows require the appropriate engine, browser integration and development setup. Reading their instructions alone does not enable live operation.

You can combine a small number of relevant actions. For example: “Critique the page first, then fix the main layout and typography problems.” A review-only request should remain a review.

## Improve a result

Describe the missing benefit and the scope to preserve:

> The opening establishes the topic, but the lower sections are mostly text. Show the important actions within those sections while keeping their copy readable.

> Make this quieter. Keep the useful illustrations and reduce competing decoration.

> The process is hard to follow. Make the sequence and handoff visible without adding unsupported steps.

> Polish the headings and spacing. Preserve the existing artwork and content.

For a review, ask the agent to identify what meaning is visible, where it appears and which useful opportunity remains missing. The [eleven TYY lenses](le-sensvisual/references/tyy-anchor.md) provide a deeper review framework; they are not an illustration quota.

## Access and tools

The main native and chat packages include all four visual references and the complete written guidance. Specialist resources load according to the task. Optional engine, extension, upstream-source and full construction companions support specific advanced workflows.

Actual execution depends on the host. Image generation, file transfer, editable authoring, rendering and browser interaction are separate capabilities. If one is unavailable, the agent should explain the effect on the requested result rather than claim completion.

The skill does not guarantee factual accuracy or consistent results across models. Supply reliable facts, review consequential claims and inspect the final artifact at its intended size. See [release status](le-sensvisual/RELEASE-STATUS.md) for the evaluation scope and [installation](le-sensvisual/INSTALL.md) for dependencies.

## Share useful feedback

[Open an issue](https://github.com/zacqual-sudoGit/Le_SensVisual/issues) with the skill version, host/model, available tools, brief and resulting artifact. Explain which visual benefit worked or was missing. Remove private information before posting.

[Back to README](README.md) · [Release downloads](https://github.com/zacqual-sudoGit/Le_SensVisual/releases/tag/v0.4.0-rc.23) · [Licensing and credits](le-sensvisual/LICENSING.md)
