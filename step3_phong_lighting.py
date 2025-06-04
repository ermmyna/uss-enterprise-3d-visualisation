#!/usr/bin/env python3
"""
object3.py - USS Enterprise 3D Viewer with Phong Lighting Model
Step 3 of Computer Graphics Major Project

Features:
- Perspective camera with orbital controls (from object2.py)
- Phong lighting model with ambient, diffuse, and specular components
- Interactive lighting controls
- Material properties for realistic metal appearance
- Light position indicator

Controls:
- Camera: W/A/S/D/Q/E for movement, C to reset
- Lighting: L to toggle, P to animate, I/K/J/;/U/O to move light
- Material: ,/. to adjust shininess
"""

import sys
import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Import shared utilities
from graphics_utils import *

# === LIGHTING-SPECIFIC VARIABLES ===

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
light_rotation_speed = 60.0  # degrees per second (was 30.0 - now faster!)
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
    
    # Set background color
    glClearColor(0.0, 0.1, 0.2, 1.0)
    
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
    return True

def render():
    """Main rendering function with lighting."""
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
    
    # Draw the model with lighting
    draw_model_with_lighting()
    
    # Draw light position indicator
    draw_light_indicator()
    
    # Update display
    pygame.display.flip()

def handle_events():
    """Handle pygame events including lighting controls."""
    global rotation_x, rotation_y, mouse_last_x, mouse_last_y, mouse_dragging
    global keys_pressed, turbo_active
    global light_position, animate_light, material_shininess
    global camera_yaw, camera_pitch, camera_distance, zoom_velocity
    
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
            
            # === LIGHTING CONTROLS ===
            elif event.key == pygame.K_l:
                toggle_lighting()
            elif event.key == pygame.K_p:
                global animate_light  # Make sure we can modify the global variable
                animate_light = not animate_light
                status = "ENABLED" if animate_light else "DISABLED"
                print(f"🔆 Light animation: {status}")
                print(f"🔆 Current light position: ({light_position[0]:.1f}, {light_position[1]:.1f}, {light_position[2]:.1f})")
                # Import delta_time to check its current value
                from graphics_utils import delta_time
                print(f"🔆 Delta time: {delta_time:.4f}s")
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
    """Print help information including lighting controls."""
    current_effective_speed = camera_speed * (turbo_multiplier if turbo_active else 1.0)
    print("\n=== 🔆 USS Enterprise 3D Viewer with Phong Lighting ===")
    print("CAMERA MOVEMENT:")
    print("  W/S - Smooth zoom in/out")
    print("  A/D - Orbit left/right around model") 
    print("  Q/E - Look up/down (pitch camera)")
    print("  C   - Reset camera position")
    print("  T   - TURBO MODE (hold for 5x speed!)")
    print("\nLIGHTING CONTROLS:")
    print("  L   - Toggle lighting on/off")
    print("  P   - Toggle light animation (orbiting)")
    print("  I/K - Move light up/down")
    print("  J/; - Move light left/right")
    print("  U/O - Move light forward/backward") 
    print("  ,/. - Decrease/increase material shininess")
    print("\nSPEED & SMOOTHING:")
    print("  [ ] - Decrease/increase base speed")
    print("  - + - Decrease/increase movement smoothing")
    print("  1-8 - Fine-tune speed multipliers")
    print(f"\nCURRENT LIGHTING:")
    print(f"  Lighting: {'ENABLED' if lighting_enabled else 'DISABLED'}")
    print(f"  Animation: {'ENABLED' if animate_light else 'DISABLED'}")
    print(f"  Light position: ({light_position[0]:.1f}, {light_position[1]:.1f}, {light_position[2]:.1f})")
    print(f"  Material shininess: {material_shininess:.0f}")
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
    print("==========================================\n")

def main():
    """Main function with lighting system."""
    try:
        # Initialize pygame
        pygame.init()
        
        # Set up resizable display
        screen = pygame.display.set_mode((window_width, window_height), 
                                       DOUBLEBUF | OPENGL | RESIZABLE)
        pygame.display.set_caption("USS Enterprise - Step 3: Phong Lighting")
        
        # Initialize OpenGL and load model
        if not init_opengl():
            print("Failed to initialize. Exiting...")
            return
        
        # Print instructions
        print("\n🔆 === USS Enterprise 3D Viewer - Step 3: Phong Lighting ===")
        print("✨ NEW: Realistic Phong lighting with ambient, diffuse, and specular components!")
        print("\n🔆 LIGHTING CONTROLS:")
        print("  L   - Toggle lighting on/off (see the difference!)")
        print("  P   - Animate light (light orbits around USS Enterprise)")
        print("  I/K - Move light up/down")
        print("  J/; - Move light left/right") 
        print("  U/O - Move light forward/backward")
        print("  ,/. - Adjust material shininess (specular highlight size)")
        print("\n📷 CAMERA CONTROLS (from Step 2):")
        print("  W/S - Zoom in/out")
        print("  A/D - Orbit around model")
        print("  Q/E - Look up/down")
        print("  C   - Reset camera")
        print("  T   - Turbo mode")
        print("  Mouse - Rotate model")
        print("\n🔍 TRY THIS:")
        print("  1. Press 'L' to toggle lighting and see the difference")
        print("  2. Press 'P' to animate the light source")
        print("  3. Use I/K/J/;/U/O to move the light around")
        print("  4. Adjust shininess with ,/. keys")
        print("  5. Press 'H' for full help")
        print("\nThe yellow dot shows the light position!\n")
        
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