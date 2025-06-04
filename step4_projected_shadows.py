#!/usr/bin/env python3
"""
object4.py - USS Enterprise 3D Viewer with Shadow Projection (Refactored)
Step 4 of Computer Graphics Major Project

Features:
- Perspective camera with orbital controls (from object2.py)
- Phong lighting model with ambient, diffuse, and specular components (from object3.py)
- Shadow projection using shadow matrices (now using graphics_utils.py functions)
- Ground plane to receive shadows
- Interactive lighting and shadow controls

Controls:
- Camera: W/A/S/D/Q/E for movement, C to reset
- Lighting: L to toggle, P to animate, I/K/J/;/U/O to move light
- Material: ,/. to adjust shininess
- Shadows: V to toggle shadows, B to toggle ground plane
"""

import sys
import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Import shared utilities (now includes shadow functions!)
from graphics_utils import *

# === SHADOW-SPECIFIC VARIABLES ===

# Shadow control
shadows_enabled = True
ground_plane_visible = True
ground_plane_y = -3.0  # Y-level where ground plane sits

# Shadow appearance
shadow_color = [0.1, 0.1, 0.1, 0.8]  # Dark gray with some transparency
ground_color = [0.3, 0.4, 0.3, 1.0]  # Dark green ground
ground_size = 30.0  # Size of the ground plane (larger to catch shadows)

# === LIGHTING VARIABLES ===

# Lighting control
lighting_enabled = True
light_position = [5.0, 5.0, 5.0, 1.0]  # [x, y, z, w] (w=1.0 for positional light)

# Light component intensities (RGBA)
ambient_light = [0.2, 0.2, 0.3, 1.0]   # Soft blue ambient
diffuse_light = [0.8, 0.9, 1.0, 1.0]   # Bright white diffuse
specular_light = [1.0, 1.0, 1.0, 1.0]  # Pure white specular

# Material properties for USS Enterprise (metallic spacecraft)
material_ambient = [0.3, 0.3, 0.4, 1.0]    # Ambient reflection (blue-gray)
material_diffuse = [0.6, 0.7, 0.8, 1.0]    # Diffuse reflection (light blue-gray)
material_specular = [0.9, 0.9, 0.9, 1.0]   # Specular reflection (bright white)
material_shininess = 32.0                   # Shininess factor (1-128)

# Light animation
animate_light = False
light_rotation_speed = 60.0  # degrees per second
light_rotation_angle = 0.0
light_orbit_radius = 8.0

# Global model instance
model = None

# === LIGHTING FUNCTIONS ===

def init_lighting():
    """Initialize OpenGL lighting with Phong model components."""
    print("🔆 Initializing Phong lighting model...")
    
    # Enable lighting globally
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # Set up light components for GL_LIGHT0
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    
    # Set global ambient light
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.1, 0.1, 0.15, 1.0])
    
    # Enable automatic normal normalization
    glEnable(GL_NORMALIZE)
    
    # Enable color material
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    print(f"   ✅ Light source enabled at position: ({light_position[0]:.1f}, {light_position[1]:.1f}, {light_position[2]:.1f})")
    print(f"   ✅ Material properties set (shininess: {material_shininess:.0f})")

def update_lighting():
    """Update lighting every frame. Handles light animation and position updates."""
    global light_rotation_angle, light_position
    from graphics_utils import delta_time  # Import delta_time from graphics_utils
    
    # Update light animation if enabled
    if animate_light and delta_time > 0:
        print(f"🔆 UPDATING: old_angle={light_rotation_angle:.1f}°, delta_time={delta_time:.4f}s")  # Debug line
        light_rotation_angle += light_rotation_speed * delta_time
        light_rotation_angle = light_rotation_angle % 360.0
        print(f"🔆 UPDATING: new_angle={light_rotation_angle:.1f}°")  # Debug line
        
        # Calculate new light position in orbit around model
        angle_rad = np.radians(light_rotation_angle)
        old_pos = [light_position[0], light_position[1], light_position[2]]
        light_position[0] = light_orbit_radius * np.cos(angle_rad)
        light_position[1] = 5.0  # Keep light elevated
        light_position[2] = light_orbit_radius * np.sin(angle_rad)
        
        print(f"🔆 POSITION: old=({old_pos[0]:.1f}, {old_pos[1]:.1f}, {old_pos[2]:.1f}) -> new=({light_position[0]:.1f}, {light_position[1]:.1f}, {light_position[2]:.1f})")
    
    # Update light position in OpenGL (IMPORTANT: This must happen every frame!)
    if lighting_enabled:
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)

def set_material_properties():
    """Set material properties for the USS Enterprise."""
    if lighting_enabled:
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, material_ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, material_specular)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, material_shininess)

