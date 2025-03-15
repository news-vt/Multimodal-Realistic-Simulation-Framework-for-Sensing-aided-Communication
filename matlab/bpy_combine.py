import bpy
import pandas as pd
import os
import math
import gc

def merge_glb_files(file1_path, output_path, obj_models, obj_locations, obj_rotations):
    # Define the path to the 3D model directory
    mapfile_path = "../3d_model/"
    
    # Select all objects in the Blender scene
    bpy.ops.object.select_all(action='SELECT')
    # Delete all selected objects
    bpy.ops.object.delete(use_global=False)

    # Import the first GLB file into the Blender scene
    bpy.ops.import_scene.gltf(filepath=file1_path)

    # Iterate through the list of object locations, models, and rotations
    for iter in range(len(obj_locations)):
        # Deselect all objects in the scene
        bpy.ops.object.select_all(action='DESELECT')

        # Import the next GLB file (e.g., a vehicle model)
        glb_file_2 = mapfile_path + 'Vehicle/' + obj_models[iter] + '.glb'
        bpy.ops.import_scene.gltf(filepath=glb_file_2)

        # Move and rotate the imported objects based on the provided location and rotation
        for obj in bpy.context.selected_objects:
            obj.location = obj_locations[iter]
            bpy.ops.transform.rotate(value=math.radians(obj_rotations[iter][0]), orient_axis='Z')  # Rotate around Z-axis
            bpy.ops.transform.rotate(value=math.radians(obj_rotations[iter][1]), orient_axis='X')  # Rotate around X-axis
            bpy.ops.transform.rotate(value=math.radians(obj_rotations[iter][2]), orient_axis='Y')  # Rotate around Y-axis

    # Export the combined objects as a new GLB file
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',  # Save in GLB format
    )

    print(f"GLB file successfully merged and saved to {output_path}.")
    
    # Clean up orphaned data in Blender to free memory
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    
    # Quit Blender after processing
    bpy.ops.wm.quit_blender()

def main(datapath, filename, modelname, output_file):
    # Define the path to the original GLB file
    orgfile = "../3d_model/" + modelname
    # Define the directory path for the input data
    dirpath = datapath + "/_out_gps/"

    # Construct the full path to the input CSV file
    file_path = os.path.join(dirpath, filename)
    
    # Read the CSV file containing object data
    df = pd.read_csv(file_path)
    num_rows, _ = df.shape  # Get the number of rows in the CSV file

    # Extract object models, locations, and rotations from the CSV file
    models = [df.iloc[iter, 1:2].values[0] for iter in range(num_rows)]
    locations = [[df.iloc[iter, 2:3].values[0], df.iloc[iter, 3:4].values[0], df.iloc[iter, 4:5].values[0]] for iter in range(num_rows)]
    rotations = [[df.iloc[iter, 5:6].values[0], df.iloc[iter, 6:7].values[0], df.iloc[iter, 7:8].values[0]] for iter in range(num_rows)]

    # Call the function to merge GLB files
    merge_glb_files(orgfile, output_file, models, locations, rotations)
    
    # Manually invoke Python's garbage collector to free memory
    gc.collect()
    return