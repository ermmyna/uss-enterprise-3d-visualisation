#!/usr/bin/env python3
"""
step6_animation.py - USS Enterprise 3D Viewer with Advanced Animation System
Step 6 of Computer Graphics Major Project

Features:
- All features from Step 5 (perspective camera, Phong lighting, shadow projection, enhanced interactivity)
- Advanced multi-layered animation system with frame-rate independence
- Model animation: smooth rotation with customizable speed and axis
- Light animation: orbital motion, vertical bobbing, and custom paths
- Animation control: pause/resume, speed adjustment, and individual animation toggles
- Smooth interpolation and easing functions for professional-quality motion
- Animation state management for easy integration into future steps
- Hot-reload support for rapid development

New Animation Controls:
- P: Toggle model animation pause/resume
- L: Toggle light orbit animation (independent of model)
- Shift+L: Toggle light vertical bobbing animation
- +/-: Increase/decrease animation speed (affects all animations)
- Shift++/Shift+-: Fine-tune animation speed
- Alt+P: Toggle light path animation (figure-8 pattern)
- R: Reset all animations to default state
- 1-5: Select different animation presets

Educational Value:
- Demonstrates frame-rate independent animation using delta time
- Shows how to create smooth, professional-looking motion in 3D
- Illustrates animation state management and modular design
- Perfect foundation for advanced animation techniques in future steps
"""

import sys
import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Import ALL animation utilities (significantly enhanced for Step 6)
from graphics_utils import *

# === STEP 6 ENHANCED VARIABLES ===

# Global model instance
model = None

# Enhanced animation feedback
show_animation_debug = True
animation_debug_timer = 0.0
debug_interval = 2.0

# === STEP 6 ENHANCED RENDERING FUNCTIONS ===

def draw_model_with_full_animation():
    """Draw the 3D model with full animation support and enhanced lighting."""
    if not model or not model.is_loaded():
        return
    
    # Set material properties for lighting
    set_material_properties()
    
    # Apply all transformations in correct order
    glPushMatrix()
    
    # 1. Apply user mouse rotations first (user has direct control)
    glRotatef(rotation_x, 1.0, 0.0, 0.0)
    glRotatef(rotation_y, 0.0, 1.0, 0.0)
    
    # 2. Apply model animations (layered on top of user control)
    apply_model_animation_transforms()
    
    # 3. Draw each face with proper normals for lighting
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
            # Use different colors for different animation states (visual feedback)
            if model_animation_paused:
                glColor3f(0.8, 0.6, 0.6)  # Slightly red tint when paused
            else:
                glColor3f(0.6, 0.8, 0.9)  # Cool blue-white when animating
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
        
        # Draw wireframe lines if wireframe mode is on
        if wireframe_mode:
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

