#!/usr/bin/env python3
"""
coloring_utils.py - Advanced Coloring and Material System
Computer Graphics Major Project - Step 7

Features:
- Position-based USS Enterprise part identification
- Angle-based dynamic coloring using face normals and dot products
- Material variation system with different properties per part
- Performance optimizations with caching strategies
- Multiple coloring modes and color schemes
"""

import numpy as np
from OpenGL.GL import *
import time

# === COLORING SYSTEM CONFIGURATION ===

# Coloring modes
COLORING_MODE_SOLID = 0
COLORING_MODE_POSITION = 1      # Position-based part coloring
COLORING_MODE_ANGLE = 2         # Angle-based brightness
COLORING_MODE_MIXED = 3         # Position + Angle combined
COLORING_MODE_ANIMATED = 4      # Animated effects

current_coloring_mode = COLORING_MODE_POSITION

# === USS ENTERPRISE PART IDENTIFICATION ===

USS_ENTERPRISE_PARTS = {
    'bridge': {
        'name': 'Bridge/Command Section',
        'condition': lambda pos: pos[1] > 1.0 and (pos[0]**2 + pos[2]**2) < 0.64,
        'base_color': [0.9, 0.9, 0.95],
        'material': {
            'ambient': [0.4, 0.4, 0.45, 1.0],
            'diffuse': [0.8, 0.8, 0.9, 1.0],
            'specular': [1.0, 1.0, 1.0, 1.0],
            'shininess': 128.0
        }
    },
    'saucer_section': {
        'name': 'Primary Hull (Saucer)',
        'condition': lambda pos: pos[1] > -0.5 and pos[1] <= 2.0 and (pos[0]**2 + pos[2]**2) < 6.25,
        'base_color': [0.7, 0.8, 0.9],
        'material': {
            'ambient': [0.3, 0.35, 0.4, 1.0],
            'diffuse': [0.7, 0.75, 0.85, 1.0],
            'specular': [0.9, 0.9, 0.95, 1.0],
            'shininess': 64.0
        }
    },
    'nacelles': {
        'name': 'Warp Nacelles',
        'condition': lambda pos: abs(pos[0]) > 2.0 and pos[1] > -1.0 and pos[1] < 1.5,
        'base_color': [0.5, 0.6, 0.9],
        'material': {
            'ambient': [0.2, 0.25, 0.4, 1.0],
            'diffuse': [0.5, 0.6, 0.85, 1.0],
            'specular': [0.95, 0.95, 1.0, 1.0],
            'shininess': 96.0
        }
    },
    'pylons': {
        'name': 'Nacelle Pylons',
        'condition': lambda pos: abs(pos[0]) > 0.8 and abs(pos[0]) < 2.0 and pos[1] > -0.5 and pos[1] < 0.5,
        'base_color': [0.6, 0.75, 0.8],
        'material': {
            'ambient': [0.2, 0.25, 0.3, 1.0],
            'diffuse': [0.55, 0.65, 0.75, 1.0],
            'specular': [0.7, 0.75, 0.8, 1.0],
            'shininess': 32.0
        }
    },
    'engineering_hull': {
        'name': 'Secondary Hull (Engineering)',
        'condition': lambda pos: pos[1] > -2.0 and pos[1] < 0.5 and pos[2] > -1.0 and pos[2] < 2.0 and abs(pos[0]) < 1.5,
        'base_color': [0.6, 0.7, 0.8],
        'material': {
            'ambient': [0.25, 0.3, 0.35, 1.0],
            'diffuse': [0.6, 0.7, 0.8, 1.0],
            'specular': [0.8, 0.85, 0.9, 1.0],
            'shininess': 48.0
        }
    }
}

# Part identification priority order
PART_CHECK_ORDER = ['bridge', 'nacelles', 'pylons', 'engineering_hull', 'saucer_section']

