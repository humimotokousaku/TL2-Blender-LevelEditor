import bpy
import os
import bpy.ops

# カスタムプロパティ['collider']追加
class MYADDON_OT_spawn(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_spawn"
    bl_label = "出現ポイントシンボルImport"
    bl_description = "出現ポイントのシンボルをImportします"
    bl_options = {"REGISTER", "UNDO"}
    prototype_object_name = "PrototypePlayerSpawn"
    object_name = "PlayerSpawn"

    def execute(self, context):
        print("出現ポイントのシンボルをImportします")

        # 重複ロード防止
        spawn_object = bpy.data.objects.get(MYADDON_OT_spawn.prototype_object_name)
        if spawn_object is not None:
            return {'CANCELLED'}

        addon_directory = os.path.dirname(__file__)
        relative_path = "player/player.obj"
        full_path = os.path.join(addon_directory, relative_path)
        # オブジェクトをインポート
        bpy.ops.wm.obj_import('EXEC_DEFAULT',
            filepath=full_path, display_type='THUMBNAIL',
            forward_axis='Z', up_axis='Y')
        
        # 回転を適用
        bpy.ops.object.transform_apply(location=False,
            rotation=True, scale=False,properties=False,
            isolate_users=False)
        
        #アクティブなオブジェクトを取得
        object = bpy.context.active_object
        #オブジェクト名を変更
        object.name = MYADDON_OT_spawn.prototype_object_name

        # オブジェクトの種類を設定
        object["type"] = MYADDON_OT_spawn.object_name

        # メモリ上には置いておくがシーンから外す
        bpy.context.collection.objects.unlink(object)
        
        return {"FINISHED"}

class MYADDON_OT_create_spawn(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_spawn"
    bl_label = "出現ポイントシンボルの作成"
    bl_description = "出現ポイントのシンボルを作成します"
    bl_options = {"REGISTER", "UNDO"}
    prototype_object_name = "PrototypePlayerSpawn"
    object_name = "PlayerSpawn"

    def execute(self, context):
        # 読み込み済みのコピー元オブジェクトを検索
        spawn_object = bpy.data.objects.get(MYADDON_OT_spawn.prototype_object_name)

        # 読み込んでいない場合
        if spawn_object is None:
            # 読み込みオペレータを実行
            bpy.ops.myaddon.myaddon_ot_spawn('EXEC_DEFAULT')
            # 再検索
            spawn_object = bpy.data.objects.get(MYADDON_OT_spawn.prototype_object_name)

        print("出現ポイントのシンボルを作成します") 

        # Blenderでの選択を解除
        bpy.ops.object.select_all(action='DESELECT')
        # 複製元の非表示オブジェクトを複製
        object = spawn_object.copy()
        # 複製したオブジェクトを現在のシーンにリンク(出現させる)
        bpy.context.collection.objects.link(object)
        # オブジェクト名を変更
        object.name = MYADDON_OT_create_spawn.object_name

        return {'FINISHED'}               