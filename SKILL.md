# Image Generation & Editing Skill (Azure OpenAI)

This skill allows the agent to generate new images from text prompts or edit existing images using reference files via Azure OpenAI's GPT-Image-1.5 model.

## Configuration

- **Script**: `gen.py`
- **Environment**: `/home/thomas/.env.azure` (Required for API credentials)
- **Output**: Images are saved to the `./out/` directory with a timestamped filename.

## Usage

### 1. Generate New Image
Use this mode when the user wants to create an image from scratch.
**Syntax:** `python3 gen.py "<detailed_prompt>"`

### 2. Edit Existing Image
Use this mode when a user provides one or more reference images and requests changes (e.g., changing colors, adding objects, or altering style).
**Syntax:** `python3 gen.py "<edit_instructions>" --edit --ref <path_to_image>`

## Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `prompt` | String | (Positional) The visual description or edit instruction. |
| `--edit` | Flag | Required to trigger image-to-image/editing mode. |
| `--ref` | Path(s) | One or more paths to the images to be used as a reference. |

## Examples

- **Create a new image**: 
  `python3 gen.py "A professional headshot of a solution consultant in a modern office, cinematic lighting"`
  
- **Modify an existing image**: 
  `python3 gen.py "Change the suit color to charcoal gray and add a laptop on the desk" --edit --ref ./out/20260208_120000.png`

## Notes for the Agent
- **Fidelity**: The skill is hardcoded to "high" fidelity to ensure identity and structural persistence during edits.
- **Image Formats**: Input images must be in PNG format.
- **Output**: The tool returns a JSON object containing the `path` to the generated image. Always display this path or the image to the user.