# Color schemes for different moods
COLOR_SCHEMES = {
    'starfleet': {
        'bridge': [0.9, 0.9, 0.95],
        'saucer_section': [0.7, 0.8, 0.9],
        'engineering_hull': [0.6, 0.7, 0.8],
        'nacelles': [0.5, 0.6, 0.9],
        'pylons': [0.6, 0.75, 0.8]
    },
    'battle': {
        'bridge': [1.0, 0.8, 0.0],
        'saucer_section': [0.8, 0.3, 0.3],
        'engineering_hull': [0.4, 0.4, 0.4],
        'nacelles': [0.9, 0.1, 0.1],
        'pylons': [0.3, 0.3, 0.3]
    },
    'exploration': {
        'bridge': [0.9, 0.9, 0.1],
        'saucer_section': [0.2, 0.8, 0.3],
        'engineering_hull': [0.1, 0.6, 0.7],
        'nacelles': [0.8, 0.2, 0.9],
        'pylons': [0.1, 0.5, 0.2]
    }
}

current_color_scheme = 'starfleet'

# Performance optimization caches
face_parts_cache = {}
face_centers_cache = {}
face_normals_cache = {}
face_colors_cache = {}
face_materials_cache = {}

cache_initialized = False

# Reduced update frequencies for performance
color_update_frequency = 0.1
material_update_frequency = 0.2

# Animation state
animation_time = 0.0
last_update_time = 0.0
last_color_cache_update = 0.0
last_material_cache_update = 0.0

# === PART IDENTIFICATION ===

def identify_part_by_position(position):
    """
    Identify USS Enterprise part based on 3D position using geometric rules.
    
    Args:
        position: numpy array [x, y, z] coordinates
    
    Returns:
        String key identifying the part
    """
    if not isinstance(position, np.ndarray):
        position = np.array(position)
    
    for part_name in PART_CHECK_ORDER:
        part_info = USS_ENTERPRISE_PARTS[part_name]
        if part_info['condition'](position):
            return part_name
    
    return 'saucer_section'

def calculate_face_center_enhanced(vertices, face):
    """Calculate the center point of a face using vectorized operations."""
    if not face or len(face) == 0:
        return np.array([0.0, 0.0, 0.0])
    
    try:
        valid_indices = [idx for idx in face if idx < len(vertices)]
        if not valid_indices:
            return np.array([0.0, 0.0, 0.0])
        
        face_vertices = vertices[valid_indices]
        return np.mean(face_vertices, axis=0)
    except (IndexError, TypeError):
        return np.array([0.0, 0.0, 0.0])

def precompute_face_data_enhanced(model):
    """
    Pre-compute all face centers, parts, and normals for optimal performance.
    Call this once after model loading.
    """
    global face_parts_cache, face_centers_cache, face_normals_cache, cache_initialized
    global face_colors_cache, face_materials_cache
    
    if not model or not hasattr(model, 'faces') or not hasattr(model, 'vertices'):
        return False
    
    # Clear all caches
    face_parts_cache.clear()
    face_centers_cache.clear()
    face_normals_cache.clear()
    face_colors_cache.clear()
    face_materials_cache.clear()
    
    num_faces = len(model.faces)
    centers = np.zeros((num_faces, 3))
    
    for i, face in enumerate(model.faces):
        # Calculate face center
        center = calculate_face_center_enhanced(model.vertices, face)
        centers[i] = center
        face_centers_cache[i] = center
        
        # Identify part based on position
        part_name = identify_part_by_position(center)
        face_parts_cache[i] = part_name
        
        # Cache normal if available
        if hasattr(model, 'normals') and i < len(model.normals):
            face_normals_cache[i] = model.normals[i]
        else:
            face_normals_cache[i] = np.array([0.0, 0.0, 1.0])
    
    cache_initialized = True
    
    # Pre-populate initial color and material caches
    populate_initial_caches()
    
    return True

def populate_initial_caches():
    """Pre-populate color and material caches for initial performance boost."""
    global face_colors_cache, face_materials_cache
    
    scheme = COLOR_SCHEMES.get(current_color_scheme, COLOR_SCHEMES['starfleet'])
    
    for face_index in face_parts_cache.keys():
        part_name = face_parts_cache[face_index]
        
        # Pre-cache base colors
        base_color = scheme.get(part_name, [0.7, 0.8, 0.9])
        face_colors_cache[face_index] = base_color
        
        # Pre-cache materials
        if part_name in USS_ENTERPRISE_PARTS:
            face_materials_cache[face_index] = USS_ENTERPRISE_PARTS[part_name]['material']