def draw_enhanced_light_indicator():
    """Draw enhanced light position indicator with animation state feedback."""
    if not lighting_enabled:
        return
    
    # Temporarily disable lighting for indicator
    glDisable(GL_LIGHTING)
    
    # Draw light indicator with animation state colors
    glPushMatrix()
    glTranslatef(light_position[0], light_position[1], light_position[2])
    
    # Color based on animation state
    if light_orbit_enabled and light_bobbing_enabled:
        glColor3f(1.0, 0.5, 1.0)  # Magenta - both animations
    elif light_orbit_enabled:
        glColor3f(1.0, 1.0, 0.0)  # Yellow - orbit only
    elif light_bobbing_enabled:
        glColor3f(0.0, 1.0, 1.0)  # Cyan - bobbing only
    else:
        glColor3f(1.0, 0.8, 0.8)  # Light pink - static
    
    # Draw animated light indicator (size pulses with animation)
    animation_pulse = 1.0 + 0.3 * np.sin(get_total_animation_time() * 3.0)
    size = 12.0 * animation_pulse if (light_orbit_enabled or light_bobbing_enabled) else 10.0
    
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex3f(0.0, 0.0, 0.0)
    glEnd()
    
    # Draw animated light rays
    glLineWidth(2.0)
    glBegin(GL_LINES)
    
    # Rotating rays when light is animated
    if light_orbit_enabled or light_bobbing_enabled:
        ray_angle = get_total_animation_time() * 180.0  # Rotate rays
        ray_length = 0.8
        for i in range(6):
            angle = np.radians(ray_angle + i * 60.0)
            x = ray_length * np.cos(angle)
            z = ray_length * np.sin(angle)
            
            glColor3f(1.0, 0.8, 0.2)
            glVertex3f(0.0, 0.0, 0.0)
            glVertex3f(x, 0.0, z)
    else:
        # Static rays when not animated
        ray_length = 0.5
        glColor3f(1.0, 0.5, 0.5)
        glVertex3f(-ray_length, 0.0, 0.0)
        glVertex3f(ray_length, 0.0, 0.0)
        glColor3f(0.5, 1.0, 0.5)
        glVertex3f(0.0, -ray_length, 0.0)
        glVertex3f(0.0, ray_length, 0.0)
        glColor3f(0.5, 0.5, 1.0)
        glVertex3f(0.0, 0.0, -ray_length)
        glVertex3f(0.0, 0.0, ray_length)
    
    glEnd()
    glLineWidth(1.0)
    glPointSize(1.0)
    glPopMatrix()
    
    # Re-enable lighting
    if lighting_enabled:
        glEnable(GL_LIGHTING)

def draw_animation_status_overlay():
    """Display animation status through console output (no visual overlay to avoid issues)."""
    global animation_debug_timer
    
    if show_animation_debug:
        animation_debug_timer += delta_time
        
        if animation_debug_timer >= debug_interval:
            animation_debug_timer = 0.0
            
            # Print comprehensive animation status
            print(f"\n📊 ANIMATION STATUS (t={get_total_animation_time():.1f}s):")
            print(f"   Model: {'PAUSED' if model_animation_paused else 'PLAYING'} "
                  f"(angle: {model_rotation_angle:.1f}°, speed: {model_rotation_speed:.1f}°/s)")
            print(f"   Light Orbit: {'ON' if light_orbit_enabled else 'OFF'} "
                  f"(angle: {light_orbit_angle:.1f}°)")
            print(f"   Light Bobbing: {'ON' if light_bobbing_enabled else 'OFF'} "
                  f"(offset: {light_bobbing_offset:.2f})")
            print(f"   Global Speed: {animation_speed_multiplier:.2f}x")
            print(f"   Animation Preset: {current_animation_preset}")

# === MAIN FUNCTIONS ===

def init_opengl():
    """Initialize OpenGL settings and load the 3D model with animation support."""
    global model
    
    # Set background color (darker for better animation contrast)
    glClearColor(0.02, 0.05, 0.1, 1.0)
    
    # Enable depth testing and smooth shading
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    
    # Set up viewport
    glViewport(0, 0, window_width, window_height)
    
    # Initialize perspective camera
    init_perspective_camera()
    
    # Initialize enhanced lighting system
    init_lighting_system()
    
    # Initialize animation system (NEW for Step 6)
    init_animation_system()
    
    # Load the USS Enterprise model
    model = Model3D("USS_enterprise_grayscale.obj")
    if not model.is_loaded():
        print("Failed to load model. Exiting...")
        return False
    
    print(f"📷 Camera initialized at: ({eyeX:.1f}, {eyeY:.1f}, {eyeZ:.1f})")
    print(f"🎬 Animation system initialized with {len(get_available_presets())} presets")
    return True

def render():
    """Main rendering function with enhanced animation support."""
    # Update all systems
    calculate_delta_time()
    update_camera_position()
    update_lighting_system()
    
    # NEW: Update all animation systems
    update_all_animation_systems()
    
    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Set up camera
    setup_camera()
    
    # === RENDERING ORDER IS IMPORTANT FOR SHADOWS ===
    
    # 1. Draw ground plane first
    draw_ground_plane(ground_plane_y, ground_size, ground_color, 
                     ground_plane_visible, lighting_enabled)
    
    # 2. Draw shadows (now with animated rotations)
    total_rotation_y = rotation_y + get_total_model_rotation()
    draw_model_shadow(model, light_position, ground_plane_y, shadow_color, 
                     rotation_x, total_rotation_y, shadows_enabled)
    
    # 3. Draw the main model with full animation
    draw_model_with_full_animation()
    
    # 4. Draw enhanced animated light indicator
    draw_enhanced_light_indicator()
    
    # 5. Draw animation status
    draw_animation_status_overlay()
    
    # Update display
    pygame.display.flip()