def toggle_lighting():
    """Toggle lighting on/off."""
    global lighting_enabled
    lighting_enabled = not lighting_enabled
    
    if lighting_enabled:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        print("🔆 Lighting ENABLED")
    else:
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        print("🔆 Lighting DISABLED")

def draw_light_indicator():
    """Draw a small sphere to show where the light source is positioned."""
    if not lighting_enabled:
        return
    
    # Temporarily disable lighting for the light indicator
    glDisable(GL_LIGHTING)
    
    # Draw a small yellow sphere at the light position
    glPushMatrix()
    glTranslatef(light_position[0], light_position[1], light_position[2])
    glColor3f(1.0, 1.0, 0.0)  # Bright yellow
    
    # Draw a larger point as fallback
    glPointSize(10.0)
    glBegin(GL_POINTS)
    glVertex3f(0.0, 0.0, 0.0)
    glEnd()
    glPointSize(1.0)
    
    glPopMatrix()
    
    # Re-enable lighting
    if lighting_enabled:
        glEnable(GL_LIGHTING)

# === MODEL RENDERING WITH LIGHTING ===

def draw_model_with_lighting():
    """Draw the 3D model with Phong lighting."""
    if not model or not model.is_loaded():
        return
    
    # Set material properties
    set_material_properties()
    
    # Apply mouse rotations
    glPushMatrix()
    glRotatef(rotation_x, 1.0, 0.0, 0.0)
    glRotatef(rotation_y, 0.0, 1.0, 0.0)
    
    # Draw each face with proper normals for lighting
    for i, face in enumerate(model.faces):
        # Set the normal for this face (essential for lighting!)
        if i < len(model.normals) and len(model.normals[i]) >= 3:
            try:
                glNormal3f(model.normals[i][0], model.normals[i][1], model.normals[i][2])
            except (IndexError, TypeError):
                glNormal3f(0.0, 0.0, 1.0)
        
        # Draw solid face
        glBegin(GL_POLYGON)
        
        # Set base color (lighting will modify this)
        if lighting_enabled:
            glColor3f(0.7, 0.8, 0.9)  # Light blue-gray base color
        else:
            glColor3f(0.7, 0.8, 0.9)  # Same color when lighting is off
        
        for vertex_idx in face:
            if vertex_idx < len(model.vertices):
                vertex = model.vertices[vertex_idx]
                try:
                    glVertex3f(vertex[0], vertex[1], vertex[2])
                except (IndexError, TypeError):
                    continue
        
        glEnd()
        
        # Draw wireframe only if lighting is disabled (for clarity)
        if not lighting_enabled:
            glBegin(GL_LINE_LOOP)
            glColor3f(0.2, 0.3, 0.4)  # Dark lines
            for vertex_idx in face:
                if vertex_idx < len(model.vertices):
                    vertex = model.vertices[vertex_idx]
                    try:
                        glVertex3f(vertex[0], vertex[1], vertex[2])
                    except (IndexError, TypeError):
                        continue
            glEnd()
    
    glPopMatrix()

# === MAIN FUNCTIONS ===

def init_opengl():
    """Initialize OpenGL settings and load the 3D model."""
    global model
    
    # Set background color (darker for better shadow contrast)
    glClearColor(0.05, 0.1, 0.15, 1.0)
    
    # Enable depth testing and smooth shading
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    
    # Set up viewport
    glViewport(0, 0, window_width, window_height)
    
    # Initialize perspective camera
    init_perspective_camera()
    
    # Initialize lighting system
    init_lighting()
    
    # Load the USS Enterprise model
    model = Model3D("USS_enterprise_grayscale.obj")
    if not model.is_loaded():
        print("Failed to load model. Exiting...")
        return False
    
    print(f"📷 Initial camera position: ({eyeX:.1f}, {eyeY:.1f}, {eyeZ:.1f})")
    print(f"🌫️  Shadow system initialized (ground plane at Y: {ground_plane_y:.1f})")
    return True

def render():
    """Main rendering function with lighting and shadows (using graphics_utils functions)."""
    # Calculate delta time
    calculate_delta_time()
    
    # Update camera position
    update_camera_position()
    
    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Set up camera
    setup_camera()
    
    # Update lighting AFTER camera setup (important for proper light positioning)
    update_lighting()
    
    # === RENDERING ORDER IS IMPORTANT FOR SHADOWS ===
    
    # 1. Draw ground plane first (using graphics_utils function)
    draw_ground_plane(ground_plane_y, ground_size, ground_color, 
                     ground_plane_visible, lighting_enabled)
    
    # 2. Draw shadows on the ground (using graphics_utils function)
    draw_model_shadow(model, light_position, ground_plane_y, shadow_color, 
                     rotation_x, rotation_y, shadows_enabled)
    
    # 3. Draw the main model with lighting (on top of shadow)
    draw_model_with_lighting()
    
    # 4. Draw light position indicator (always on top)
    draw_light_indicator()
    
    # Update display
    pygame.display.flip()

