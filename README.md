
# COSC3000 Major Project – USS Enterprise 3D Graphics Pipeline

## Description

This project implements a real-time 3D graphics rendering system using Python and OpenGL. It visualizes the USS Enterprise model through a structured, step-by-step pipeline that introduces advanced graphics techniques such as Phong lighting, shadow projection, animation, interactivity, and geometric segmentation.

Developed for the COSC3000 Visualisation, Computer Graphics & Data Analysis course at the University of Queensland.

---

## Features by Step

| Step | Description |
|------|-------------|
| **1** | Load and render a 3D `.obj` model |
| **2** | Free-look camera with mouse and keyboard controls |
| **3** | Phong lighting with material and normal support |
| **4** | Projected planar shadows based on light alignment |
| **5** | Interactive toggles for lighting, shadow, and rendering modes |
| **6** | Frame-rate independent animation (orbital, bobbing, figure-eight) |
| **7** | Region-based coloring using geometric segmentation filters |

---

## File Structure

```
uss-enterprise-3d-visualisation/
├── step1_display_object.py
├── step2_camera_controls.py
├── step3_phong_lighting.py
├── step4_projected_shadows.py
├── step5_interactivity.py
├── step6_animation.py
├── step7_advanced_coloring.py
│
├── main.py
├── graphics_utils.py
├── coloring_utils.py
└── USS_enterprise_grayscale.obj
```

---

## Installation

Install dependencies using pip:

```bash
pip install PyOpenGL PyOpenGL_accelerate glfw numpy pillow
```

---

## Running the Project

To run the final integrated version:

```bash
python main.py
```

To run individual development steps:

```bash
python step1_display_object.py
# ...
python step7_advanced_coloring.py
```

---

## Acknowledgements

- USS Enterprise model (grayscale `.obj`)
- Libraries: PyOpenGL, GLFW, NumPy, Pillow

---

## Author

**Ermmyna Roselee**  
Bachelor of Computer Science  
University of Queensland – Semester 1, 2025
