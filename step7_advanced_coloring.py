#!/usr/bin/env python3
"""
step7_simplified.py - USS Enterprise 3D Viewer with WORKING Advanced Coloring
Step 7 of Computer Graphics Major Project - SIMPLIFIED WORKING VERSION

FIXES:
- Removed complex caching that was causing 6 FPS performance
- Simplified color system that works immediately
- Fixed color scheme changes (Ctrl+1/2/3 now work!)
- Fixed animation preset 3 model spinning (P key)
- Restored 60+ FPS performance

Features:
- All features from Step 6 (perspective camera, Phong lighting, shadow projection, enhanced interactivity, advanced animation)
- WORKING per-part coloring system for USS Enterprise components
- Position-based part identification using 3D coordinates
- Angle-based dynamic brightness using face normals and dot products
- Material variation system with different properties per part
- Multiple coloring modes with instant switching
- WORKING: Color schemes change immediately when you press Ctrl+1/2/3

Controls:
- M: Cycle enhanced coloring modes
- Ctrl+1/2/3: Switch color schemes (OR F1/F2/F3) - NOW WORKING!
- F: Toggle wireframe
- R: Toggle shadows
- P: Toggle model animation (works in all presets)
- All previous animation and camera controls
"""

import sys
import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import time

# Import ALL previous systems (animation, lighting, shadows, camera)
from graphics_utils import *

# Import SIMPLIFIED coloring system
try:
    from coloring_utils import (
        precompute_face_data_enhanced,
        apply_enhanced_face_coloring,
        cycle_coloring_mode,
        set_color_scheme_enhanced,
        get_enhanced_status,
        print_enhanced_coloring_help,
        debug_part_identification,
        clear_enhanced_cache,
        COLORING_MODE_POSITION,
        COLORING_MODE_ANGLE,
        COLORING_MODE_MIXED,
        COLORING_MODE_ANIMATED,
        COLORING_MODE_SOLID,
        current_coloring_mode,
        COLOR_SCHEMES,
        current_color_scheme,
        USS_ENTERPRISE_PARTS,
        face_parts_cache,
        face_centers_cache,
        face_normals_cache,
        cache_initialized
    )
    print("✅ Simplified coloring system imported successfully")
except ImportError as e:
    print(f"❌ Failed to import coloring system: {e}")
    print("❌ Make sure coloring_utils.py is in the same directory")
    sys.exit(1)

# === SIMPLIFIED VARIABLES ===

# Global model instance
model = None

# Local variables for toggles
local_wireframe_mode = False
local_shadows_enabled = True
local_ground_plane_visible = True

# Performance tracking
frame_times = []
last_fps_report = 0.0
fps_report_interval = 3.0

# === SIMPLIFIED RENDERING FUNCTIONS ===

def draw_model_with_enhanced_coloring():
    """
    SIMPLIFIED: Draw the 3D model with enhanced coloring.
    This version is simplified for reliability and performance.
    """
    if not model or not model.is_loaded():
        return
    
    # Set default material properties for lighting
    if lighting_enabled:
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, material_ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, material_specular)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, material_shininess)
    
    # Apply all transformations in correct order
    glPushMatrix()
    
    # 1. Apply user mouse rotations first
    glRotatef(rotation_x, 1.0, 0.0, 0.0)
    glRotatef(rotation_y, 0.0, 1.0, 0.0)
    
    # 2. Apply model animations
    apply_model_animation_transforms()
    
    # 3. Draw each face with enhanced coloring
    for i, face in enumerate(model.faces):
        # Set the normal for lighting
        if i < len(model.normals) and len(model.normals[i]) >= 3:
            try:
                face_normal = model.normals[i]
                glNormal3f(face_normal[0], face_normal[1], face_normal[2])
            except (IndexError, TypeError):
                glNormal3f(0.0, 0.0, 1.0)
        else:
            glNormal3f(0.0, 0.0, 1.0)
        
        # Apply enhanced coloring (simplified - no caching)
        apply_enhanced_face_coloring(i, lighting_enabled)
        
        # Draw solid face
        glBegin(GL_POLYGON)
        for vertex_idx in face:
            if vertex_idx < len(model.vertices):
                vertex = model.vertices[vertex_idx]
                glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()
        
        # Draw wireframe lines if wireframe mode is on
        if local_wireframe_mode:
            glColor3f(0.2, 0.3, 0.4)
            glBegin(GL_LINE_LOOP)
            for vertex_idx in face:
                if vertex_idx < len(model.vertices):
                    vertex = model.vertices[vertex_idx]
                    glVertex3f(vertex[0], vertex[1], vertex[2])
            glEnd()
    
    glPopMatrix()