# === COLORING FUNCTIONS ===

def batch_update_color_cache():
    """Batch update color cache for all faces at reduced frequency."""
    global face_colors_cache, last_color_cache_update, animation_time
    
    current_time = time.time()
    
    if current_time - last_color_cache_update < color_update_frequency:
        return
    
    last_color_cache_update = current_time
    
    if not cache_initialized:
        return
    
    if current_coloring_mode == COLORING_MODE_ANIMATED:
        animation_time += color_update_frequency
    
    scheme = COLOR_SCHEMES.get(current_color_scheme, COLOR_SCHEMES['starfleet'])
    
    if current_coloring_mode == COLORING_MODE_SOLID:
        solid_color = [0.7, 0.8, 0.9]
        for face_index in face_parts_cache.keys():
            face_colors_cache[face_index] = solid_color
            
    elif current_coloring_mode == COLORING_MODE_POSITION:
        for face_index in face_parts_cache.keys():
            part_name = face_parts_cache[face_index]
            face_colors_cache[face_index] = scheme.get(part_name, [0.7, 0.8, 0.9])
            
    elif current_coloring_mode == COLORING_MODE_ANGLE:
        batch_calculate_angle_colors()
        
    elif current_coloring_mode == COLORING_MODE_MIXED:
        batch_calculate_mixed_colors(scheme)
        
    elif current_coloring_mode == COLORING_MODE_ANIMATED:
        batch_calculate_animated_colors(scheme)

def batch_calculate_angle_colors():
    """Batch calculate angle-based colors using vectorized operations."""
    view_direction = np.array([0.0, 0.0, 1.0])
    
    for face_index in face_normals_cache.keys():
        face_normal = face_normals_cache[face_index]
        
        normal = np.array(face_normal)
        normal_length = np.linalg.norm(normal)
        if normal_length > 0:
            normal = normal / normal_length
        
        dot_product = np.dot(normal, view_direction)
        brightness = 0.2 + 0.8 * max(0.0, dot_product)
        
        face_colors_cache[face_index] = [brightness, brightness, brightness]

def batch_calculate_mixed_colors(scheme, mix_factor=0.6):
    """Batch calculate mixed colors (position + angle) using vectorized operations."""
    view_direction = np.array([0.0, 0.0, 1.0])
    
    for face_index in face_parts_cache.keys():
        if face_index not in face_normals_cache:
            face_colors_cache[face_index] = [0.7, 0.8, 0.9]
            continue
        
        part_name = face_parts_cache[face_index]
        part_color = np.array(scheme.get(part_name, [0.7, 0.8, 0.9]))
        
        face_normal = face_normals_cache[face_index]
        normal = np.array(face_normal)
        normal_length = np.linalg.norm(normal)
        if normal_length > 0:
            normal = normal / normal_length
        
        dot_product = np.dot(normal, view_direction)
        brightness = 0.3 + 0.7 * max(0.0, dot_product)
        
        final_color = part_color * (mix_factor + (1.0 - mix_factor) * brightness)
        final_color = np.clip(final_color, 0.0, 1.0)
        
        face_colors_cache[face_index] = final_color.tolist()

def batch_calculate_animated_colors(scheme):
    """Batch calculate animated colors with reduced frequency updates."""
    for face_index in face_parts_cache.keys():
        part_name = face_parts_cache[face_index]
        base_color = np.array(scheme.get(part_name, [0.7, 0.8, 0.9]))
        
        # Different animation patterns for different parts
        if part_name == 'nacelles':
            pulse = 1.0 + 0.2 * np.sin(animation_time * 4.0)
            color_shift = np.array([0.1, 0.0, 0.2]) * np.sin(animation_time * 2.0)
        elif part_name == 'bridge':
            pulse = 1.0 + 0.1 * np.sin(animation_time * 1.5)
            color_shift = np.array([0.05, 0.05, 0.0]) * np.sin(animation_time * 0.8)
        elif part_name == 'engineering_hull':
            pulse = 1.0 + 0.15 * np.sin(animation_time * 2.5)
            color_shift = np.array([0.0, 0.08, 0.08]) * np.sin(animation_time * 1.2)
        else:
            pulse = 1.0 + 0.05 * np.sin(animation_time * 1.0)
            color_shift = np.array([0.0, 0.0, 0.0])
        
        final_color = (base_color + color_shift) * pulse
        final_color = np.clip(final_color, 0.0, 1.0)
        
        face_colors_cache[face_index] = final_color.tolist()

