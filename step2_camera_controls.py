#!/usr/bin/env python3
"""
Ultra-Smooth 3D Model Viewer with Enhanced Camera System
CLEANED VERSION - Properly uses graphics_utils.py without duplication
"""

import sys
import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Import all necessary functions and variables from graphics_utils
from graphics_utils import (
    # Camera functions
    calculate_delta_time, init_perspective_camera, setup_camera, 
    update_camera_position, handle_window_resize, update_orbital_camera,
    
    # Model functions  
    load_obj, calculate_face_normals, center_and_scale_model,
    
    # Utility functions
    check_for_file_changes, restart_program,
    
    # Global variables we need to access/modify
    window_width, window_height, keys_pressed, delta_time
)

# Import graphics_utils module to access variables that change at runtime
import graphics_utils as gu

# Only keep variables specific to this main script (not in graphics_utils)
model = None
rotation_x = 0.0  # Model rotation from mouse drag
rotation_y = 0.0  # Model rotation from mouse drag
mouse_last_x = 0
mouse_last_y = 0
mouse_dragging = False
check_reload_timer = 0

def init_opengl():
    """Initialize OpenGL settings and load the 3D model."""
    global model
    
    # Set the background color to dark blue/black
    glClearColor(0.0, 0.1, 0.2, 1.0)
    
    # Enable depth testing
    glEnable(GL_DEPTH_TEST)
    
    # Enable smooth shading
    glShadeModel(GL_SMOOTH)
    
    # Set up the viewport
    glViewport(0, 0, window_width, window_height)
    
    # Initialize perspective camera (from graphics_utils)
    init_perspective_camera()
    
    # Try multiple possible filenames for the USS Enterprise model
    possible_names = [
        "USS_enterprise_grayscale.obj",
        "USS Enterprise gray scale.obj", 
        "USS_Enterprise_gray_scale.obj",
        "uss_enterprise.obj"
    ]
    
    print("Loading USS Enterprise model...")
    vertices, faces = None, None
    
    for filename in possible_names:
        print(f"Trying: {filename}")
        vertices, faces = load_obj(filename)  # From graphics_utils
        if vertices is not None and faces is not None:
            print(f"Successfully loaded: {filename}")
            break
    
    if vertices is None or faces is None:
        print("Failed to load model. Available .obj files:")
        for file in os.listdir('.'):
            if file.endswith('.obj'):
                print(f"  - {file}")
        print("Please ensure the USS Enterprise OBJ file is in the same directory.")
        return False
    
    # Center and scale the model (from graphics_utils)
    vertices = center_and_scale_model(vertices)
    
    # Calculate face normals (from graphics_utils)
    face_normals = calculate_face_normals(vertices, faces)
    
    # Store model data
    model = {
        'vertices': vertices,
        'faces': faces,
        'normals': face_normals
    }
    
    print(f"Model loaded successfully!")
    print(f"Vertices: {len(vertices)}")
    print(f"Faces: {len(faces)}")
    print(f"📷 Initial camera position: ({gu.eyeX:.1f}, {gu.eyeY:.1f}, {gu.eyeZ:.1f})")
    return True

def draw_model():
    """Draw the 3D model using OpenGL."""
    if not model:
        return
    
    vertices = model['vertices']
    faces = model['faces']
    normals = model['normals']
    
    # Apply mouse rotations for model interaction
    glPushMatrix()  # Save current matrix
    glRotatef(rotation_x, 1.0, 0.0, 0.0)  # Rotate around X-axis
    glRotatef(rotation_y, 0.0, 1.0, 0.0)  # Rotate around Y-axis
    
    # Draw each face of the model
    for i, face in enumerate(faces):
        # Set the normal for this face
        if i < len(normals) and len(normals[i]) >= 3:
            try:
                glNormal3f(normals[i][0], normals[i][1], normals[i][2])
            except (IndexError, TypeError):
                glNormal3f(0.0, 0.0, 1.0)
        
        # Draw solid face
        glBegin(GL_POLYGON)
        glColor3f(0.7, 0.8, 0.9)  # Light blue-gray color
        
        for vertex_idx in face:
            if vertex_idx < len(vertices):
                vertex = vertices[vertex_idx]
                try:
                    glVertex3f(vertex[0], vertex[1], vertex[2])
                except (IndexError, TypeError):
                    continue
        
        glEnd()
        
        # Draw wireframe
        glBegin(GL_LINE_LOOP)
        glColor3f(0.2, 0.3, 0.4)  # Dark lines
        for vertex_idx in face:
            if vertex_idx < len(vertices):
                vertex = vertices[vertex_idx]
                try:
                    glVertex3f(vertex[0], vertex[1], vertex[2])
                except (IndexError, TypeError):
                    continue
        glEnd()
    
    glPopMatrix()  # Restore matrix

def render():
    """Main rendering function."""
    # Calculate delta time and update camera (from graphics_utils)
    calculate_delta_time()
    update_camera_position()
    
    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Set up camera (from graphics_utils)
    setup_camera()
    
    # Draw the model
    draw_model()
    
    # Update display
    pygame.display.flip()