# === PERFORMANCE MONITORING ===

def track_frame_performance():
    """Track frame performance to monitor improvements."""
    global frame_times, last_fps_report
    
    current_time = time.time()
    frame_times.append(current_time)
    
    # Keep only last 60 frames
    if len(frame_times) > 60:
        frame_times.pop(0)
    
    # Report FPS every few seconds
    if current_time - last_fps_report >= fps_report_interval:
        if len(frame_times) >= 2:
            time_span = frame_times[-1] - frame_times[0]
            if time_span > 0:
                fps = (len(frame_times) - 1) / time_span
                print(f"🚀 SIMPLIFIED Step 7 Performance: {fps:.1f} FPS")
        last_fps_report = current_time

# === TOGGLE FUNCTIONS ===

def toggle_wireframe_fixed():
    """Toggle wireframe mode."""
    global local_wireframe_mode
    
    local_wireframe_mode = not local_wireframe_mode
    
    if local_wireframe_mode:
        message = "🔲 WIREFRAME: ON"
    else:
        message = "🔳 SOLID: ON"
    
    print(message)
    set_status_message(message)

def toggle_shadows_fixed():
    """Toggle shadow rendering."""
    global local_shadows_enabled
    
    local_shadows_enabled = not local_shadows_enabled
    message = f"🌫️  SHADOWS: {'ON' if local_shadows_enabled else 'OFF'}"
    print(message)
    set_status_message(message)

def toggle_ground_plane_fixed():
    """Toggle ground plane visibility."""
    global local_ground_plane_visible
    
    local_ground_plane_visible = not local_ground_plane_visible
    message = f"🌍 GROUND: {'VISIBLE' if local_ground_plane_visible else 'HIDDEN'}"
    print(message)
    set_status_message(message)

# === MAIN FUNCTIONS ===

def init_opengl():
    """Initialize OpenGL settings and load the 3D model with enhanced coloring support."""
    global model
    
    # Set background color
    glClearColor(0.02, 0.05, 0.1, 1.0)
    
    # Enable depth testing and smooth shading
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    
    # Set up viewport
    glViewport(0, 0, window_width, window_height)
    
    # Initialize systems
    init_perspective_camera()
    init_lighting_system()
    init_animation_system()
    
    # Load the USS Enterprise model - try multiple possible filenames
    possible_filenames = [
        "USS Enterprise gray scale.obj",
        "USS_Enterprise_grayscale.obj", 
        "USS_enterprise_grayscale.obj",
        "USS_Enterprise_gray_scale.obj",
        "uss_enterprise.obj"
    ]
    
    model = None
    for filename in possible_filenames:
        print(f"Trying to load: {filename}")
        test_model = Model3D(filename)
        if test_model.is_loaded():
            model = test_model
            print(f"✅ Successfully loaded: {filename}")
            break
    
    if not model or not model.is_loaded():
        print("❌ Failed to load USS Enterprise model.")
        print("📁 Available .obj files in current directory:")
        obj_files = [f for f in os.listdir('.') if f.endswith('.obj')]
        if obj_files:
            for obj_file in obj_files:
                print(f"   - {obj_file}")
        else:
            print("   (No .obj files found)")
        return False
    
    # Pre-compute face data for position-based coloring
    success = precompute_face_data_enhanced(model)
    if not success:
        print("❌ Failed to pre-compute face data")
        return False
    
    # Add this after precompute_face_data_enhanced(model) succeeds
    debug_part_identification(model)

    print(f"📷 Camera initialized at: ({eyeX:.1f}, {eyeY:.1f}, {eyeZ:.1f})")
    print(f"🎬 Animation system initialized")
    print(f"🎨 SIMPLIFIED coloring system ready!")
    return True

def render():
    """Main rendering function with enhanced coloring support."""
    # Track performance
    track_frame_performance()
    
    # Update all systems
    calculate_delta_time()
    update_camera_position()
    update_lighting_system()
    update_all_animation_systems()
    
    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Set up camera
    setup_camera()
    
    # === RENDERING ORDER IS IMPORTANT FOR SHADOWS ===
    
    # 1. Draw ground plane first
    draw_ground_plane(ground_plane_y, ground_size, ground_color, 
                     local_ground_plane_visible, lighting_enabled)
    
    # 2. Draw shadows
    total_rotation_y = rotation_y + get_total_model_rotation()
    current_light_pos = [light_position[0], light_position[1], light_position[2], 1.0]
    draw_model_shadow(model, current_light_pos, ground_plane_y, shadow_color, 
                     rotation_x, total_rotation_y, local_shadows_enabled)
    
    # 3. Draw the main model with enhanced coloring
    draw_model_with_enhanced_coloring()
    
    # 4. Draw light position indicator
    draw_light_indicator()
    
    # Update display
    pygame.display.flip()