def handle_events():
    """Handle pygame events including lighting and shadow controls."""
    global rotation_x, rotation_y, mouse_last_x, mouse_last_y, mouse_dragging
    global keys_pressed, turbo_active
    global light_position, animate_light, material_shininess
    global camera_yaw, camera_pitch, camera_distance, zoom_velocity
    global shadows_enabled, ground_plane_visible  # Shadow controls
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        elif event.type == pygame.KEYDOWN:
            keys_pressed.add(event.key)
            
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_r:
                print("🔄 Manual refresh - restarting program...")
                restart_program()
            elif event.key == pygame.K_h:
                print_help()
            
            # === SHADOW CONTROLS ===
            elif event.key == pygame.K_v:
                shadows_enabled = not shadows_enabled
                status = "ENABLED" if shadows_enabled else "DISABLED"
                print(f"🌫️  Shadows: {status}")
            elif event.key == pygame.K_b:
                ground_plane_visible = not ground_plane_visible
                status = "VISIBLE" if ground_plane_visible else "HIDDEN"
                print(f"🌍 Ground plane: {status}")
            
            # === LIGHTING CONTROLS ===
            elif event.key == pygame.K_l:
                toggle_lighting()
            elif event.key == pygame.K_p:
                animate_light = not animate_light
                status = "ENABLED" if animate_light else "DISABLED"
                print(f"🔆 Light animation: {status}")
                if animate_light:
                    print(f"🔆 Light will orbit around USS Enterprise at {light_rotation_speed}°/sec")
            elif event.key == pygame.K_i:
                light_position[1] += 1.0
                print(f"🔆 Light moved up to Y: {light_position[1]:.1f}")
            elif event.key == pygame.K_k:
                light_position[1] -= 1.0
                print(f"🔆 Light moved down to Y: {light_position[1]:.1f}")
            elif event.key == pygame.K_j:
                light_position[0] -= 1.0
                print(f"🔆 Light moved left to X: {light_position[0]:.1f}")
            elif event.key == pygame.K_SEMICOLON:
                light_position[0] += 1.0
                print(f"🔆 Light moved right to X: {light_position[0]:.1f}")
            elif event.key == pygame.K_u:
                light_position[2] -= 1.0
                print(f"🔆 Light moved forward to Z: {light_position[2]:.1f}")
            elif event.key == pygame.K_o:
                light_position[2] += 1.0
                print(f"🔆 Light moved backward to Z: {light_position[2]:.1f}")
            elif event.key == pygame.K_COMMA:
                material_shininess = max(1.0, material_shininess - 8.0)
                print(f"✨ Material shininess: {material_shininess:.0f} (less shiny)")
            elif event.key == pygame.K_PERIOD:
                material_shininess = min(128.0, material_shininess + 8.0)
                print(f"✨ Material shininess: {material_shininess:.0f} (more shiny)")
            
            # === CAMERA CONTROLS ===
            elif event.key == pygame.K_c:
                # Reset camera
                global eyeX, eyeY, eyeZ, centerX, centerY, centerZ
                global camera_velocity, rotation_velocity
                eyeX, eyeY, eyeZ = 0.0, 0.0, 8.0
                centerX, centerY, centerZ = 0.0, 0.0, 0.0
                camera_velocity = np.array([0.0, 0.0, 0.0])
                rotation_velocity = np.array([0.0, 0.0])
                camera_yaw, camera_pitch = 0.0, 0.0
                camera_distance = 8.0
                zoom_velocity = 0.0
                print(f"📷 Camera reset to initial position")
            elif event.key == pygame.K_t:
                turbo_active = True
                print(f"🚀 TURBO MODE ACTIVATED! Speed multiplier: {turbo_multiplier:.1f}x")
        
        elif event.type == pygame.KEYUP:
            keys_pressed.discard(event.key)
            
            if event.key == pygame.K_t:
                turbo_active = False
                print(f"🚀 Turbo mode deactivated")
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_dragging = True
                mouse_last_x, mouse_last_y = event.pos
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if mouse_dragging:
                x, y = event.pos
                dx = x - mouse_last_x
                dy = y - mouse_last_y
                
                rotation_y += dx * 0.5 * rotation_speed
                rotation_x += dy * 0.5 * rotation_speed
                
                mouse_last_x, mouse_last_y = x, y
        
        elif event.type == pygame.VIDEORESIZE:
            handle_window_resize(event.w, event.h)
    
    return True