def handle_events():
    """Handle pygame events."""
    global rotation_x, rotation_y, mouse_last_x, mouse_last_y, mouse_dragging
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        elif event.type == pygame.KEYDOWN:
            # Add key to pressed set (from graphics_utils)
            keys_pressed.add(event.key)
            
            # Handle special keys
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_r:
                print("🔄 Manual refresh - restarting program...")
                restart_program()  # From graphics_utils
            elif event.key == pygame.K_h:
                print_help()
            elif event.key == pygame.K_c:
                # Reset camera position (accessing graphics_utils variables)
                gu.eyeX, gu.eyeY, gu.eyeZ = 0.0, 0.0, 8.0
                gu.centerX, gu.centerY, gu.centerZ = 0.0, 0.0, 0.0
                gu.camera_velocity = gu.np.array([0.0, 0.0, 0.0])
                gu.rotation_velocity = gu.np.array([0.0, 0.0])
                gu.camera_yaw, gu.camera_pitch = 0.0, 0.0
                gu.camera_distance = 8.0
                gu.zoom_velocity = 0.0
                print(f"📷 Camera reset to initial position")
            elif event.key == pygame.K_t:
                gu.turbo_active = True
                print(f"🚀 TURBO MODE ACTIVATED! Speed multiplier: {gu.turbo_multiplier:.1f}x")
            elif event.key == pygame.K_LEFTBRACKET:
                gu.camera_speed = max(0.5, gu.camera_speed - 5.0)
                print(f"📷 Camera speed: {gu.camera_speed:.1f} units/sec")
            elif event.key == pygame.K_RIGHTBRACKET:
                gu.camera_speed = min(100.0, gu.camera_speed + 5.0)
                print(f"📷 Camera speed: {gu.camera_speed:.1f} units/sec")
            elif event.key == pygame.K_MINUS:
                gu.movement_smoothing = max(0.0, gu.movement_smoothing - 0.05)
                print(f"🎛️ Movement smoothing: {gu.movement_smoothing:.2f} (lower = more responsive)")
            elif event.key == pygame.K_EQUALS:
                gu.movement_smoothing = min(0.99, gu.movement_smoothing + 0.05)
                print(f"🎛️ Movement smoothing: {gu.movement_smoothing:.2f}")
            elif event.key == pygame.K_1:
                gu.forward_speed_multiplier = max(0.1, gu.forward_speed_multiplier - 0.5)
                print(f"⬆️ Forward/back speed: {gu.forward_speed_multiplier:.1f}x")
            elif event.key == pygame.K_2:
                gu.forward_speed_multiplier = min(10.0, gu.forward_speed_multiplier + 0.5)
                print(f"⬆️ Forward/back speed: {gu.forward_speed_multiplier:.1f}x")
            elif event.key == pygame.K_3:
                gu.orbit_speed = max(10.0, gu.orbit_speed - 10.0)
                print(f"🔄 Orbital speed: {gu.orbit_speed:.1f} deg/sec")
            elif event.key == pygame.K_4:
                gu.orbit_speed = min(360.0, gu.orbit_speed + 10.0)
                print(f"🔄 Orbital speed: {gu.orbit_speed:.1f} deg/sec")
            elif event.key == pygame.K_5:
                gu.zoom_speed = max(0.1, gu.zoom_speed - 0.2)
                print(f"🔍 Zoom speed: {gu.zoom_speed:.1f} units/sec")
            elif event.key == pygame.K_6:
                gu.zoom_speed = min(10.0, gu.zoom_speed + 0.2)
                print(f"🔍 Zoom speed: {gu.zoom_speed:.1f} units/sec")
            elif event.key == pygame.K_7:
                gu.pitch_speed = max(5.0, gu.pitch_speed - 5.0)
                print(f"⬆️ Pitch speed: {gu.pitch_speed:.1f} deg/sec")
            elif event.key == pygame.K_8:
                gu.pitch_speed = min(180.0, gu.pitch_speed + 5.0)
                print(f"⬆️ Pitch speed: {gu.pitch_speed:.1f} deg/sec")
            elif event.key == pygame.K_9:
                gu.smoothing_boost_on_input = not gu.smoothing_boost_on_input
                status = "ENABLED" if gu.smoothing_boost_on_input else "DISABLED"
                print(f"🎛️ Dynamic smoothing: {status}")
            elif event.key == pygame.K_0:
                if gu.max_distance_from_origin <= 20.0:
                    gu.max_distance_from_origin = 50.0
                elif gu.max_distance_from_origin <= 50.0:
                    gu.max_distance_from_origin = 100.0
                else:
                    gu.max_distance_from_origin = 20.0
                print(f"📏 Max camera distance: {gu.max_distance_from_origin:.0f} units")
        
        elif event.type == pygame.KEYUP:
            # Remove key from pressed set
            keys_pressed.discard(event.key)
            
            # Handle turbo mode deactivation
            if event.key == pygame.K_t:
                gu.turbo_active = False
                print(f"🚀 Turbo mode deactivated")
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
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
                
                # Enhanced rotation with adjustable speed
                rotation_y += dx * 0.5 * gu.rotation_speed
                rotation_x += dy * 0.5 * gu.rotation_speed
                
                mouse_last_x, mouse_last_y = x, y
        
        elif event.type == pygame.VIDEORESIZE:
            # Handle window resize (from graphics_utils)
            handle_window_resize(event.w, event.h)
    
    return True