def batch_update_material_cache():
    """Batch update material cache at reduced frequency."""
    global face_materials_cache, last_material_cache_update
    
    current_time = time.time()
    
    if current_time - last_material_cache_update < material_update_frequency:
        return
    
    last_material_cache_update = current_time
    
    if not cache_initialized:
        return
    
    for face_index in face_parts_cache.keys():
        part_name = face_parts_cache[face_index]
        if part_name in USS_ENTERPRISE_PARTS:
            face_materials_cache[face_index] = USS_ENTERPRISE_PARTS[part_name]['material']

# === MAIN INTERFACE FUNCTIONS ===

def apply_enhanced_face_coloring(face_index, lighting_enabled=True):
    """
    Main function to apply enhanced coloring to a face using cached values.
    
    Args:
        face_index: Index of the face in the model
        lighting_enabled: Whether OpenGL lighting is enabled
    """
    # Update caches at reduced frequency (not every frame)
    if face_index == 0:
        batch_update_color_cache()
        if lighting_enabled:
            batch_update_material_cache()
    
    # Apply cached material properties
    if lighting_enabled and face_index in face_materials_cache:
        material = face_materials_cache[face_index]
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, material['ambient'])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, material['diffuse'])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, material['specular'])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, material['shininess'])
    
    # Apply cached color
    if face_index in face_colors_cache:
        color = face_colors_cache[face_index]
        glColor3f(color[0], color[1], color[2])
    else:
        glColor3f(0.7, 0.8, 0.9)

# === CONTROL FUNCTIONS ===

def cycle_coloring_mode():
    """Cycle through enhanced coloring modes with cache invalidation."""
    global current_coloring_mode, last_color_cache_update
    
    current_coloring_mode = (current_coloring_mode + 1) % 5
    
    # Force immediate cache update for new mode
    last_color_cache_update = 0.0
    
    mode_names = [
        "Solid Color",
        "Position-Based Parts",
        "Angle-Based Brightness", 
        "Mixed (Position + Angle)",
        "Animated Effects"
    ]
    
    mode_name = mode_names[current_coloring_mode]
    
    return mode_name

def set_color_scheme_enhanced(scheme_name):
    """Set color scheme with enhanced feedback and cache invalidation."""
    global current_color_scheme, last_color_cache_update
    
    if scheme_name not in COLOR_SCHEMES:
        return False
    
    current_color_scheme = scheme_name
    
    # Force immediate cache update for new scheme
    last_color_cache_update = 0.0
    
    return True

def get_enhanced_status():
    """Get current enhanced coloring system status."""
    mode_names = [
        "Solid Color",
        "Position-Based Parts",
        "Angle-Based Brightness", 
        "Mixed (Position + Angle)",
        "Animated Effects"
    ]
    
    return {
        'mode': mode_names[current_coloring_mode],
        'mode_index': current_coloring_mode,
        'scheme': current_color_scheme,
        'cache_initialized': cache_initialized,
        'cached_faces': len(face_parts_cache),
        'cached_colors': len(face_colors_cache),
        'cached_materials': len(face_materials_cache),
        'animation_time': animation_time,
        'color_update_freq': color_update_frequency,
        'material_update_freq': material_update_frequency
    }

def clear_enhanced_cache():
    """Clear all caches (call when model changes)."""
    global face_parts_cache, face_centers_cache, face_normals_cache, cache_initialized
    global face_colors_cache, face_materials_cache
    
    face_parts_cache.clear()
    face_centers_cache.clear()
    face_normals_cache.clear()
    face_colors_cache.clear()
    face_materials_cache.clear()
    cache_initialized = False

