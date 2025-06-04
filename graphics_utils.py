#!/usr/bin/env python3
"""
graphics_utils.py - Complete utilities for Computer Graphics Major Project
Contains all shared functions including lighting, interactivity, shadow systems, and animation systems.
OPTIMIZED FOR RESPONSIVE CONTROLS
"""

import sys
import os
import time
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# === SHARED GLOBAL VARIABLES ===
window_width = 800
window_height = 600

# Camera variables
eyeX, eyeY, eyeZ = 0.0, 0.0, 8.0
centerX, centerY, centerZ = 0.0, 0.0, 0.0
upX, upY, upZ = 0.0, 1.0, 0.0
camera_speed = 7.0  # BALANCED: responsive but smooth

# Orbital camera system - OPTIMIZED FOR SMOOTH RESPONSIVENESS
camera_yaw = 0.0
camera_pitch = 0.0
camera_distance = 8.0
orbit_speed = 100.0  # BALANCED: fast but smooth
pitch_limit = 89.0
zoom_speed = 3.5     # BALANCED: responsive but smooth
pitch_speed = 70.0   # BALANCED: fast but smooth
min_zoom_distance = 2.0
max_zoom_distance = 50.0

# Movement multipliers - BALANCED FOR SMOOTH RESPONSIVENESS
forward_speed_multiplier = 1.3  # BALANCED: faster but smooth
strafe_speed_multiplier = 1.3   # BALANCED: faster but smooth
vertical_speed_multiplier = 1.6  # BALANCED: faster but smooth
rotation_speed = 1.2  # BALANCED: responsive but smooth mouse rotation

# Turbo mode - ENHANCED
turbo_active = False
turbo_multiplier = 3.0  # REDUCED from 5.0 for better control
fast_smoothing_threshold = 15.0

# Smoothing and timing - OPTIMIZED FOR SMOOTH RESPONSIVENESS
max_distance_from_origin = 50.0
smoothing_boost_on_input = True
input_smoothing_factor = 0.15   # BALANCED: responsive but smooth
idle_smoothing_factor = 0.88    # BALANCED: less sticky but smooth
fast_mode_smoothing = 0.08      # BALANCED: very responsive but not jerky
last_input_time = 0.0

# Delta time variables
last_frame_time = 0.0
delta_time = 0.0
frame_count = 0
delta_time_sum = 0.0
last_debug_time = 0.0

# Mouse rotation - ENHANCED RESPONSIVENESS
rotation_x = 0.0
rotation_y = 0.0
mouse_last_x = 0
mouse_last_y = 0
mouse_dragging = False
mouse_sensitivity = 1.0  # NEW: Adjustable mouse sensitivity

# Hot reload
script_path = __file__
last_modified = 0
check_reload_timer = 0

# Key state tracking - OPTIMIZED FOR SMOOTH RESPONSIVENESS
keys_pressed = set()
movement_smoothing = 0.82  # BALANCED: smooth but responsive
current_smoothing = 0.82   # BALANCED: smooth but responsive

# Camera velocity
camera_velocity = np.array([0.0, 0.0, 0.0])
rotation_velocity = np.array([0.0, 0.0])
zoom_velocity = 0.0

# === LIGHTING SYSTEM VARIABLES ===

# Display modes
wireframe_mode = False
lighting_enabled = True
shadows_enabled = True
ground_plane_visible = True
animation_paused = False

# Legacy animation system
auto_rotation_enabled = True
rotation_speed_degrees_per_sec = 15.0
current_auto_rotation = 0.0

# Enhanced lighting
light_position = [5.0, 5.0, 5.0, 1.0]
default_light_position = [5.0, 5.0, 5.0, 1.0]
light_move_speed = 1.5  # INCREASED from 1.0
animate_light = False
light_rotation_speed = 60.0
light_rotation_angle = 0.0
light_orbit_radius = 8.0

# Shadow and ground settings
ground_plane_y = -3.0
shadow_color = [0.1, 0.1, 0.1, 0.8]
ground_color = [0.3, 0.4, 0.3, 1.0]
ground_size = 30.0

# Light components
ambient_light = [0.2, 0.2, 0.3, 1.0]
diffuse_light = [0.8, 0.9, 1.0, 1.0]
specular_light = [1.0, 1.0, 1.0, 1.0]

# Material properties
material_ambient = [0.3, 0.3, 0.4, 1.0]
material_diffuse = [0.6, 0.7, 0.8, 1.0]
material_specular = [0.9, 0.9, 0.9, 1.0]
material_shininess = 32.0

