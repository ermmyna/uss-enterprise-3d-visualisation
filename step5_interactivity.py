#!/usr/bin/env python3
"""
step5_interactivity.py - USS Enterprise 3D Viewer with Enhanced Real-Time Interactivity
Step 5 of Computer Graphics Major Project

Features:
- All features from Step 4 (perspective camera, Phong lighting, shadow projection)
- Enhanced real-time interactivity with comprehensive controls
- Toggle lighting on/off to compare lit vs unlit rendering
- Toggle shadows and ground plane visibility
- Real-time light source movement with visual feedback
- Reset functionality for camera and lighting
- Optional wireframe/solid rendering toggle
- Optional animation pause/resume
- Enhanced help system and status feedback
- Smooth user experience with action messages

Controls:
- Camera: W/A/S/D/Q/E for movement, C to reset everything
- Lighting: L to toggle, P to animate, I/K/J/;/U/O to move light
- Display: F for wireframe, R for shadows, T for ground plane
- Animation: SPACE to pause/resume, P for light orbit
- Material: ,/. to adjust shininess
- System: H for help, Z to restart, ESC to quit
"""

import sys
import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Import shared utilities (includes all shadow and lighting functions)
from graphics_utils import *

# === STEP 5 ENHANCED VARIABLES ===

# Status display system (console-based feedback only)
show_status_overlay = False  # Disabled to prevent black rectangle
last_action_message = ""
last_action_time = 0.0
message_display_duration = 2.0

# Enhanced interactivity flags
display_help_on_start = True
verbose_feedback = True

# Global model instance
model = None

# === ENHANCED RENDERING FUNCTIONS ===

def draw_model_with_enhanced_lighting():
    """Draw the 3D model with enhanced lighting and all rotation modes."""
    if not model or not model.is_loaded():
        return
    
    # Set material properties
    set_material_properties()
    
    # Apply all rotations (manual + automatic)
    glPushMatrix()
    
    # Apply mouse rotations
    glRotatef(rotation_x, 1.0, 0.0, 0.0)
    glRotatef(rotation_y, 0.0, 1.0, 0.0)
    
    # Apply automatic rotation if enabled and not paused
    if auto_rotation_enabled and not animation_paused:
        glRotatef(current_auto_rotation, 0.0, 1.0, 0.0)
    
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
        
        # Set color based on lighting state
        if lighting_enabled:
            glColor3f(0.7, 0.8, 0.9)  # Light blue-gray base color for lighting
        else:
            # Use face normal for simple shading when lighting is off
            if i < len(model.normals):
                normal = model.normals[i]
                # Simple dot product shading with fixed light direction
                light_dir = np.array([0.5, 0.7, 0.5])
                brightness = max(0.3, np.dot(normal, light_dir))
                glColor3f(0.7 * brightness, 0.8 * brightness, 0.9 * brightness)
            else:
                glColor3f(0.7, 0.8, 0.9)
        
        for vertex_idx in face:
            if vertex_idx < len(model.vertices):
                vertex = model.vertices[vertex_idx]
                try:
                    glVertex3f(vertex[0], vertex[1], vertex[2])
                except (IndexError, TypeError):
                    continue
        
        glEnd()
        
        # Draw wireframe lines if lighting is off or wireframe mode is on
        if not lighting_enabled or wireframe_mode:
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

def draw_status_overlay():
    """Status feedback through console messages only (no visual overlay)."""
    # We'll use console feedback instead of a visual overlay
    # This prevents the black rectangle issue while maintaining user feedback
    pass

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
    
    # Initialize enhanced lighting system
    init_lighting_system()
    
    # Load the USS Enterprise model
    model = Model3D("USS_enterprise_grayscale.obj")
    if not model.is_loaded():
        print("Failed to load model. Exiting...")
        return False
    
    print(f"📷 Initial camera position: ({eyeX:.1f}, {eyeY:.1f}, {eyeZ:.1f})")
    print(f"🌫️  Enhanced shadow system initialized")
    return True

