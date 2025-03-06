import bpy
import pandas as pd
import os
import math
import gc

def merge_glb_files(file1_path, output_path, obj_models, obj_locations, obj_rotations):
    mapfile_path = "../3d_model/"
    # 모든 오브젝트 선택
    bpy.ops.object.select_all(action='SELECT')
    # 선택된 모든 오브젝트 삭제
    bpy.ops.object.delete(use_global=False)

    # 첫 번째 GLB 파일 불러오기
    bpy.ops.import_scene.gltf(filepath=file1_path)

    for iter in range(len(obj_locations)):
        bpy.ops.object.select_all(action='DESELECT')

        # 두 번째 GLB 파일 불러오기
        glb_file_2 = mapfile_path + 'Vehicle/' + obj_models[iter] + '.glb'
        bpy.ops.import_scene.gltf(filepath=glb_file_2)

        # 오브젝트를 이동
        for obj in bpy.context.selected_objects:
            obj.location = obj_locations[iter]
            bpy.ops.transform.rotate(value=math.radians(obj_rotations[iter][0]), orient_axis='Z')
            bpy.ops.transform.rotate(value=math.radians(obj_rotations[iter][1]), orient_axis='X')
            bpy.ops.transform.rotate(value=math.radians(obj_rotations[iter][2]), orient_axis='Y')

    # 결합된 파일을 새로운 GLB 파일로 내보내기
    output_glb_path = output_path
    bpy.ops.export_scene.gltf(
            filepath=output_path,
            export_format='GLB',           # GLB 포맷으로 저장
        )

    print(f"GLB 파일이 성공적으로 결합되어 {output_glb_path}에 저장되었습니다.")
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    bpy.ops.wm.quit_blender()

def main(datapath, filename, modelname, output_file):
    orgfile = "../3d_model/" + modelname
    dirpath = datapath + "/_out_gps/"

    file_path = os.path.join(dirpath, filename)
    
    # 파일 읽기
    df = pd.read_csv(file_path)
    num_rows, _ = df.shape
    models = [ df.iloc[iter, 1:2].values[0] for iter in range(num_rows)]
    locations = [[df.iloc[iter, 2:3].values[0], df.iloc[iter, 3:4].values[0], df.iloc[iter, 4:5].values[0]] for iter in range(num_rows)]
    rotations = [[df.iloc[iter, 5:6].values[0], df.iloc[iter, 6:7].values[0], df.iloc[iter, 7:8].values[0]] for iter in range(num_rows)]
    merge_glb_files(orgfile, output_file, models, locations, rotations)
    # Python 가비지 컬렉션을 수동으로 호출
    gc.collect()
    return