def print_help():
    """Print help information."""
    current_effective_speed = gu.camera_speed * (gu.turbo_multiplier if gu.turbo_active else 1.0)
    print("\n=== 📷 Perfect Orbital Camera Controls ===")
    print("CAMERA MOVEMENT:")
    print("  W/S - Smooth zoom in/out (velocity-based!)")
    print("  A/D - Orbit left/right around model (smooth rotation!)") 
    print("  Q/E - Look up/down (pitch camera to see top/bottom!)")
    print("  C   - Reset camera position")
    print("  T   - TURBO MODE (hold for speed boost!)")
    print("\nSPEED & SMOOTHING:")
    print("  [ ] - Decrease/increase base speed (±5 units)")
    print("  - + - Decrease/increase movement smoothing")
    print("  1/2 - Decrease/increase forward/back multiplier (±0.5x)")
    print("  3/4 - Decrease/increase orbital rotation speed (±10 deg/sec)")
    print("  5/6 - Decrease/increase zoom speed (±0.2 units/sec)")
    print("  7/8 - Decrease/increase pitch speed (±5 deg/sec)")
    print("  9   - Toggle dynamic smoothing boost")
    print("  0   - Cycle max camera distance (20/50/100)")
    print(f"\nCURRENT SETTINGS:")
    print(f"  Base speed: {gu.camera_speed:.1f} units/sec")
    print(f"  Effective speed: {current_effective_speed:.1f} units/sec {'🚀 TURBO!' if gu.turbo_active else ''}")
    print(f"  Forward/back multiplier: {gu.forward_speed_multiplier:.1f}x")
    print(f"  Orbital speed: {gu.orbit_speed:.1f} deg/sec × {gu.strafe_speed_multiplier:.1f}")
    print(f"  Zoom speed: {gu.zoom_speed:.1f} units/sec")
    print(f"  Pitch speed: {gu.pitch_speed:.1f} deg/sec")
    print(f"  Mouse rotation: {gu.rotation_speed:.1f}x")
    print(f"  Smoothing: {gu.movement_smoothing:.2f} (current: {gu.current_smoothing:.2f})")
    print(f"  Dynamic smoothing: {'ENABLED' if gu.smoothing_boost_on_input else 'DISABLED'}")
    print(f"\nORBITAL POSITION:")
    print(f"  Distance: {gu.camera_distance:.1f} units (range: {gu.min_zoom_distance:.1f}-{gu.max_zoom_distance:.1f})")
    print(f"  Yaw: {gu.camera_yaw:.1f}° | Pitch: {gu.camera_pitch:.1f}°")
    print(f"  Camera: ({gu.eyeX:.1f}, {gu.eyeY:.1f}, {gu.eyeZ:.1f})")
    print(f"  Zoom velocity: {gu.zoom_velocity:.2f} u/s")
    print("\nMODEL INTERACTION:")
    print("  Mouse drag - Rotate model")
    print("\nOTHER CONTROLS:")
    print("  H - Show this help")
    print("  R - Manual restart")
    print("  Escape - Quit")
    print("==========================================\n")

def main():
    """Main function with enhanced frame timing."""
    try:
        # Initialize pygame
        pygame.init()
        
        # Set up resizable display
        screen = pygame.display.set_mode((window_width, window_height), 
                                       DOUBLEBUF | OPENGL | RESIZABLE)
        pygame.display.set_caption("USS Enterprise - Step 2: Camera Controls")
        
        # Initialize OpenGL and load model
        if not init_opengl():
            print("Failed to initialize. Exiting...")
            return
        
        # Print enhanced instructions
        print("\n🚀 === USS Enterprise 3D Viewer - Ultra-Smooth Edition ===")
        print("✨ ENHANCED: Velocity-based movement + delta time smoothing")
        print("🧹 CLEANED: Now using modular graphics_utils.py")
        print("\n📷 CAMERA CONTROLS:")
        print("  W/A/S/D - Move forward/left/backward/right")
        print("  Q/E     - Move up/down")
        print("  C       - Reset camera position")
        print("  T       - TURBO MODE (hold for speed boost!)")
        print("  [ ]     - Decrease/increase base speed (±5)")
        print("  - +     - Adjust movement smoothing")
        print("  1-8     - Fine-tune speed multipliers")
        print("  9       - Toggle dynamic smoothing")
        print("  0       - Cycle max distance limit")
        print("  Mouse   - Rotate model")
        print(f"\n⚡ ULTRA-SMOOTH ORBITAL CAMERA:")
        print(f"   A/D: Smooth orbital rotation")
        print(f"   W/S: Smooth zoom")
        print(f"   Q/E: Pitch camera up/down")
        print("   Hold 'T' for turbo mode! Press 'H' for full help.\n")
        
        # Main loop with enhanced timing
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Check for file changes (from graphics_utils)
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