def render():
    """Main rendering function with enhanced lighting, shadows, and status display."""
    # Calculate delta time and update systems
    calculate_delta_time()
    update_camera_position()
    update_lighting_system()
    update_all_animations()
    
    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Set up camera
    setup_camera()
    
    # === RENDERING ORDER IS IMPORTANT FOR SHADOWS ===
    
    # 1. Draw ground plane first
    draw_ground_plane(ground_plane_y, ground_size, ground_color, 
                     ground_plane_visible, lighting_enabled)
    
    # 2. Draw shadows on the ground (pass both manual and auto rotation)
    total_rotation_y = rotation_y + (current_auto_rotation if auto_rotation_enabled and not animation_paused else 0.0)
    draw_model_shadow(model, light_position, ground_plane_y, shadow_color, 
                     rotation_x, total_rotation_y, shadows_enabled)
    
    # 3. Draw the main model with enhanced lighting
    draw_model_with_enhanced_lighting()
    
    # 4. Draw light position indicator
    draw_light_indicator()
    
    # 5. Draw status overlay
    draw_status_overlay()
    
    # Update display
    pygame.display.flip()

def handle_events():
    """Handle pygame events with enhanced interactivity controls."""
    global rotation_x, rotation_y, mouse_last_x, mouse_last_y, mouse_dragging
    global keys_pressed, turbo_active
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        elif event.type == pygame.KEYDOWN:
            keys_pressed.add(event.key)
            
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_z:
                print("🔄 Manual restart - restarting program...")
                restart_program()
            elif event.key == pygame.K_h:
                print_comprehensive_help()
            
            # === ENHANCED LIGHTING CONTROLS ===
            elif event.key == pygame.K_l:
                toggle_lighting()
            elif event.key == pygame.K_p:
                toggle_light_animation()
            elif event.key == pygame.K_i:
                move_light('forward')
            elif event.key == pygame.K_k:
                move_light('back')
            elif event.key == pygame.K_j:
                move_light('left')
            elif event.key == pygame.K_SEMICOLON:
                move_light('right')
            elif event.key == pygame.K_u:
                move_light('up')
            elif event.key == pygame.K_o:
                move_light('down')
            elif event.key == pygame.K_COMMA:
                adjust_material_shininess(-8.0)
            elif event.key == pygame.K_PERIOD:
                adjust_material_shininess(8.0)
            
            # === ENHANCED DISPLAY CONTROLS ===
            elif event.key == pygame.K_f:
                toggle_wireframe()
            elif event.key == pygame.K_r:
                toggle_shadows()
            elif event.key == pygame.K_t:
                toggle_ground_plane()
            
            # === ENHANCED ANIMATION CONTROLS ===
            elif event.key == pygame.K_SPACE:
                toggle_animation()
            
            # === ENHANCED CAMERA CONTROLS ===
            elif event.key == pygame.K_c:
                reset_all_settings()
            
            # === TURBO MODE ===
            elif event.key == pygame.K_TAB:
                turbo_active = True
                message = f"🚀 TURBO MODE: ON (speed x{turbo_multiplier:.1f})"
                print(message)
                set_status_message(message)
        
        elif event.type == pygame.KEYUP:
            keys_pressed.discard(event.key)
            
            if event.key == pygame.K_TAB:
                turbo_active = False
                message = "🚀 TURBO MODE: OFF"
                print(message)
                set_status_message(message)
        
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

