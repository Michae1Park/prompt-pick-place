# Stage 1 — YOLOE detection playground

Give YOLOE prompts (or none) + a scene image → see every detection (box, mask, score) and how fast it ran.

## Which script

| Want | Use | Where it runs |
|---|---|---|
| **Live**: sliders, image re-renders on every change | `notebooks/yoloe_playground.ipynb` | Cursor notebook (or JupyterLab), workstation `.venv` |
| **One command**, reproducible, scriptable | `pipeline/interactive_detect.py` | Cursor terminal, workstation `.venv` |

Both use the same code (`vision/detect.py`) and the same defaults (`config.yaml`).

## Commands

Two machines: your **laptop** (where you sit) and the **workstation** (has the GPU; everything runs here).

### With Cursor / VS Code Remote-SSH (recommended)

Connect Cursor to the workstation and open the `prompt-pick-place` folder. From then on, Cursor's
**terminal, file explorer and notebooks all run on the workstation** — you don't type anything on the laptop.

**One-time**: Extensions panel → install **Python** and **Jupyter** (Cursor installs them on the workstation side).

**CLI** — open a terminal in Cursor (`` Ctrl+` ``):
```bash
source .venv/bin/activate        # once per terminal; prompt now starts with (.venv)
python pipeline/interactive_detect.py --text "mustard bottle"                                   # one text prompt
python pipeline/interactive_detect.py --text "mustard bottle" --text banana --text "cracker box" # several classes
python pipeline/interactive_detect.py --ref 006_mustard_bottle                                  # visual prompt (ready-made)
python pipeline/interactive_detect.py --prompt my_obj path/ref.png 120,80,340,410               # visual prompt (your own)
python pipeline/interactive_detect.py --prompt-free --conf 0.25                                  # no prompt: detect everything
python pipeline/interactive_detect.py --text "mustard bottle" --conf 0.3 --iou 0.5 --imgsz 1280 --tag hi_res
python pipeline/interactive_detect.py --ref 006_mustard_bottle --scene third_party/FoundationPose/demo_data/mustard0/rgb/1581120424100262102.png
python pipeline/interactive_detect.py --help                                                    # all flags
```
Each run prints a table, saves the overlay to `output/yoloe/<tag>.png`, and **opens it as a tab in Cursor**.
The tab stays until you close it and refreshes on every re-run.

**Notebook**:
1. Open `notebooks/yoloe_playground.ipynb` in the file explorer.
2. Top right → **Select Kernel** → **Python Environments** → `.venv` (`.venv/bin/python`).
3. Click into the code cell → **Shift+Enter**. Sliders appear under the cell; move them.

No JupyterLab, no port forwarding needed.

If the notebook misbehaves in Cursor:
- **Cell runs but no sliders/image appear.** The widget JavaScript is downloaded by the *laptop*, and unpkg.com is unreachable from it. `.vscode/settings.json` already points Cursor at jsDelivr first; after changing it, **Ctrl+Shift+P → Developer: Reload Window**. Check: Output panel → **Jupyter** shows `Failed to access CDN`.
- **Notebook changed on disk (git pull, someone else edited it) but Cursor shows the old version.** Running cells marks the notebook unsaved, and Cursor keeps its unsaved copy even across restarts. **Ctrl+Shift+P → File: Revert File**, then restart the kernel. Don't Ctrl+S first: that writes the old copy over the new one.

### With a separate terminal (e.g. Windows PowerShell)

Windows 10/11 ship `ssh` and `scp`, so PowerShell works as-is.

**Laptop (PowerShell)** — log in. The `-L` part is only needed for the notebook: it makes the laptop's
port 8888 lead to the workstation's port 8888.
```powershell
ssh -L 8888:localhost:8888 <user>@<workstation>
```
**Workstation** (you're now in the SSH session; this is bash):
```bash
cd ~/workspace/prompt-pick-place
source .venv/bin/activate
python pipeline/interactive_detect.py --text "mustard bottle"     # CLI, same flags as above (no image pop-up here: no display)
jupyter lab --no-browser --port 8888                              # notebook; Ctrl+C to stop
```
**Laptop (browser)** — open the printed `http://localhost:8888/lab?token=...` URL → open the notebook → Shift+Enter.

**Laptop (a second PowerShell window)** — copy a CLI image over and open it:
```powershell
scp <user>@<workstation>:~/workspace/prompt-pick-place/output/yoloe/play.png .
start play.png
```

- `port 8888 is already in use` → use `-L 8889:localhost:8888` and open `localhost:8889` instead.
- Closing the PowerShell window stops JupyterLab. To keep it running, start it inside `tmux` on the workstation.

## Model weights

| File | What | Set by |
|---|---|---|
| `yoloe-11l-seg.pt` (`models/`, 71 MB) | YOLOE detector + seg head — **the default** | `config.yaml` → `detect.weights` |
| `yoloe-11s-seg.pt` / `-11m-` (`models/`) | smaller variants | `--weights` / notebook dropdown |
| `yoloe-11{s,m,l}-seg-pf.pt` (`models/`, 74 MB for l) | prompt-free variant: same network, fixed 4585-class vocabulary | `--prompt-free` / notebook prompt **none** (same size as `--weights`) |
| `mobileclip_blt.ts` (`models/`, 600 MB) | text encoder, used **only for text prompts** | loaded automatically by ultralytics |

- All live in `models/` (gitignored) and auto-download there on first use. `config.yaml` uses the bare file name.
- The weights in use are printed on every run (`weights=...` line) and shown in the notebook dropdown.

## Inputs

| Input | How to give it | Default |
|---|---|---|
| Scene image (RGB) | `--scene PATH` / notebook "scene" dropdown or "or path" | `data/multi_object_scene/scene_rgb.png` |
| Text prompt | `--text "name"` (repeat) / notebook: comma-separated | — |
| Visual prompt, ready-made | `--ref NAME` → `data/multi_object_scene/refs/NAME.{png,json}` | — |
| Visual prompt, your own | `--prompt NAME IMAGE X0,Y0,X1,Y1` / notebook "own ref": `name \| path \| x0,y0,x1,y1` | — |
| No prompt (prompt-free) | `--prompt-free` / notebook: prompt **none** | — |

- One prompt kind per run: text, visual **or** prompt-free.
- Prompt-free swaps `--weights` for the `-pf` file of the same size (e.g. `yoloe-11l-seg-pf.pt`, auto-downloaded), which detects from a fixed 4585-class vocabulary. Expect many low-score detections and generic names ("bottle"); raise `--conf`.
- Visual prompt = an image + a box (pixels, `x0,y0,x1,y1`) around the object in that image.
- To add a ready-made ref: put `NAME.png` + `NAME.json` (`{"bbox": [x0, y0, x1, y1]}`) in `data/multi_object_scene/refs/`.

## Knobs

Defaults live in **`config.yaml` → `detect:`**. CLI flags / notebook controls override them for that run.

| Knob | Flag | What it does | Try |
|---|---|---|---|
| `weights` | `--weights` | Model size. `yoloe-11s/m/l-seg.pt` (auto-downloaded) | s = faster, l = fewer false positives |
| `conf` | `--conf` | Hide detections scoring below this. Prompt-free: also skips naming low-objectness cells, so higher = faster | 0.05 (see everything) → 0.3 (clean) |
| `iou` | `--iou` | NMS: merge boxes overlapping more than this | 0.3 → 0.9 on duplicate boxes |
| `imgsz` | `--imgsz` | Inference resolution | 320 / 640 / 1280 |
| `max_det` | `--max-det` | Keep at most N detections | 1 = "just the best" |
| `half` | `--half` | FP16 inference | compare speed and scores |

Changing prompts or weights rebuilds the model (~0.5–2 s). Everything else only re-runs predict (~17 ms on the L40S; prompt-free 20–40 ms depending on `conf`).
Most of a text rebuild is reloading the YOLOE weights and MobileCLIP from disk; swapping the class vectors itself takes < 0.1 ms.

## Outputs

| Output | Where |
|---|---|
| Table: class, score, box `xyxy`, mask pixel count | terminal (CLI) / under the controls (notebook) |
| Model build time + predict p50 (ms) | same |
| Overlay image (all masks + boxes + labels) | CLI: `output/yoloe/<tag>.png` (`--tag`, default `play`). Notebook: live, plus **save** |
| Settings + detections as JSON | notebook **save** → `output/yoloe/<tag>.json` |
| Equivalent CLI command | printed under the notebook image (copy it to reproduce) |

## How it works

What we established by reading the checkpoints tensor by tensor and the ultralytics 8.3.150 head code.

**One network, three ways to name things.** `yoloe-11l-seg.pt` and `yoloe-11l-seg-pf.pt` share the backbone, neck, box branch and mask branch bit for bit (33.2M parameters). They differ only in the last layers of the class branch.

**Everything happens per grid cell.** The neck produces 80×80 + 40×40 + 20×20 grids (8,400 cells for a 640×640 input, 6,300 for the 640×480 multi-object scene). Every cell outputs one row: `box (4) | class scores (N) | mask coefficients (32)`.

**A class is just a vector.** Each cell's class branch outputs a 256-number feature. How it becomes a class score depends on the mode:

| Mode | Where the class vectors come from | Per scene |
|---|---|---|
| text | phrase → MobileCLIP (`mobileclip_blt.ts`) → `reprta` refiner → 512-d vector. Built at runtime, once per prompt list | every cell: 256→512, dot with the N vectors |
| visual | ref image + box → same backbone/neck → `savpe` pools the box → 512-d vector. Built at runtime, once per ref | same as text: identical computation |
| prompt-free | 4,585 names encoded by the YOLOE authors and folded into `lrpc.vocab` (4585×256), stored in the `-pf` file | every cell: one "is it an object?" score; only cells above `conf` are compared with the 4,585 vectors |

- Text and visual rows could be mixed in one class table (both are 512 numbers). The code here doesn't do that.
- With the prompted weights and **no prompts set, you get 0 detections and no error.**
- `model.set_classes(...)` then `model.save('x.pt')` stores the prompt vectors in the file; reloading it needs no prompts and no MobileCLIP.

**Boxes and masks are never filtered by the prompt directly.** Every cell predicts a box and mask coefficients regardless. The class score is the only filter, and the box and mask ride along with it:

```
6,300 cells ─ conf 0.05 ─► 23 ─ NMS iou 0.7 (per class) ─► 4 ─ max_det ─► 4 ─ build masks ─► 4 detections
```
(`--text "mustard bottle" --text banana` on the multi-object scene.) Masks are built last, only for survivors: 32 prototype masks (shared per image) × the detection's 32 coefficients → upscaled (`retina_masks`) → **cropped to its own box** → pixels > 0. An empty mask drops the detection.

## Things to try

1. **Wording**: `"mustard sauce"` vs `"mustard bottle"` vs `"yellow bottle"` vs `"condiment"`.
2. **Distractor classes**: one class vs all five object names. Watch the false positives get their real labels.
3. **Visual vs text** for the same object. Visual matched the yellow banana weakly (0.05). Why?
4. **NMS**: `--iou 0.3` vs `0.9` on the "power drill" boxes.
5. **Prompt quality**: tight box vs loose box; prompt image from a different angle.
6. **Model size × speed**: `11s` / `11m` / `11l` — note scores are not comparable across models.
7. **Prompt-free**: what does the built-in vocabulary call each object? Compare its boxes with the prompted ones (same box branch, so they should match).

## Gotchas

- ROS sourced in your shell? Its `PYTHONPATH` leaks into `.venv`. Harmless so far; if imports act up, prefix `env -u PYTHONPATH`.
- Set `YOLO_VERBOSE=True` to see ultralytics' own logging (the CLI and notebook hide it).
- Two identical prompts (same image + box) → identical embeddings → only one class name wins each box.