def print_help():
    """Print help information including shadow controls."""
    current_effective_speed = camera_speed * (turbo_multiplier if turbo_active else 1.0)
    print("\n=== 🌫️  USS Enterprise 3D Viewer with Shadow Projection (Refactored) ===")
    print("CAMERA MOVEMENT:")
    print("  W/S - Smooth zoom in/out")
    print("  A/D - Orbit left/right around model") 
    print("  Q/E - Look up/down (pitch camera)")
    print("  C   - Reset camera position")
    print("  T   - TURBO MODE (hold for 5x speed!)")
    print("\nSHADOW CONTROLS:")
    print("  V   - Toggle shadows on/off")
    print("  B   - Toggle ground plane visibility")
    print("\nLIGHTING CONTROLS:")
    print("  L   - Toggle lighting on/off")
    print("  P   - Toggle light animation (orbiting)")
    print("  I/K - Move light up/down")
    print("  J/; - Move light left/right")
    print("  U/O - Move light forward/backward") 
    print("  ,/. - Decrease/increase material shininess")
    print(f"\nCURRENT STATUS:")
    print(f"  Lighting: {'ENABLED' if lighting_enabled else 'DISABLED'}")
    print(f"  Shadows: {'ENABLED' if shadows_enabled else 'DISABLED'}")
    print(f"  Ground plane: {'VISIBLE' if ground_plane_visible else 'HIDDEN'}")
    print(f"  Light animation: {'ENABLED' if animate_light else 'DISABLED'}")
    print(f"  Light position: ({light_position[0]:.1f}, {light_position[1]:.1f}, {light_position[2]:.1f})")
    print(f"  Material shininess: {material_shininess:.0f}")
    print(f"  Ground level: Y = {ground_plane_y:.1f}")
    print(f"\nCAMERA STATUS:")
    print(f"  Distance: {camera_distance:.1f} units")
    print(f"  Yaw: {camera_yaw:.1f}° | Pitch: {camera_pitch:.1f}°")
    print(f"  Speed: {current_effective_speed:.1f} units/sec {'🚀 TURBO!' if turbo_active else ''}")
    print("\nMODEL INTERACTION:")
    print("  Mouse drag - Rotate model")
    print("\nOTHER CONTROLS:")
    print("  H - Show this help")
    print("  R - Manual restart")
    print("  Escape - Quit")
    print("\n📦 REFACTORED: Now uses shadow functions from graphics_utils.py!")
    print("=====================================================\n")

def main():
    """Main function with lighting and shadow system (refactored)."""
    try:
        # Initialize pygame
        pygame.init()
        
        # Set up resizable display
        screen = pygame.display.set_mode((window_width, window_height), 
                                       DOUBLEBUF | OPENGL | RESIZABLE)
        pygame.display.set_caption("USS Enterprise - Step 4: Shadow Projection (Refactored)")
        
        # Initialize OpenGL and load model
        if not init_opengl():
            print("Failed to initialize. Exiting...")
            return
        
        # Print instructions
        print("\n🌫️  === USS Enterprise 3D Viewer - Step 4: Shadow Projection (Refactored) ===")
        print("✨ Features realistic shadow projection using shadow matrices!")
        print("📦 REFACTORED: Shadow functions now live in graphics_utils.py for reuse!")
        print("🌍 The USS Enterprise casts shadows onto a large ground plane.")
        print("\n🌫️  SHADOW CONTROLS:")
        print("  V   - Toggle shadows on/off")
        print("  B   - Toggle ground plane visibility")
        print("\n🔆 LIGHTING CONTROLS:")
        print("  L   - Toggle lighting on/off")
        print("  P   - Animate light (watch shadow move!)")
        print("  I/K - Move light up/down (changes shadow direction)")
        print("  J/; - Move light left/right") 
        print("  U/O - Move light forward/backward")
        print("  ,/. - Adjust material shininess")
        print("\n📷 CAMERA CONTROLS:")
        print("  W/S - Zoom in/out")
        print("  A/D - Orbit around model")
        print("  Q/E - Look up/down")
        print("  C   - Reset camera")
        print("  T   - Turbo mode")
        print("  Mouse - Rotate model")
        print("\n🔍 TRY THIS:")
        print("  1. Press 'P' to animate the light and watch shadows move")
        print("  2. Use I/K to move light up/down (shadow gets longer/shorter)")
        print("  3. Press 'V' to toggle shadows on/off")
        print("  4. Press 'B' to toggle the ground plane")
        print("  5. Orbit around with A/D to see shadows from different angles")
        print("  6. Press 'H' for full help")
        print("\n📦 Ready for Steps 5, 6, 7 - shadow functions are now modular!\n")
        
        # Main loop
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Check for file changes
            global check_reload_timer
            check_reload_timer += 1
            if check_reload_timer >= 30:
                check_reload_timer = 0
                if check_for_file_changes():
                    restart_program()
            
            # Handle events
            running = handle_events()
            
            # Render the scene
            render()
            
            # Target 60 FPS
            clock.tick(60)
        
        print("Exiting cleanly...")
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    main()