def print_startup_instructions():
    """Print comprehensive startup instructions."""
    print("\n" + "="*80)
    print("🎮 USS Enterprise 3D Viewer - Step 5: Enhanced Real-Time Interactivity")
    print("="*80)
    print("✨ Experience the USS Enterprise with full interactive control!")
    print("🎯 This step demonstrates advanced real-time user interaction patterns.")
    
    print("\n🌟 KEY FEATURES:")
    print("  • Toggle lighting on/off to compare rendering modes")
    print("  • Real-time light source movement with visual feedback")
    print("  • Toggle shadows and ground plane visibility")
    print("  • Wireframe/solid rendering toggle")
    print("  • Animation pause/resume for model and light")
    print("  • Complete reset functionality")
    print("  • Enhanced status feedback system")
    
    print("\n🚀 QUICK START DEMO:")
    print("  1. Press 'L' to turn lighting off/on - see the difference!")
    print("  2. Press 'P' to make the light orbit around the model")
    print("  3. Use I/K/J/;/U/O to move the light and watch shadows change")
    print("  4. Press 'F' to toggle wireframe mode")
    print("  5. Press 'SPACE' to pause/resume model rotation")
    print("  6. Press 'R' to toggle shadows on/off")
    print("  7. Press 'C' to reset everything if you get lost")
    
    print("\n⚡ ENHANCED CONTROLS:")
    print("  L       - Toggle lighting ON/OFF (compare lit vs unlit!)")
    print("  P       - Toggle light orbit animation")
    print("  I/K/J/; - Move light forward/back/left/right")
    print("  U/O     - Move light up/down")
    print("  F       - Toggle wireframe/solid rendering")
    print("  R       - Toggle shadows ON/OFF")
    print("  T       - Toggle ground plane visibility")
    print("  SPACE   - Pause/resume model rotation")
    print("  C       - RESET everything to defaults")
    print("  TAB     - TURBO mode (hold for 5x speed)")
    print("  H       - Show detailed help")
    
    print("\n💡 INTERACTION TIPS:")
    print("  • Toggle lighting (L) to understand how Phong lighting works")
    print("  • Move the light source and observe how shadows change direction")
    print("  • Try wireframe mode (F) to see the model's geometric structure")
    print("  • Pause animation (SPACE) to focus on lighting effects")
    print("  • Use orbit controls (A/D) to view shadows from different angles")
    
    print("\n📊 STATUS FEEDBACK:")
    print("  • All actions provide immediate console feedback")
    print("  • Light position updates shown in real-time")
    print("  • Current settings displayed when you press 'H'")
    
    print("\n🎯 EDUCATIONAL GOALS:")
    print("  • Understand the difference between lit and unlit rendering")
    print("  • Observe how light position affects shadow direction and length")
    print("  • Experience real-time parameter adjustment in 3D graphics")
    print("  • Learn about different rendering modes (solid vs wireframe)")
    
    print("\n📦 TECHNICAL IMPLEMENTATION:")
    print("  • Enhanced event handling with comprehensive key mapping")
    print("  • Real-time state management for all toggleable features")
    print("  • Smooth integration of lighting, shadows, and animation systems")
    print("  • Modular design using graphics_utils.py for reusable components")
    
    print("\n🔥 TRY THIS SEQUENCE:")
    print("  1. Press 'P' to start light animation")
    print("  2. Press 'L' to turn off lighting - see the difference!")
    print("  3. Press 'L' again to turn it back on")
    print("  4. Press 'F' to see wireframe mode")
    print("  5. Press 'SPACE' to pause model rotation")
    print("  6. Use I/K to move light up/down and watch shadow length change")
    print("  7. Press 'C' to reset and start over!")
    
    print("\n" + "="*80)
    print("🎮 Ready for interactive exploration! Press 'H' anytime for detailed help.")
    print("="*80 + "\n")

def main():
    """Main function with enhanced real-time interactivity system."""
    try:
        # Initialize pygame
        pygame.init()
        
        # Set up resizable display
        screen = pygame.display.set_mode((window_width, window_height), 
                                       DOUBLEBUF | OPENGL | RESIZABLE)
        pygame.display.set_caption("USS Enterprise - Step 5: Enhanced Real-Time Interactivity")
        
        # Initialize OpenGL and load model
        if not init_opengl():
            print("Failed to initialize. Exiting...")
            return
        
        # Print startup instructions
        print_startup_instructions()
        
        # Main loop
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Check for file changes (hot reload)
            global check_reload_timer
            check_reload_timer += 1
            if check_reload_timer >= 30:
                check_reload_timer = 0
                if check_for_file_changes():
                    restart_program()
            
            # Handle events with enhanced interactivity
            running = handle_events()
            
            # Render the scene with all enhancements
            render()
            
            # Target 60 FPS
            clock.tick(60)
        
        print("Exiting cleanly...")
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    main()