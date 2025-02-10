import bpy
import os
import bpy.ops
import bpy.props

# カスタムプロパティ['collider']追加
class MYADDON_OT_spawn(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_spawn"
    bl_label = "出現ポイントシンボルImport"
    bl_description = "出現ポイントのシンボルをImportします"
    bl_options = {"REGISTER", "UNDO"}

    def load_obj(self, type):
        # 重複ロード防止
        spawn_object = bpy.data.objects.get(SpawnNames.names[type][SpawnNames.PROTOTYPE])
        if spawn_object is not None:
            return {'CANCELLED'}

        addon_directory = os.path.dirname(__file__)
        relative_path = SpawnNames.names[type][SpawnNames.FILENAME]
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
        object.name = SpawnNames.names[type][SpawnNames.PROTOTYPE]

        # オブジェクトの種類を設定
        object["type"] = SpawnNames.names[type][SpawnNames.INSTANCE]

        # メモリ上には置いておくがシーンから外す
        bpy.context.collection.objects.unlink(object)
        
        return {"FINISHED"}
        
    def execute(self, context):
        #Enemyオブジェクト読み込み
        self.load_obj("Enemy")
        #Playerオブジェクト読み込み
        self.load_obj("Player")
        
        return {"FINISHED"}
             

class MYADDON_OT_create_spawn(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_spawn"
    bl_label = "出現ポイントシンボルの作成"
    bl_description = "出現ポイントのシンボルを作成します"
    bl_options = {"REGISTER", "UNDO"}

    type: bpy.props.StringProperty(name="Type", default="Player")

    def execute(self, context):
        # 読み込み済みのコピー元オブジェクトを検索
        spawn_object = bpy.data.objects.get(SpawnNames.names[self.type][SpawnNames.PROTOTYPE])

        # 読み込んでいない場合
        if spawn_object is None:
            # 読み込みオペレータを実行
            bpy.ops.myaddon.myaddon_ot_spawn('EXEC_DEFAULT')
            # 再検索
            spawn_object = bpy.data.objects.get(SpawnNames.names[self.type][SpawnNames.PROTOTYPE])

        print("出現ポイントのシンボルを作成します") 

        # Blenderでの選択を解除
        bpy.ops.object.select_all(action='DESELECT')
        # 複製元の非表示オブジェクトを複製
        object = spawn_object.copy()
        # 複製したオブジェクトを現在のシーンにリンク(出現させる)
        bpy.context.collection.objects.link(object)
        # オブジェクト名を変更
        object.name = SpawnNames.names[self.type][SpawnNames.INSTANCE]
        return {'FINISHED'}   

class MYADDON_OT_create_player_spawn(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_player_spawn"
    bl_label = "player出現ポイントシンボルの作成"
    bl_description = "player出現ポイントのシンボルを作成します"

    def execute(self, context):
        bpy.ops.myaddon.myaddon_ot_create_spawn('EXEC_DEFAULT', type = "Player")

        return {'FINISHED'}
    
class MYADDON_OT_create_enemy_spawn(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_enemy_spawn"
    bl_label = "enemy出現ポイントシンボルの作成"
    bl_description = "enemy出現ポイントのシンボルを作成します"

    def execute(self, context):
        bpy.ops.myaddon.myaddon_ot_create_spawn('EXEC_DEFAULT', type = "Enemy")

        return {'FINISHED'}
    
class SpawnNames():
    # インデックス
    PROTOTYPE = 0
    INSTANCE = 1
    FILENAME = 2

    names = {}
    # names["キー"] = (プロトタイプのオブジェクト名、量産時のオブジェクト名、リソースファイル名)
    names["Enemy"] = ("PrototypeEnemySpawn", "EnemySpawn", "needle/needle.obj")
    names["Player"] = ("PrototypePlayerSpawn", "PlayerSpawn", "Player/Player.obj")