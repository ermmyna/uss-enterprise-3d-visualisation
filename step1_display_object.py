#!/usr/bin/env python3
"""
object.py - Step 1: Basic 3D Model Display
Computer Graphics Major Project

Features:
- Load and display OBJ files
- Basic mouse rotation
- Hot reload for development
- Simple orthographic/perspective projection

Controls:
- Mouse drag - Rotate model
- R - Manual restart
- H - Help
- Q/Escape - Quit
"""

import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Import shared utilities
from graphics_utils import *

# Global model instance
model = None

def init_opengl():
    """Initialize OpenGL settings and load the 3D model."""
    global model
    
    # Set background color to black
    glClearColor(0.0, 0.0, 0.0, 1.0)
    
    # Enable depth testing and smooth shading
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    
    # Set up viewport
    glViewport(0, 0, window_width, window_height)
    
    # Set up perspective projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect_ratio = window_width / window_height
    gluPerspective(45.0, aspect_ratio, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
    # Load the USS Enterprise model
    model = Model3D("USS_Enterprise_grayscale.obj")
    if not model.is_loaded():
        print("Failed to load model. Exiting...")
        return False
    
    return True

def render():
    """Main rendering function."""
    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Reset modelview matrix
    glLoadIdentity()
    
    # Set up basic camera position
    gluLookAt(0.0, 0.0, 6.0,    # Camera position
              0.0, 0.0, 0.0,    # Look at origin
              0.0, 1.0, 0.0)    # Up vector
    
    # Apply mouse rotations
    glRotatef(rotation_x, 1.0, 0.0, 0.0)
    glRotatef(rotation_y, 0.0, 1.0, 0.0)
    
    # Draw the model
    if model:
        model.draw_basic()
    
    # Update display
    pygame.display.flip()

def handle_events():
    """Handle pygame events."""
    global rotation_x, rotation_y, mouse_last_x, mouse_last_y, mouse_dragging
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_r:
                print("🔄 Manual refresh - restarting program...")
                restart_program()
            elif event.key == pygame.K_h:
                print_help()
        
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
                
                rotation_y += dx * 0.5
                rotation_x += dy * 0.5
                
                mouse_last_x, mouse_last_y = x, y
    
    return True

def print_help():
    """Print help information."""
    print("\n=== 🚀 USS Enterprise 3D Viewer - Step 1: Basic Display ===")
    print("BASIC CONTROLS:")
    print("  Mouse drag - Rotate model")
    print("  R - Manual restart (hot reload)")
    print("  H - Show this help")
    print("  Q/Escape - Quit")
    print("\nFEATURES:")
    print("  ✅ OBJ file loading")
    print("  ✅ Basic 3D rendering")
    print("  ✅ Mouse rotation")
    print("  ✅ Hot reload for development")
    print("\nDEVELOPMENT:")
    print("  The program automatically detects file changes and restarts!")
    print("  Just save this file after making changes.")
    print("========================================\n")

def main():
    """Main function."""
    try:
        # Initialize pygame
        pygame.init()
        
        # Set up display
        pygame.display.set_mode((window_width, window_height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("USS Enterprise - Step 1: Basic 3D Display")
        
        # Initialize OpenGL and load model
        if not init_opengl():
            print("Failed to initialize. Exiting...")
            return
        
        # Print instructions
        print("\n🚀 === USS Enterprise 3D Viewer - Step 1: Basic Display ===")
        print("✨ HOT RELOAD ENABLED - Automatically restarts when you save changes!")
        print("\nControls:")
        print("  Mouse drag - Rotate the USS Enterprise")
        print("  'R' - Manual restart")
        print("  'H' - Show help")
        print("  'Q' or Escape - Quit")
        print("\n💡 Development Tip:")
        print("   Save this file after making changes - auto-restart!")
        print("\nThe USS Enterprise should appear in the center. Drag to rotate!\n")
        
        # Main loop
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Check for file changes every 30 frames
            global check_reload_timer
            check_reload_timer += 1
            if check_reload_timer >= 30:
                check_reload_timer = 0
                if check_for_file_changes():
                    restart_program()
            
            # Handle events
            running = handle_events()
            
            # Render scene
            render()
            
            # 60 FPS
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