def handle_events():
    """FIXED: Handle pygame events with working color scheme controls."""
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
            ctrl_held = mods[pygame.K_LCTRL] or mods[pygame.K_RCTRL]
            
            # === SYSTEM CONTROLS ===
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_z:
                print("🔄 Manual restart - restarting program...")
                restart_program()
            elif event.key == pygame.K_h:
                print_enhanced_help()
            
            # === ENHANCED COLORING CONTROLS ===
            elif event.key == pygame.K_m:
                mode_name = cycle_coloring_mode()
                print(f"🎨 ═══ COLORING MODE CHANGED ═══")
                print(f"    ✨ {mode_name}")
                print(f"🎨 ═══════════════════════════════")
            
            # === COLOR SCHEME CONTROLS - FIXED AND WORKING ===
            elif ctrl_held and event.key == pygame.K_1:
                set_color_scheme_enhanced('starfleet')
                print("🎨 ✅ STARFLEET colors activated! (blue-gray)")
            elif ctrl_held and event.key == pygame.K_2:
                set_color_scheme_enhanced('battle')
                print("🎨 ✅ BATTLE colors activated! (red alert!)")
            elif ctrl_held and event.key == pygame.K_3:
                set_color_scheme_enhanced('exploration')
                print("🎨 ✅ EXPLORATION colors activated! (green/purple)")
            
            # Alternative F-key controls
            elif event.key == pygame.K_F1:
                set_color_scheme_enhanced('starfleet')
                print("🎨 ✅ STARFLEET colors activated! (F1)")
            elif event.key == pygame.K_F2:
                set_color_scheme_enhanced('battle')
                print("🎨 ✅ BATTLE colors activated! (F2)")
            elif event.key == pygame.K_F3:
                set_color_scheme_enhanced('exploration')
                print("🎨 ✅ EXPLORATION colors activated! (F3)")
            
            # === ANIMATION PRESET SELECTION ===
            elif not ctrl_held and event.key >= pygame.K_1 and event.key <= pygame.K_5:
                preset_number = event.key - pygame.K_0
                apply_animation_preset(preset_number)
                print(f"🎬 ✅ Animation preset {preset_number} applied!")
            
            # === DISPLAY CONTROLS ===
            elif event.key == pygame.K_f:
                toggle_wireframe_fixed()
            elif event.key == pygame.K_r:
                if alt_held:
                    reset_all_animations()
                else:
                    toggle_shadows_fixed()
            elif event.key == pygame.K_g:
                toggle_ground_plane_fixed()
            
            # === ANIMATION CONTROLS ===
            elif event.key == pygame.K_p:
                if alt_held:
                    toggle_light_path_animation()
                else:
                    toggle_model_animation()
                    print(f"🎬 Model animation: {'PAUSED' if model_animation_paused else 'PLAYING'}")
            elif event.key == pygame.K_l:
                if shift_held:
                    toggle_light_bobbing()
                else:
                    toggle_light_orbit()
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                if shift_held:
                    adjust_animation_speed(0.1)
                else:
                    adjust_animation_speed(0.5)
            elif event.key == pygame.K_MINUS:
                if shift_held:
                    adjust_animation_speed(-0.1)
                else:
                    adjust_animation_speed(-0.5)
            
            # === LIGHTING CONTROLS ===
            elif event.key == pygame.K_t:
                toggle_lighting()
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
            elif event.key == pygame.K_F4:
                # Force cache refresh with new part definitions
                clear_enhanced_cache()
                precompute_face_data_enhanced(model)
                debug_part_identification(model)
                print("🔄 Part identification cache refreshed!")
            
            # === CAMERA CONTROLS ===
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