def print_enhanced_coloring_help():
    """Print help for the enhanced coloring system."""
    status = get_enhanced_status()
    
    print("\n" + "="*85)
    print("Advanced Coloring System - Performance Enhanced")
    print("="*85)
    
    print("\nPERFORMANCE OPTIMIZATIONS:")
    print("  • Color calculations cached and updated at 10Hz instead of 60Hz")
    print("  • Material properties batch-processed and cached at 5Hz")
    print("  • Vectorized numpy operations for angle calculations")
    print("  • Pre-allocated arrays for batch processing")
    print("  • Smart cache invalidation on mode/scheme changes")
    
    print("\nENHANCED COLORING MODES:")
    print("  M - Cycle through enhanced coloring modes")
    print("    • Solid Color           - Single color for entire model")
    print("    • Position-Based Parts  - USS Enterprise parts by 3D position")
    print("    • Angle-Based Brightness- Face brightness by normal angles")
    print("    • Mixed                 - Position-based colors + angle-based brightness")
    print("    • Animated Effects      - Position-based parts with pulsing animations")
    
    print("\nCOLOR SCHEMES:")
    print("  Ctrl+1 - Starfleet (classic Federation blue-gray)")
    print("  Ctrl+2 - Battle (dramatic red alert colors)")
    print("  Ctrl+3 - Exploration (vibrant green/purple/cyan)")
    
    print("\nUSS ENTERPRISE PARTS (Position-Based):")
    for part_name, part_info in USS_ENTERPRISE_PARTS.items():
        scheme = COLOR_SCHEMES[current_color_scheme]
        color = scheme.get(part_name, [0.7, 0.8, 0.9])
        print(f"  {part_info['name']}: RGB({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f})")
    
    print(f"\nCURRENT STATUS:")
    print(f"  Coloring Mode:         {status['mode']}")
    print(f"  Color Scheme:          {status['scheme']}")
    print(f"  Cache Initialized:     {'YES' if status['cache_initialized'] else 'NO'}")
    print(f"  Cached Faces:          {status['cached_faces']}")
    print(f"  Cached Colors:         {status['cached_colors']}")
    print(f"  Cached Materials:      {status['cached_materials']}")
    
    print("\nTECHNICAL FEATURES:")
    print("  • Position-based part identification using 3D coordinates")
    print("  • Angle-based brightness using face normal dot products")
    print("  • Mixed mode combines position colors with angle brightness")
    print("  • Per-part material properties for realistic lighting")
    print("  • Pre-computed face data with smart caching")
    print("  • Batch processing with vectorized operations")
    print("  • Multiple dramatic color schemes")
    
    print("="*85 + "\n")

# === COMPATIBILITY FUNCTIONS ===

def apply_face_coloring(vertices, face, face_index, normal, light_position=[5.0, 5.0, 5.0]):
    """Backward compatibility wrapper."""
    apply_enhanced_face_coloring(face_index, True)

def cycle_coloring_mode_old():
    """Backward compatibility wrapper."""
    return cycle_coloring_mode()

def set_color_scheme(scheme_name):
    """Backward compatibility wrapper."""
    return set_color_scheme_enhanced(scheme_name)

# === DEBUGGING FUNCTIONS ===

def debug_part_identification(model):
    """Debug function to analyze how parts are being identified."""
    if not cache_initialized or not face_parts_cache:
        return
    
    # Count parts
    part_counts = {}
    for part_name in face_parts_cache.values():
        part_counts[part_name] = part_counts.get(part_name, 0) + 1
    
    # Print statistics - simplified for final version
    total_faces = len(face_parts_cache)
    if total_faces > 0:
        print(f"Face data computed for {total_faces} faces")
        for part_name, count in part_counts.items():
            part_display_name = USS_ENTERPRISE_PARTS[part_name]['name']
            print(f"  {part_display_name}: {count} faces")

def get_performance_stats():
    """Get performance statistics for monitoring."""
    return {
        'color_cache_size': len(face_colors_cache),
        'material_cache_size': len(face_materials_cache),
        'face_cache_size': len(face_parts_cache),
        'cache_initialized': cache_initialized
    }