# Status display
show_status_overlay = False
last_action_message = ""
last_action_time = 0.0
message_display_duration = 2.0

# === ANIMATION SYSTEM VARIABLES ===

# Global animation timing
total_animation_time = 0.0
animation_start_time = 0.0
animation_speed_multiplier = 1.0
min_animation_speed = 0.1
max_animation_speed = 5.0

# Model animation
model_animation_paused = False
model_rotation_angle = 0.0
model_rotation_speed = 30.0
model_rotation_axis = [0.0, 1.0, 0.0]

# Light animation - orbital motion
light_orbit_enabled = False
light_orbit_angle = 0.0
light_orbit_speed = 45.0
light_orbit_radius = 6.0
light_orbit_center = [0.0, 3.0, 0.0]

# Light animation - vertical bobbing
light_bobbing_enabled = False
light_bobbing_speed = 2.0
light_bobbing_amplitude = 1.5
light_bobbing_offset = 0.0
light_base_height = 5.0

# Light animation - complex path
light_path_enabled = False
light_path_speed = 1.0
light_path_scale = 4.0

# Animation presets
current_animation_preset = 1
animation_presets = {
    1: {
        'name': 'Showcase',
        'model_speed': 20.0,
        'model_paused': False,
        'light_orbit': True,
        'light_orbit_speed': 30.0,
        'light_bobbing': False,
        'global_speed': 1.0
    },
    2: {
        'name': 'Dynamic',
        'model_speed': 60.0,
        'model_paused': False,
        'light_orbit': False,
        'light_bobbing': True,
        'light_bobbing_speed': 3.0,
        'global_speed': 1.5
    },
    3: {
        'name': 'Cinematic',
        'model_speed': 0.0,
        'model_paused': True,
        'light_orbit': True,
        'light_orbit_speed': 20.0,
        'light_bobbing': True,
        'light_bobbing_speed': 1.5,
        'global_speed': 0.8
    },
    4: {
        'name': 'Hyperdrive',
        'model_speed': 120.0,
        'model_paused': False,
        'light_orbit': True,
        'light_orbit_speed': 90.0,
        'light_path': True,
        'global_speed': 2.5
    },
    5: {
        'name': 'Zen',
        'model_speed': 10.0,
        'model_paused': False,
        'light_orbit': True,
        'light_orbit_speed': 15.0,
        'light_bobbing': True,
        'light_bobbing_speed': 0.5,
        'global_speed': 0.3
    }
}

# Easing and smoothing
use_easing = True
easing_factor = 0.1
smooth_transitions = True

# === MODEL LOADING FUNCTIONS ===

def load_obj(filename):
    """
    Load vertices and faces from an OBJ file.
    Returns vertices as numpy array and faces as list of vertex indices.
    """
    vertices = []
    faces = []
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('#'): continue
                
                values = line.split()
                if not values: continue
                
                if values[0] == 'v':
                    vertices.append([float(x) for x in values[1:4]])
                elif values[0] == 'f':
                    face = []
                    for v in values[1:]:
                        if '/' in v:
                            vertex_indices = v.split('/')
                            face.append(int(vertex_indices[0]) - 1)
                        else:
                            face.append(int(v) - 1)
                    faces.append(face)
    except FileNotFoundError:
        print(f"Error: Could not find file '{filename}'")
        return None, None
    except Exception as e:
        print(f"Error loading OBJ file: {e}")
        return None, None
    
    return np.array(vertices), faces

def calculate_face_normals(vertices, faces):
    """Calculate normal vectors for each face."""
    normals = []
    for face in faces:
        if len(face) >= 3:
            v0 = vertices[face[0]]
            v1 = vertices[face[1]]
            v2 = vertices[face[2]]
            
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = np.cross(edge1, edge2)
            
            length = np.sqrt(normal.dot(normal))
            if length > 0:
                normal = normal / length
            
            normals.append(normal)
        else:
            normals.append(np.array([0, 0, 1]))
    
    return np.array(normals)

def center_and_scale_model(vertices):
    """Center the model at origin and scale it to fit nicely in view."""
    if len(vertices) == 0:
        return vertices
    
    min_coords = np.min(vertices, axis=0)
    max_coords = np.max(vertices, axis=0)
    center = (min_coords + max_coords) / 2
    
    centered_vertices = vertices - center
    
    max_dimension = np.max(max_coords - min_coords)
    if max_dimension > 0:
        scale_factor = 4.0 / max_dimension
        centered_vertices *= scale_factor
    
    return centered_vertices

