import bpy
import math
import copy

import bpy_extras
import gpu
import gpu_extras.batch
import mathutils
import json

# 頂点引き延ばし
from .stretch_vertex import MYADDON_OT_stretch_vertex
# ICO球生成
from .create_ico_sphere import MYADDON_OT_create_ico_sphere
# シーン出力
from .export_scene import MYADDON_OT_export_scene
# カスタムプロパティ['file_name']追加
from .add_filename import MYADDON_OT_add_filename
# カスタムプロパティ['collider']追加
from .add_collider import MYADDON_OT_add_collider
# カスタムプロパティ['disabled']追加
from .is_disabled import MYADDON_OT_is_disabled
from .is_disabled import OBJECT_PT_is_disabled
from .spawn import MYADDON_OT_spawn
from .spawn import MYADDON_OT_create_spawn
from .spawn import MYADDON_OT_create_player_spawn
from .spawn import MYADDON_OT_create_enemy_spawn

#ブレンダーに登録するアドオン情報
bl_info = {
    "name": "レベルエディタ",
    "author": "Kousaku Fumimoto",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "",
    "descriptor": "レベルエディタ",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}


#アドオン有効化時コールバック
def register():
    # Blenderにクラスを登録
    for cls in classes:
        bpy.utils.register_class(cls)

    #メニューから項目を追加
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    #3Dビューに描画関数を追加
    DrawCollider.handle = bpy.types.SpaceView3D.draw_handler_add(DrawCollider.draw_collider, (), "WINDOW", "POST_VIEW")
    print("レベルエディタが有効化されました")

#アドオン無効化時コールバック
def unregister():
     #メニューから項目を削除
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)
    #3Dビューから描画関数を削除
    bpy.types.SpaceView3D.draw_handler_remove(DrawCollider.handle, "WINDOW")

    #Blenderからクラスを削除
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("レベルエディタが無効化されました")
    
#テスト実行用コード
if __name__ == "__main__":
    register()

# パネルクラス↓
# ファイル名記入
class OBJECT_PT_file_name(bpy.types.Panel):
    """オブジェクトのファイルネームパネル"""
    bl_idname = "OBJECT_PT_file_name"
    bl_label = "FileName"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    #サブメニューの描画
    def draw(self, context):
        #パネルに項目を追加
        if "file_name" in context.object:
            #すでにプロパティがあれば表示
            self.layout.prop(context.object, '["file_name"]', text=self.bl_label)
        else:
            #プロパティがなければ追加ボタンを表示
            self.layout.operator(MYADDON_OT_add_filename.bl_idname)

# コライダー追加
class OBJECT_PT_collider(bpy.types.Panel):
    bl_idname = "OBJECT_PT_collider"
    bl_label = "Collider"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    #サブメニューの描画
    def draw(self, context):
        #パネルに項目を追加
        if "collider" in context.object:
            #すでにプロパティがあれば表示
            self.layout.prop(context.object, '["collider"]', text="Type")
            self.layout.prop(context.object, '["collider_center"]', text="Center")
            self.layout.prop(context.object, '["collider_size"]', text="Size")
        else:
            #プロパティがなければ追加ボタンを表示
            self.layout.operator(MYADDON_OT_add_collider.bl_idname)

# パネルクラス↑


