# Le_SensVisual

### Visual communication with a world of its own.

**By TH_Ng · v0.4.0-rc.23 · Public preview · MIT**

Le_SensVisual is an AI agent skill for turning information into coherent visual experiences. It helps an agent recognise the opportunities in a subject: the places, people, objects, actions and relationships that make a message tangible, memorable and easy to understand.

Its foundation is **TYY**: build a recognisable world around the subject, carry meaningful visuals into supporting content, and give the information calm, readable space.

[Get the skill](https://github.com/zacqual-sudoGit/Le_SensVisual/releases/tag/v0.4.0-rc.23) · [How to use](GUIDE.md) · [Installation guide](le-sensvisual/INSTALL.md) · [Visual references](le-sensvisual/examples/INDEX.md) · [Release notes](RELEASE-NOTES.md)

![Gardens composition showing a shared setting and distinct illustrated supporting regions](le-sensvisual/examples/gardens/preview.jpg)

*Gardens is a composition reference: a shared setting, individual audience scenes and readable information working together. Explore the [reference notes](le-sensvisual/examples/INDEX.md) for its origin and transferable decisions.*

## What it brings to your work

- **A subject-specific world.** Use setting, people, objects and atmosphere to make the topic recognisable.
- **Supporting visuals with a purpose.** Look beyond the opening image for opportunities to illustrate an action, explain a relationship or reinforce the message.
- **Readable, harmonious composition.** Coordinate imagery, symbols, colour and typography while protecting the information.
- **One coordinated production process.** Plan the visual experience, choose suitable tools, carry actual assets into the final composition and inspect the result.
- **Freedom of format.** Use images, PowerPoint, HTML, editorial pages, teaching material, charts or interfaces according to the brief and available tools.

The skill guides visual decisions and production. It does not prescribe a single aesthetic, require HTML or force image generation for every task.

## Get started

Read the [user guide](GUIDE.md) for setup by app, example briefs, all 24 micro commands and practical ways to improve a result.

### Coding agents

Install from GitHub using the Skills CLI:

```bash
npx skills add zacqual-sudoGit/Le_SensVisual --skill le-sensvisual
```

Choose your supported agent when prompted. Add `-g` for installation across projects. The CLI requires Node.js 22.20 or later; see the [installer documentation](https://github.com/vercel-labs/skills).

Alternatively, download or clone this repository and use the included installer:

```bash
python le-sensvisual/scripts/install.py --host codex
# For Claude Code:
python le-sensvisual/scripts/install.py --host claude-code
```

Use your agent's skill selector or invoke `le-sensvisual` with a normal brief. See [installation and prerequisites](le-sensvisual/INSTALL.md) for setup and optional tools.

### Claude chat and other chat apps

| Where you use it | What to download | How to use it |
|---|---|---|
| Claude chat Skills | **Le_SensVisual-v0.4.0-rc.23.zip** | Upload through Customize → Skills, then enable the skill. |
| ChatGPT, Gemini or another attachment-based chat | **…-chat-guidance.zip** | Attach it and ask the model to read SKILL.md and the relevant references before your task. Archive support varies. |
| A chat that cannot read ZIPs | **…-complete-guidance.txt** and the four [reference images](le-sensvisual/examples/INDEX.md) | Attach the text and images separately. |

Download these from the [release page](https://github.com/zacqual-sudoGit/Le_SensVisual/releases/tag/v0.4.0-rc.23). Chat attachments provide guidance for the conversation; they do not install tools or create a permanent account-level skill.

### Try a normal brief

> Use Le_SensVisual to create a welcome guide for customers moving into their first HDB home. Help them prepare for moving week and understand moving day. Produce one image in English. Choose the remaining content and design decisions yourself.

Supply the facts your audience needs and specify the output when it matters. The skill is intended to handle the visual planning and appropriate production route.

## Inside the skill

| Component | What it supports |
|---|---|
| TYY core and eleven review lenses | World building, visual meaning, relationships, composition and review |
| Worked decisions and four bundled visual references | Concrete examples of visual opportunities and their execution |
| Production guidance and optional helpers | Artwork, asset transfer, editable PPTX, HTML assembly, extraction and rendering |
| Interface workflows | Design context, components, critique, accessibility, motion, responsive work, hardening and optimisation |
| HTML presentation library | Presentation authoring with 12 presets and 34 detailed style systems |

The main package includes the complete guidance, specialist modules and all four reference images. Resources load according to the task. Larger software, upstream source and full construction studies are available as optional companions; they are not required to read the visual guidance. See the [capability map](le-sensvisual/CAPABILITIES.json).

## Release status and practical limits

**rc.23 is a published release candidate.** It is available for use and feedback while broader validation continues.

The model and host determine execution quality. Image generation, file creation, rendering and editing require tools the host actually provides. Installing the skill does not add those services. A repository link alone may not expose all referenced files or images to a chat model.

The visual references illustrate design decisions, not guaranteed results. Earlier evaluations show promising visual applications; they do not establish consistent performance across models and hosts. rc.23 received package and local-installation checks, with no new model-output evaluation. See [release status](le-sensvisual/RELEASE-STATUS.md) for the verification scope.

## Feedback

[Open an issue](https://github.com/zacqual-sudoGit/Le_SensVisual/issues) with the version, model or agent, available tools, your brief and the resulting artifact. Explain which visual benefit worked or was missing. Remove private information before sharing.

## Licence and acknowledgements

Original work by **TH_Ng** is available under the [MIT licence](LICENSE). Le_SensVisual was previously named VisuaSense.

Adapted Impeccable material retains Apache-2.0 terms. Frontend Slides and bundled dependencies retain their respective licences and credits. See [licensing and acknowledgements](le-sensvisual/LICENSING.md). The original TYY deck is not redistributed; no upstream endorsement is implied.