# === CAMERA FUNCTIONS - OPTIMIZED FOR RESPONSIVENESS ===

def calculate_delta_time():
    """Calculate the time elapsed since the last frame - OPTIMIZED FOR SMOOTHNESS."""
    global last_frame_time, delta_time, frame_count, delta_time_sum
    
    current_time = time.time()
    
    if last_frame_time == 0.0:
        delta_time = 1.0 / 60.0
    else:
        raw_delta = current_time - last_frame_time
        
        # BALANCED: Prevent huge jumps but allow natural variation
        if raw_delta > 0.033:  # Cap at ~30 FPS minimum
            delta_time = 0.033
        elif raw_delta < 0.001:
            delta_time = 0.001
        else:
            # BALANCED: Smooth but responsive delta time
            delta_time = delta_time * 0.7 + raw_delta * 0.3
    
    last_frame_time = current_time
    frame_count += 1
    delta_time_sum += delta_time

def init_perspective_camera():
    """Set up perspective projection matrix."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    aspect_ratio = window_width / window_height
    field_of_view = 45.0
    near_plane = 0.1
    far_plane = 100.0
    
    gluPerspective(field_of_view, aspect_ratio, near_plane, far_plane)
    glMatrixMode(GL_MODELVIEW)

def setup_camera():
    """Set up the camera using gluLookAt."""
    glLoadIdentity()
    gluLookAt(
        eyeX, eyeY, eyeZ,
        centerX, centerY, centerZ,
        upX, upY, upZ
    )

def update_orbital_camera():
    """Update camera position using orbital coordinates."""
    global eyeX, eyeY, eyeZ
    
    yaw_rad = np.radians(camera_yaw)
    pitch_rad = np.radians(camera_pitch)
    
    eyeX = centerX + camera_distance * np.cos(pitch_rad) * np.sin(yaw_rad)
    eyeY = centerY + camera_distance * np.sin(pitch_rad)
    eyeZ = centerZ + camera_distance * np.cos(pitch_rad) * np.cos(yaw_rad)

def update_dynamic_smoothing():
    """Update smoothing based on user input - OPTIMIZED FOR SMOOTH RESPONSIVENESS."""
    global current_smoothing, last_input_time
    
    current_time = time.time()
    
    if not smoothing_boost_on_input:
        current_smoothing = movement_smoothing
        return
    
    has_input = bool(keys_pressed)
    current_speed = camera_speed
    if turbo_active:
        current_speed *= turbo_multiplier
    
    if has_input:
        last_input_time = current_time
        
        if current_speed > fast_smoothing_threshold or turbo_active:
            target_smoothing = fast_mode_smoothing
        else:
            target_smoothing = input_smoothing_factor
    else:
        time_since_input = current_time - last_input_time
        
        # BALANCED: Responsive transition but smooth
        if time_since_input < 0.2:  # Slightly longer transition
            blend_factor = time_since_input / 0.2
            if current_speed > fast_smoothing_threshold:
                target_smoothing = fast_mode_smoothing + (input_smoothing_factor - fast_mode_smoothing) * blend_factor
            else:
                target_smoothing = input_smoothing_factor + (idle_smoothing_factor - input_smoothing_factor) * blend_factor
        else:
            target_smoothing = idle_smoothing_factor
    
    # BALANCED: Smooth but responsive smoothing transitions
    transition_speed = 0.15 if has_input else 0.25  # Smoother transitions
    current_smoothing = current_smoothing * (1.0 - transition_speed) + target_smoothing * transition_speed

def update_camera_position():
    """Update camera position with responsive controls - HEAVILY OPTIMIZED."""
    global eyeX, eyeY, eyeZ, camera_velocity, rotation_velocity
    global camera_yaw, camera_pitch, camera_distance
    global centerX, centerY, centerZ
    global zoom_velocity
    
    update_dynamic_smoothing()
    
    effective_speed = camera_speed
    effective_orbit_speed = orbit_speed * strafe_speed_multiplier
    effective_zoom_speed = zoom_speed * forward_speed_multiplier
    effective_pitch_speed = pitch_speed * vertical_speed_multiplier
    
    if turbo_active:
        effective_speed *= turbo_multiplier
        effective_orbit_speed *= turbo_multiplier
        effective_zoom_speed *= turbo_multiplier
        effective_pitch_speed *= turbo_multiplier
    
    target_rotation_velocity = np.array([0.0, 0.0])
    
    if K_a in keys_pressed:
        target_rotation_velocity[0] = effective_orbit_speed
    if K_d in keys_pressed:
        target_rotation_velocity[0] = -effective_orbit_speed
    
    if K_q in keys_pressed:
        target_rotation_velocity[1] = effective_pitch_speed
    if K_e in keys_pressed:
        target_rotation_velocity[1] = -effective_pitch_speed
    
    # OPTIMIZED: More responsive velocity updates
    rotation_velocity = rotation_velocity * current_smoothing + target_rotation_velocity * (1.0 - current_smoothing)
    
    if delta_time > 0:
        camera_yaw += rotation_velocity[0] * delta_time
        camera_pitch += rotation_velocity[1] * delta_time
        
        camera_pitch = np.clip(camera_pitch, -pitch_limit, pitch_limit)
        camera_yaw = camera_yaw % 360.0
    
    target_zoom_velocity = 0.0
    
    if K_w in keys_pressed:
        target_zoom_velocity = -effective_zoom_speed
    if K_s in keys_pressed:
        target_zoom_velocity = effective_zoom_speed
    
    # OPTIMIZED: More responsive zoom
    zoom_velocity = zoom_velocity * current_smoothing + target_zoom_velocity * (1.0 - current_smoothing)
    
    if delta_time > 0:
        new_distance = camera_distance + zoom_velocity * delta_time
        camera_distance = np.clip(new_distance, min_zoom_distance, max_zoom_distance)
    
    update_orbital_camera()

def handle_window_resize(width, height):
    """Handle window resize events."""
    global window_width, window_height
    
    window_width = width
    window_height = height
    
    glViewport(0, 0, width, height)
    init_perspective_camera()

# === LIGHTING SYSTEM FUNCTIONS ===

def init_lighting_system():
    """Initialize OpenGL lighting with Phong model components."""
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.1, 0.1, 0.15, 1.0])
    
    glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

def update_lighting_system():
    """Update lighting every frame with animation support."""
    global light_rotation_angle, light_position
    
    # Legacy light animation for backward compatibility
    if animate_light and delta_time > 0:
        light_rotation_angle += light_rotation_speed * delta_time
        light_rotation_angle = light_rotation_angle % 360.0
        
        angle_rad = np.radians(light_rotation_angle)
        light_position[0] = light_orbit_radius * np.cos(angle_rad)
        light_position[1] = 5.0
        light_position[2] = light_orbit_radius * np.sin(angle_rad)
    
    # Advanced light animation
    update_light_animation()
    
    # Update light position in OpenGL
    if lighting_enabled:
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)

def set_material_properties():
    """Set material properties for models."""
    if lighting_enabled:
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, material_ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, material_specular)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, material_shininess)

def draw_light_indicator():
    """Draw light position indicator."""
    if not lighting_enabled:
        return
    
    glDisable(GL_LIGHTING)
    
    glPushMatrix()
    glTranslatef(light_position[0], light_position[1], light_position[2])
    
    glColor3f(1.0, 1.0, 0.0)
    
    glPointSize(15.0)
    glBegin(GL_POINTS)
    glVertex3f(0.0, 0.0, 0.0)
    glEnd()
    
    glLineWidth(2.0)
    glBegin(GL_LINES)
    # X-axis ray
    glColor3f(1.0, 0.5, 0.5)
    glVertex3f(-0.5, 0.0, 0.0)
    glVertex3f(0.5, 0.0, 0.0)
    # Y-axis ray
    glColor3f(0.5, 1.0, 0.5)
    glVertex3f(0.0, -0.5, 0.0)
    glVertex3f(0.0, 0.5, 0.0)
    # Z-axis ray
    glColor3f(0.5, 0.5, 1.0)
    glVertex3f(0.0, 0.0, -0.5)
    glVertex3f(0.0, 0.0, 0.5)
    glEnd()
    
    glLineWidth(1.0)
    glPointSize(1.0)
    glPopMatrix()
    
    if lighting_enabled:
        glEnable(GL_LIGHTING)

# === LEGACY ANIMATION SYSTEM FUNCTIONS ===

def update_all_animations():
    """Update legacy animations for backward compatibility."""
    global current_auto_rotation
    
    if not animation_paused and delta_time > 0:
        if auto_rotation_enabled:
            current_auto_rotation += rotation_speed_degrees_per_sec * delta_time
            current_auto_rotation = current_auto_rotation % 360.0

# === ANIMATION SYSTEM FUNCTIONS ===

def init_animation_system():
    """Initialize the animation system."""
    global animation_start_time, total_animation_time
    
    animation_start_time = time.time()
    total_animation_time = 0.0

def update_all_animation_systems():
    """Update all animation systems."""
    global total_animation_time
    
    if delta_time > 0:
        total_animation_time += delta_time * animation_speed_multiplier
        update_model_animation()
        update_all_animations()

def update_model_animation():
    """Update model rotation animation."""
    global model_rotation_angle
    
    if not model_animation_paused and delta_time > 0:
        rotation_delta = model_rotation_speed * delta_time * animation_speed_multiplier
        
        if use_easing:
            easing_multiplier = 1.0 + easing_factor * np.sin(total_animation_time * 0.5)
            rotation_delta *= easing_multiplier
        
        model_rotation_angle += rotation_delta
        model_rotation_angle = model_rotation_angle % 360.0

def update_light_animation():
    """Update all light animation components."""
    global light_position, light_orbit_angle, light_bobbing_offset
    
    if animate_light:
        return
    
    if delta_time > 0:
        effective_time_delta = delta_time * animation_speed_multiplier
        
        base_pos = list(default_light_position[:3])
        
        if light_orbit_enabled:
            light_orbit_angle += light_orbit_speed * effective_time_delta
            light_orbit_angle = light_orbit_angle % 360.0
            
            angle_rad = np.radians(light_orbit_angle)
            base_pos[0] = light_orbit_center[0] + light_orbit_radius * np.cos(angle_rad)
            base_pos[2] = light_orbit_center[2] + light_orbit_radius * np.sin(angle_rad)
            base_pos[1] = light_orbit_center[1]
        
        if light_bobbing_enabled:
            light_bobbing_offset = light_bobbing_amplitude * np.sin(
                2 * np.pi * light_bobbing_speed * total_animation_time
            )
            base_pos[1] += light_bobbing_offset
        
        if light_path_enabled:
            path_time = total_animation_time * light_path_speed
            path_x = light_path_scale * np.sin(path_time)
            path_z = light_path_scale * np.sin(2 * path_time) / 2
            base_pos[0] += path_x
            base_pos[2] += path_z
        
        if light_orbit_enabled or light_bobbing_enabled or light_path_enabled:
            light_position[0] = base_pos[0]
            light_position[1] = max(0.5, base_pos[1])
            light_position[2] = base_pos[2]

def apply_model_animation_transforms():
    """Apply model animation transformations to the current OpenGL matrix."""
    if not model_animation_paused:
        glRotatef(model_rotation_angle, 
                 model_rotation_axis[0], 
                 model_rotation_axis[1], 
                 model_rotation_axis[2])

def get_total_model_rotation():
    """Get the total model rotation for shadow calculations."""
    if model_animation_paused:
        return 0.0
    return model_rotation_angle

def get_total_animation_time():
    """Get the total animation time."""
    return total_animation_time

# === ANIMATION CONTROL FUNCTIONS ===

def toggle_model_animation():
    """Toggle model animation pause/resume."""
    global model_animation_paused, model_rotation_speed
    
    model_animation_paused = not model_animation_paused
    
    if not model_animation_paused and model_rotation_speed <= 0.1:
        model_rotation_speed = 30.0
    
    message = f"Model Animation: {'PAUSED' if model_animation_paused else 'PLAYING'}"
    set_status_message(message)

def toggle_light_orbit():
    """Toggle light orbital animation."""
    global light_orbit_enabled
    
    light_orbit_enabled = not light_orbit_enabled
    message = f"Light Orbit: {'ON' if light_orbit_enabled else 'OFF'}"
    set_status_message(message)

def toggle_light_bobbing():
    """Toggle light vertical bobbing animation."""
    global light_bobbing_enabled
    
    light_bobbing_enabled = not light_bobbing_enabled
    message = f"Light Bobbing: {'ON' if light_bobbing_enabled else 'OFF'}"
    set_status_message(message)

def toggle_light_path_animation():
    """Toggle light path animation (figure-8)."""
    global light_path_enabled
    
    light_path_enabled = not light_path_enabled
    message = f"Light Path: {'ON' if light_path_enabled else 'OFF'}"
    set_status_message(message)

def adjust_animation_speed(delta_speed):
    """Adjust global animation speed."""
    global animation_speed_multiplier
    
    old_speed = animation_speed_multiplier
    animation_speed_multiplier = np.clip(
        animation_speed_multiplier + delta_speed,
        min_animation_speed,
        max_animation_speed
    )
    
    message = f"Speed: {old_speed:.2f}x → {animation_speed_multiplier:.2f}x"
    set_status_message(message)

def apply_animation_preset(preset_number):
    """Apply an animation preset."""
    global current_animation_preset, model_rotation_speed, model_animation_paused
    global light_orbit_enabled, light_orbit_speed, light_bobbing_enabled, light_bobbing_speed
    global light_path_enabled, animation_speed_multiplier
    
    if preset_number not in animation_presets:
        return
    
    preset = animation_presets[preset_number]
    current_animation_preset = preset_number
    
    model_rotation_speed = preset.get('model_speed', 30.0)
    model_animation_paused = preset.get('model_paused', False)
    
    light_orbit_enabled = preset.get('light_orbit', False)
    light_orbit_speed = preset.get('light_orbit_speed', 45.0)
    light_bobbing_enabled = preset.get('light_bobbing', False)
    light_bobbing_speed = preset.get('light_bobbing_speed', 2.0)
    light_path_enabled = preset.get('light_path', False)
    
    animation_speed_multiplier = preset.get('global_speed', 1.0)
    
    message = f"Preset {preset_number}: '{preset['name']}' applied"
    set_status_message(message)

def reset_all_animations():
    """Reset all animations to default state."""
    global model_animation_paused, model_rotation_angle, model_rotation_speed
    global light_orbit_enabled, light_orbit_angle, light_bobbing_enabled, light_bobbing_offset
    global light_path_enabled, animation_speed_multiplier, total_animation_time
    global current_animation_preset
    
    model_animation_paused = False
    model_rotation_angle = 0.0
    model_rotation_speed = 30.0
    
    light_orbit_enabled = False
    light_orbit_angle = 0.0
    light_bobbing_enabled = False
    light_bobbing_offset = 0.0
    light_path_enabled = False
    
    animation_speed_multiplier = 1.0
    total_animation_time = 0.0
    current_animation_preset = 1
    
    if not animate_light:
        light_position[:3] = default_light_position[:3]
    
    message = "All animations reset to defaults"
    set_status_message(message)

def get_available_presets():
    """Get list of available animation presets."""
    return list(animation_presets.keys())

# === INTERACTIVITY FUNCTIONS ===

def toggle_lighting():
    """Toggle lighting on/off."""
    global lighting_enabled
    
    lighting_enabled = not lighting_enabled
    
    if lighting_enabled:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        message = "Lighting: ON"
    else:
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        message = "Lighting: OFF"
    
    set_status_message(message)

def toggle_wireframe():
    """Toggle between wireframe and solid rendering."""
    global wireframe_mode
    
    wireframe_mode = not wireframe_mode
    
    if wireframe_mode:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        message = "Wireframe: ON"
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        message = "Solid: ON"
    
    set_status_message(message)

def toggle_shadows():
    """Toggle shadow rendering."""
    global shadows_enabled
    
    shadows_enabled = not shadows_enabled
    message = f"Shadows: {'ON' if shadows_enabled else 'OFF'}"
    set_status_message(message)

def toggle_ground_plane():
    """Toggle ground plane visibility."""
    global ground_plane_visible
    
    ground_plane_visible = not ground_plane_visible
    message = f"Ground: {'VISIBLE' if ground_plane_visible else 'HIDDEN'}"
    set_status_message(message)

def toggle_light_animation():
    """Toggle light animation - legacy system."""
    global animate_light
    
    animate_light = not animate_light
    message = f"Legacy Light Orbit: {'ON' if animate_light else 'OFF'}"
    set_status_message(message)

def move_light(direction):
    """Move light source in specified direction - ENHANCED RESPONSIVENESS."""
    global light_position
    
    if direction == 'forward':
        light_position[2] -= light_move_speed
    elif direction == 'back':
        light_position[2] += light_move_speed
    elif direction == 'left':
        light_position[0] -= light_move_speed
    elif direction == 'right':
        light_position[0] += light_move_speed
    elif direction == 'up':
        light_position[1] += light_move_speed
    elif direction == 'down':
        light_position[1] = max(0.1, light_position[1] - light_move_speed)
    
    message = f"Light: ({light_position[0]:.1f}, {light_position[1]:.1f}, {light_position[2]:.1f})"
    set_status_message(message)

def adjust_material_shininess(change):
    """Adjust material shininess."""
    global material_shininess
    
    material_shininess = max(1.0, min(128.0, material_shininess + change))
    message = f"Shininess: {material_shininess:.0f}"
    set_status_message(message)

def reset_all_settings():
    """Reset all settings to defaults including animations."""
    global eyeX, eyeY, eyeZ, centerX, centerY, centerZ
    global camera_velocity, rotation_velocity, camera_yaw, camera_pitch, camera_distance, zoom_velocity
    global rotation_x, rotation_y, current_auto_rotation
    global lighting_enabled, shadows_enabled, ground_plane_visible, wireframe_mode, animation_paused
    global light_position, light_rotation_angle, animate_light, material_shininess
    
    # Reset camera
    eyeX, eyeY, eyeZ = 0.0, 0.0, 8.0
    centerX, centerY, centerZ = 0.0, 0.0, 0.0
    camera_velocity = np.array([0.0, 0.0, 0.0])
    rotation_velocity = np.array([0.0, 0.0])
    camera_yaw, camera_pitch = 0.0, 0.0
    camera_distance = 8.0
    zoom_velocity = 0.0
    
    # Reset model rotation
    rotation_x, rotation_y = 0.0, 0.0
    current_auto_rotation = 0.0
    
    # Reset light
    light_position = default_light_position.copy()
    light_rotation_angle = 0.0
    animate_light = False
    
    # Reset display modes
    lighting_enabled = True
    shadows_enabled = True
    ground_plane_visible = True
    animation_paused = False
    material_shininess = 32.0
    
    if wireframe_mode:
        wireframe_mode = False
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    reset_all_animations()
    
    message = "All settings reset"
    set_status_message(message)

def set_status_message(message):
    """Set a status message to display temporarily."""
    global last_action_message, last_action_time
    last_action_message = message
    last_action_time = pygame.time.get_ticks() / 1000.0

# === SHADOW SYSTEM FUNCTIONS ===

def create_shadow_matrix(light_pos, plane_point, plane_normal):
    """
    Create a 4x4 shadow projection matrix that projects geometry onto a plane.
    
    Args:
        light_pos: [x, y, z, w] - light position
        plane_point: [x, y, z] - a point on the plane
        plane_normal: [x, y, z] - normal vector of the plane
    
    Returns:
        4x4 numpy array representing the shadow matrix
    """
    normal = np.array(plane_normal)
    normal = normal / np.linalg.norm(normal)
    
    a, b, c = normal
    d = -np.dot(normal, plane_point)
    
    lx, ly, lz, lw = light_pos
    
    dot = a * lx + b * ly + c * lz + d * lw
    
    shadow_matrix = np.array([
        [dot - a * lx, -b * lx, -c * lx, -d * lx],
        [-a * ly, dot - b * ly, -c * ly, -d * ly],
        [-a * lz, -b * lz, dot - c * lz, -d * lz],
        [-a * lw, -b * lw, -c * lw, dot - d * lw]
    ], dtype=np.float32)
    
    return shadow_matrix

def apply_shadow_matrix(light_pos, ground_y=0.0):
    """
    Apply shadow projection matrix to current OpenGL matrix stack.
    
    Args:
        light_pos: [x, y, z, w] - position of light source
        ground_y: Y-coordinate of the ground plane
    """
    plane_point = [0.0, ground_y, 0.0]
    plane_normal = [0.0, 1.0, 0.0]
    
    shadow_matrix = create_shadow_matrix(light_pos, plane_point, plane_normal)
    
    glMultMatrixf(shadow_matrix.T)

def draw_ground_plane(ground_y=-3.0, ground_size=30.0, ground_color=[0.3, 0.4, 0.3, 1.0], 
                     visible=True, lighting_enabled=False):
    """Draw a simple ground plane to receive shadows."""
    if not visible:
        return
    
    was_lighting_enabled = glIsEnabled(GL_LIGHTING)
    glDisable(GL_LIGHTING)
    
    glColor4f(ground_color[0], ground_color[1], ground_color[2], ground_color[3])
    
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    
    half_size = ground_size / 2.0
    glVertex3f(-half_size, ground_y, -half_size)
    glVertex3f( half_size, ground_y, -half_size)
    glVertex3f( half_size, ground_y,  half_size)
    glVertex3f(-half_size, ground_y,  half_size)
    
    glEnd()
    
    if was_lighting_enabled and lighting_enabled:
        glEnable(GL_LIGHTING)

def draw_model_shadow(model, light_pos, ground_y=-3.0, shadow_color=[0.1, 0.1, 0.1, 0.8], 
                     rotation_x=0.0, rotation_y=0.0, enabled=True):
    """
    Draw the shadow of a 3D model projected onto the ground plane.
    
    Args:
        model: Model3D instance to draw shadow of
        light_pos: [x, y, z, w] position of light source
        ground_y: Y-level of the ground plane
        shadow_color: [r, g, b, a] color of the shadow
        rotation_x, rotation_y: Model rotations to match
        enabled: Whether shadows are enabled
    """
    if not enabled or not model or not model.is_loaded():
        return
    
    glPushMatrix()
    glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glDisable(GL_LIGHTING)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(-1.0, -1.0)
    
    glColor4f(shadow_color[0], shadow_color[1], shadow_color[2], shadow_color[3])
    
    apply_shadow_matrix(light_pos, ground_y)
    
    glRotatef(rotation_x, 1.0, 0.0, 0.0)
    glRotatef(rotation_y, 0.0, 1.0, 0.0)
    
    for face in model.faces:
        glBegin(GL_POLYGON)
        for vertex_idx in face:
            if vertex_idx < len(model.vertices):
                vertex = model.vertices[vertex_idx]
                try:
                    glVertex3f(vertex[0], vertex[1], vertex[2])
                except (IndexError, TypeError):
                    continue
        glEnd()
    
    glPopAttrib()
    glPopMatrix()

# === UTILITY FUNCTIONS ===

def check_for_file_changes():
    """Check if the script file has been modified."""
    global last_modified
    
    try:
        current_modified = os.path.getmtime(script_path)
        if last_modified == 0:
            last_modified = current_modified
            return False
        elif current_modified > last_modified:
            last_modified = current_modified
            return True
    except OSError:
        pass
    
    return False

def restart_program():
    """Restart the current program cleanly."""
    pygame.quit()
    os.execv(sys.executable, [sys.executable] + sys.argv)

# === MODEL CLASS ===

class Model3D:
    """3D Model class to encapsulate model data and rendering."""
    
    def __init__(self, filename):
        """Load a 3D model from an OBJ file."""
        self.vertices = None
        self.faces = None
        self.normals = None
        self.filename = filename
        self.load()
    
    def load(self):
        """Load the model from file."""
        vertices, faces = load_obj(self.filename)
        
        if vertices is None or faces is None:
            return False
        
        self.vertices = center_and_scale_model(vertices)
        self.faces = faces
        self.normals = calculate_face_normals(self.vertices, faces)
        
        return True
    
    def draw_basic(self):
        """Draw the model with basic rendering (no lighting)."""
        if not self.is_loaded():
            return
        
        glPushMatrix()
        glRotatef(rotation_x, 1.0, 0.0, 0.0)
        glRotatef(rotation_y, 0.0, 1.0, 0.0)
        
        for i, face in enumerate(self.faces):
            if i < len(self.normals) and len(self.normals[i]) >= 3:
                try:
                    glNormal3f(self.normals[i][0], self.normals[i][1], self.normals[i][2])
                except (IndexError, TypeError):
                    glNormal3f(0.0, 0.0, 1.0)
            
            glBegin(GL_POLYGON)
            glColor3f(0.7, 0.8, 0.9)
            
            for vertex_idx in face:
                if vertex_idx < len(self.vertices):
                    vertex = self.vertices[vertex_idx]
                    try:
                        glVertex3f(vertex[0], vertex[1], vertex[2])
                    except (IndexError, TypeError):
                        continue
            
            glEnd()
            
            glBegin(GL_LINE_LOOP)
            glColor3f(0.2, 0.3, 0.4)
            for vertex_idx in face:
                if vertex_idx < len(self.vertices):
                    vertex = self.vertices[vertex_idx]
                    try:
                        glVertex3f(vertex[0], vertex[1], vertex[2])
                    except (IndexError, TypeError):
                        continue
            glEnd()
        
        glPopMatrix()
    
    def is_loaded(self):
        """Check if the model is loaded successfully."""
        return self.vertices is not None and self.faces is not None