# コライダー描画クラス
class DrawCollider:
    #描画ハンドル
    handle = None#3Dビューに登録する描画関数
    def draw_collider():
        #頂点データ
        vertices = {"pos":[]}
        #インデックスデータ
        indices = []
        #各頂点の、オブジェクト中心からのオフセット
        offsets = [
            [-0.5,-0.5,-0.5],
            [+0.5,-0.5,-0.5],
            [-0.5,+0.5,-0.5],
            [+0.5,+0.5,-0.5],
            [-0.5,-0.5,+0.5],
            [+0.5,-0.5,+0.5],
            [-0.5,+0.5,+0.5],
            [+0.5,+0.5,+0.5],
        ]
        #立方体のX,Y,Z方向のサイズ
        size = [2,2,2]

        #現在シーンのオブジェクトリストを走査
        for object in bpy.context.scene.objects:
            #コライダープロパティがなければ描画をスキップ
            if not "collider" in object:
                continue

            #中心点、サイズの変数を宣言
            center = mathutils.Vector((0,0,0))
            size = mathutils.Vector((2,2,2))

            #プロパティから値を取得
            center[0]=object["collider_center"][0]
            center[1]=object["collider_center"][1]
            center[2]=object["collider_center"][2]
            size[0]=object["collider_size"][0]
            size[1]=object["collider_size"][1]
            size[2]=object["collider_size"][2]

            #追加前の頂点数
            start = len(vertices["pos"])

            #boxの8頂点分回す
            for offset in offsets:
                #オブジェクトの中心座標をコピー
                pos = copy.copy(center)
                #中心点を基準に各頂点ごとにずらす
                pos[0]+=offset[0]*size[0]
                pos[1]+=offset[1]*size[1]
                pos[2]+=offset[2]*size[2]
                #ローカル座標からワールド座標に変換
                pos = object.matrix_world @ pos
                #頂点データリストに座標を追加
                vertices['pos'].append(pos)

                #前面を構成する辺の頂点インデックス
                indices.append([start+0, start+1])
                indices.append([start+2, start+3])
                indices.append([start+0, start+2])
                indices.append([start+1, start+3])
                #奥面を構成する辺の頂点インデックス
                indices.append([start+4, start+5])
                indices.append([start+6, start+7])
                indices.append([start+4, start+6])
                indices.append([start+5, start+7])
                #前と頂点をつなぐ辺の頂点インデックス
                indices.append([start+0, start+4])
                indices.append([start+1, start+5])
                indices.append([start+2, start+6])
                indices.append([start+3, start+7])

        #ビルドインのシェーダを取得
        shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
        #バッチを作成(引数:シェーダ、トポロジー、頂点データ、インデックスデータ)
        batch = gpu_extras.batch.batch_for_shader(shader, "LINES", vertices, indices = indices)
        #シェーダのパラメータ設定
        color = [0.5, 1.0, 1.0, 1.0]
        shader.bind()
        shader.uniform_float("color", color)
        #描画
        batch.draw(shader)


# トップバーの拡張メニュー
class TOPBAR_MT_my_menu(bpy.types.Menu):
    #Blenderがクラスを識別するための固有文字列
    bl_idname = "TOPBAR_MT_my_menu"
    #メニューのラベルとして表示される文字列
    bl_label = "MyMenu"
    #著者表示用の文字列
    bl_description = "拡張メニュー by " + bl_info["author"]

    # サブメニューの描画
    def draw(self, context):
        #トップバーのエディターメニューに項目を追加
        self.layout.operator(MYADDON_OT_stretch_vertex.bl_idname, text=MYADDON_OT_stretch_vertex.bl_label)
        self.layout.operator(MYADDON_OT_create_ico_sphere.bl_idname, text=MYADDON_OT_create_ico_sphere.bl_label)
        self.layout.operator(MYADDON_OT_export_scene.bl_idname, text=MYADDON_OT_export_scene.bl_label)
        self.layout.operator(MYADDON_OT_create_player_spawn.bl_idname, text=MYADDON_OT_create_player_spawn.bl_label)
        self.layout.operator(MYADDON_OT_create_enemy_spawn.bl_idname, text=MYADDON_OT_create_enemy_spawn.bl_label)
        
    # 既存のメニューにサブメニューを追加
    def submenu(self, context):
        # ID指定でサブメニューを追加
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# Blenderに登録するクラスリスト
classes = (
    #シーンの出力
    MYADDON_OT_export_scene,
    #ICO球の生成
    MYADDON_OT_create_ico_sphere,
    #Cubeの頂点を伸ばす
    MYADDON_OT_stretch_vertex,
    #カスタムプロパティ_ファイル名
    MYADDON_OT_add_filename,
    #カスタムプロパティ_コライダー
    MYADDON_OT_add_collider,
    #カスタムプロパティ_無効フラグ
    MYADDON_OT_is_disabled,
    MYADDON_OT_spawn,
    MYADDON_OT_create_spawn,
    MYADDON_OT_create_player_spawn,
    MYADDON_OT_create_enemy_spawn,
    #パネルクラス_ファイル名
    OBJECT_PT_file_name,
    #パネルクラス_コライダー
    OBJECT_PT_collider,
    #パネルクラス_無効フラグ
    OBJECT_PT_is_disabled,
    #トップバーの拡張メニュー
    TOPBAR_MT_my_menu,
)