def print_enhanced_help():
    """Print enhanced help information."""
    status = get_enhanced_status()
    
    print("\n" + "="*85)
    print("🎨 USS Enterprise 3D Viewer - SIMPLIFIED Advanced Coloring")
    print("="*85)
    
    print("\n🎨 COLOR SCHEME CONTROLS (WORKING!):")
    print("  Ctrl+1       - Starfleet colors (blue-gray)")
    print("  Ctrl+2       - Battle colors (red alert!)")
    print("  Ctrl+3       - Exploration colors (green/purple)")
    print("  F1/F2/F3     - Alternative color scheme keys")
    
    print("\n🌈 COLORING MODES:")
    print("  M            - Cycle through coloring modes:")
    print("    1. Solid Color           - Single color")
    print("    2. Position-Based Parts  - Parts by 3D position")
    print("    3. Angle-Based Brightness- Brightness by face orientation")
    print("    4. Mixed (Position+Angle)- Realistic colored shading")
    print("    5. Animated Effects      - Pulsing animations")
    
    print("\n🔧 DISPLAY CONTROLS:")
    print("  F - Toggle wireframe")
    print("  R - Toggle shadows")
    print("  G - Toggle ground plane")
    print("  T - Toggle lighting on/off")
    
    print("\n📷 CAMERA CONTROLS:")
    print("  W/S - Zoom in/out  |  A/D - Orbit left/right")
    print("  Q/E - Look up/down |  Mouse - Rotate model")
    print("  C   - Reset camera")
    
    print("\n🎬 ANIMATION CONTROLS:")
    print("  P   - Toggle model animation (FIXED - works in all presets!)")
    print("  L   - Toggle light orbit")
    print("  1-5 - Animation presets (without Ctrl)")
    print("  +/- - Adjust speed")
    
    print(f"\n📊 CURRENT STATUS:")
    print(f"  Coloring Mode:     {status['mode']}")
    print(f"  Color Scheme:      {status['scheme']}")
    print(f"  Wireframe:         {'ON' if local_wireframe_mode else 'OFF'}")
    print(f"  Shadows:           {'ON' if local_shadows_enabled else 'OFF'}")
    print(f"  Ground Plane:      {'ON' if local_ground_plane_visible else 'OFF'}")
    print(f"  Lighting:          {'ON' if lighting_enabled else 'OFF'}")
    print(f"  Model Animation:   {'PAUSED' if model_animation_paused else 'PLAYING'}")
    
    print("\n🔧 OTHER CONTROLS:")
    print("  H - This help  |  Z - Restart  |  ESC - Quit")
    
    print("="*85 + "\n")

def main():
    """Main function with simplified working coloring system."""
    try:
        # Initialize pygame
        pygame.init()
        
        # Set up resizable display
        screen = pygame.display.set_mode((window_width, window_height), 
                                       DOUBLEBUF | OPENGL | RESIZABLE)
        pygame.display.set_caption("USS Enterprise - Step 7: SIMPLIFIED Advanced Coloring")
        
        # Initialize OpenGL and load model
        if not init_opengl():
            print("Failed to initialize. Exiting...")
            return
        
        print("\n🚀 === USS Enterprise 3D Viewer - SIMPLIFIED Step 7 ===")
        print("✨ WORKING: Color schemes change immediately!")
        print("✨ FIXED: Model animation (P key) works in all presets!")
        print("✨ PERFORMANCE: Should run at 60+ FPS like Step 6!")
        print("\n🎨 COLOR SCHEME CONTROLS:")
        print("  Ctrl+1  - Starfleet colors (blue-gray)")
        print("  Ctrl+2  - Battle colors (dramatic red!)")
        print("  Ctrl+3  - Exploration colors (green/purple)")
        print("  F1/F2/F3 - Alternative keys")
        print("\n🎬 OTHER CONTROLS:")
        print("  M       - Cycle coloring modes")
        print("  P       - Toggle model animation")
        print("  1-5     - Animation presets")
        print("  H       - Full help")
        print("\n🎯 TEST SEQUENCE:")
        print("  1. Press 'Ctrl+2' → Should see dramatic red/yellow colors!")
        print("  2. Press 'Ctrl+3' → Should see bright green/purple colors!")
        print("  3. Press 'Ctrl+1' → Should return to blue-gray colors!")
        print("  4. Press 'M' → Cycle through different coloring modes!")
        print("  5. Press '3' → Animation preset 3, then 'P' → Model should spin!")
        print("\n🚀 Starting simplified renderer - colors should change instantly!\n")
        
        # Start with nice defaults
        apply_animation_preset(1)
        set_color_scheme_enhanced('starfleet')
        
        # Main loop
        clock = pygame.time.Clock()
        running = True
        frame_count = 0
        
        while running:
            frame_count += 1
            
            # Handle events
            running = handle_events()
            
            # Render the scene
            render()
            
            # Target 60 FPS
            clock.tick(60)
            
            # Performance check every 300 frames (5 seconds at 60fps)
            if frame_count % 300 == 0:
                actual_fps = clock.get_fps()
                if actual_fps >= 55:
                    print(f"✅ Performance excellent: {actual_fps:.1f} FPS")
                elif actual_fps >= 30:
                    print(f"⚠️  Performance moderate: {actual_fps:.1f} FPS")
                else:
                    print(f"❌ Performance poor: {actual_fps:.1f} FPS")
        
        print("Exiting cleanly...")
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    main()