def handle_events():
    """Handle pygame events with enhanced animation controls."""
    global rotation_x, rotation_y, mouse_last_x, mouse_last_y, mouse_dragging
    global keys_pressed, turbo_active
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        elif event.type == pygame.KEYDOWN:
            keys_pressed.add(event.key)
            
            # Check for modifier keys
            mods = pygame.key.get_pressed()
            shift_held = mods[pygame.K_LSHIFT] or mods[pygame.K_RSHIFT]
            alt_held = mods[pygame.K_LALT] or mods[pygame.K_RALT]
            
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_z:
                print("🔄 Manual restart - restarting program...")
                restart_program()
            elif event.key == pygame.K_h:
                print_comprehensive_animation_help()
            
            # === ENHANCED ANIMATION CONTROLS (NEW FOR STEP 6) ===
            elif event.key == pygame.K_p:
                if alt_held:
                    toggle_light_path_animation()
                else:
                    toggle_model_animation()
            elif event.key == pygame.K_l:
                if shift_held:
                    toggle_light_bobbing()
                else:
                    toggle_light_orbit()
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                if shift_held:
                    adjust_animation_speed(0.1)  # Fine adjustment
                else:
                    adjust_animation_speed(0.5)  # Coarse adjustment
            elif event.key == pygame.K_MINUS:
                if shift_held:
                    adjust_animation_speed(-0.1)  # Fine adjustment
                else:
                    adjust_animation_speed(-0.5)  # Coarse adjustment
            elif event.key == pygame.K_r:
                if alt_held:
                    reset_all_animations()
                else:
                    toggle_shadows()  # Keep existing shadow toggle on 'r'
            
            # Animation preset selection (1-5)
            elif event.key >= pygame.K_1 and event.key <= pygame.K_5:
                preset_number = event.key - pygame.K_0
                apply_animation_preset(preset_number)
            
            # === EXISTING LIGHTING CONTROLS ===
            elif event.key == pygame.K_j:
                move_light('left')
            elif event.key == pygame.K_SEMICOLON:
                move_light('right')
            elif event.key == pygame.K_i:
                move_light('forward')
            elif event.key == pygame.K_k:
                move_light('back')
            elif event.key == pygame.K_u:
                move_light('up')
            elif event.key == pygame.K_o:
                move_light('down')
            elif event.key == pygame.K_COMMA:
                adjust_material_shininess(-8.0)
            elif event.key == pygame.K_PERIOD:
                adjust_material_shininess(8.0)
            
            # === EXISTING DISPLAY CONTROLS ===
            elif event.key == pygame.K_f:
                toggle_wireframe()
            elif event.key == pygame.K_t:
                toggle_ground_plane()
            
            # === EXISTING CAMERA CONTROLS ===
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
    """Print comprehensive startup instructions for Step 6."""
    print("\n" + "="*90)
    print("🎬 USS Enterprise 3D Viewer - Step 6: Advanced Animation System")
    print("="*90)
    print("✨ Experience smooth, professional-quality animation with full control!")
    print("🎯 This step demonstrates advanced frame-rate independent animation techniques.")
    
    print("\n🌟 NEW ANIMATION FEATURES:")
    print("  • Multi-layered model animation with smooth interpolation")
    print("  • Advanced light animation: orbital motion + vertical bobbing")
    print("  • Frame-rate independent timing using delta time")
    print("  • Global animation speed control with fine/coarse adjustment")
    print("  • Animation presets for instant cool effects")
    print("  • Independent animation toggles (model vs light vs effects)")
    print("  • Professional easing and smoothing functions")
    
    print("\n🚀 QUICK ANIMATION DEMO:")
    print("  1. Watch the USS Enterprise rotate automatically!")
    print("  2. Press 'L' to make the light orbit around the model")
    print("  3. Press 'Shift+L' to add vertical light bobbing")
    print("  4. Press '+' or '-' to speed up/slow down all animations")
    print("  5. Press '1', '2', '3', '4', or '5' for different animation presets")
    print("  6. Press 'P' to pause/resume model animation")
    print("  7. Press 'Alt+R' to reset all animations")
    
    print("\n⚡ ENHANCED ANIMATION CONTROLS:")
    print("  P           - Toggle model animation pause/resume")
    print("  L           - Toggle light orbit animation")
    print("  Shift+L     - Toggle light vertical bobbing animation")
    print("  +/-         - Increase/decrease animation speed (coarse)")
    print("  Shift++/-   - Fine-tune animation speed")
    print("  Alt+P       - Toggle light path animation (figure-8)")
    print("  Alt+R       - Reset ALL animations to defaults")
    print("  1-5         - Apply animation presets (try them all!)")
    
    print("\n💫 ANIMATION PRESETS:")
    print("  1 - 'Showcase': Slow, elegant model rotation + light orbit")
    print("  2 - 'Dynamic': Fast model rotation + light bobbing")
    print("  3 - 'Cinematic': Model paused + complex light movement")
    print("  4 - 'Hyperdrive': Everything fast + light path animation")
    print("  5 - 'Zen': Very slow, peaceful animations")
    
    print("\n🎨 VISUAL FEEDBACK:")
    print("  • Model color changes: blue when animating, red when paused")
    print("  • Light indicator changes color based on animation state:")
    print("    - Yellow: orbit only    - Cyan: bobbing only")
    print("    - Magenta: both         - Pink: static")
    print("  • Light indicator pulses when animated")
    print("  • Console shows detailed animation status every 2 seconds")
    
    print("\n📊 TECHNICAL FEATURES:")
    print("  • Frame-rate independent using delta time")
    print("  • Smooth interpolation and easing functions")
    print("  • Modular animation system in graphics_utils.py")
    print("  • State management for easy integration into future steps")
    print("  • Hot-reload support for rapid development")
    
    print("\n🔥 TRY THIS ANIMATION SEQUENCE:")
    print("  1. Press '1' for Showcase preset - see smooth, elegant motion")
    print("  2. Press '4' for Hyperdrive preset - experience fast action!")
    print("  3. Press '+' several times to speed everything up")
    print("  4. Press 'P' to pause model but keep light moving")
    print("  5. Press 'Shift+L' to add light bobbing")
    print("  6. Press '-' to slow it down and appreciate the smoothness")
    print("  7. Press 'Alt+R' to reset and try preset '5' for zen mode")
    
    print("\n🎓 EDUCATIONAL VALUE:")
    print("  • Learn frame-rate independent animation techniques")
    print("  • Understand smooth interpolation and easing")
    print("  • See how modular animation systems work")
    print("  • Experience professional-quality 3D animation")
    
    print("\n" + "="*90)
    print("🎬 Ready for smooth animation! Try the presets and speed controls!")
    print("="*90 + "\n")

def main():
    """Main function with enhanced animation system."""
    try:
        # Initialize pygame
        pygame.init()
        
        # Set up resizable display
        screen = pygame.display.set_mode((window_width, window_height), 
                                       DOUBLEBUF | OPENGL | RESIZABLE)
        pygame.display.set_caption("USS Enterprise - Step 6: Advanced Animation System")
        
        # Initialize OpenGL and load model
        if not init_opengl():
            print("Failed to initialize. Exiting...")
            return
        
        # Print startup instructions
        print_startup_instructions()
        
        # Start with a nice animation preset
        apply_animation_preset(1)  # Start with "Showcase" preset
        
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
            
            # Handle events with enhanced animation controls
            running = handle_events()
            
            # Render the scene with full animation
            render()
            
            # Target 60 FPS for smooth animation
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