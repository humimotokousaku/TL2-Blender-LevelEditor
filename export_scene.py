import bpy
import math
import bpy_extras
import json

# シーン出力
class MYADDON_OT_export_scene(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    bl_descriptor = "シーン情報をExportします"
    #出力するファイルの拡張子
    filename_ext = ".json"

    def write_and_print(self, file, str):
        print(str)
        file.write(str)
        file.write('\n')

    def export(self):
        """ファイルに出力"""
        print("シーン情報出力開始... %r" % self.filepath)

        #ファイルをテキスト形式で書きだしようにオープン
        #スコープを抜けると自動的にクローズされる
        with open(self.filepath, "wt") as file:
            #ファイルに文字列を書き込む
            self.write_and_print(file, "SCENE")

            #シーン内の全オブジェクトについて
            for object in bpy.context.scene.objects:
                #親オブジェクトの名前を表示
                if object.parent:
                    self.write_and_print(file, "Parent:" + object.parent.name)
                #シーン直下のオブジェクトをルートノード(深さ0)とし、再帰関数で走査
                self.parse_scene_recursive(file, object, 0)

    def export_json(self):
        """JSON形式でファイル出力"""
        #保存する情報をまとめるdict
        json_object_root = dict()

        #ノード名
        json_object_root["name"] = "scene"
        #オブジェクトリストの作成
        json_object_root["objects"] = list()

        #シーン内の全オブジェクト走査してパック
        for object in bpy.context.scene.objects:
            #親オブジェクトがあるものはスキップ
            if(object.parent):
                continue

            #シーン直下のオブジェクトをルートノード(深さ0)とし再帰関数で走査
            self.parse_scene_recursive_json(json_object_root["objects"], object, 0)

        #オブジェクトをJSON文字列にエンコード
        json_text = json.dumps(json_object_root, ensure_ascii=False, cls=json.JSONEncoder, indent=4)
        #コンソールに表示してみる
        print(json_text)

        #ファイルをテキスト形式で書きだし用にオープン
        #スコープを抜けると自動的にクローズされる
        with open(self.filepath, "wt", encoding="utf-8") as file:
            #ファイルに文字列を書き込む
            file.write(json_text)

    def execute(self, context):
        print("シーン情報をExportします")  

        #ファイルに出力
        self.export_json()

        print("シーン情報をExportしました")
        self.report({'INFO'}, "シーン情報をExportしました")

        return {'FINISHED'}
    
    def parse_scene_recursive(self, file, object, level):
        """シーン解析用再帰関数"""

        #深さ分インデントする(深さ0)
        indent = ''
        for i in range(level):
            indent += "\t"
        
        # オブジェクト名書き込み
        self.write_and_print(file, indent + object.type + " - " + object.name)
        #ローカルトランスフォーム行列から平行移動、回転、スケーリングを抽出
        #型はVector, Quaternion, Vector
        trans, rot, scale = object.matrix_local.decompose()
        #回転をQuaternionからEuler(3軸での回転角)に変換
        rot = rot.to_euler()
        #ラジアンから度数法に変換
        rot.x = math.degrees(rot.x)
        rot.y = math.degrees(rot.y)
        rot.z = math.degrees(rot.z)
        #トランスフォーム情報を表示
        self.write_and_print(file, indent + "Trans(%f, %f, %f)" % (trans.x, trans.y, trans.z))
        self.write_and_print(file, indent + "Rot(%f, %f, %f)" % (rot.x, rot.y, rot.z))
        self.write_and_print(file, indent + "Scale(%f, %f, %f)" % (scale.x, scale.y, scale.z))
    
        #カスタムプロパティ'file_name'
        if "file_name" in object:
            self.write_and_print(file, indent + "N %s" % object["file_name"])
        #カスタムプロパティ'collision'
        if "collider" in object:
            self.write_and_print(file, indent + "C %s" % object["collider"])
            temp_str = indent + "CC %f %f %f"
            temp_str %= (object["collider_center"][0],object["collider_center"][1],object["collider_center"][2])
            self.write_and_print(file, temp_str)
            temp_str = indent + "CS %f %f %f"
            temp_str %= (object["collider_size"][0],object["collider_size"][1],object["collider_size"][2])
            self.write_and_print(file, temp_str)

        self.write_and_print(file, indent + 'END')
        self.write_and_print(file,'')

        #子ノードへ進む(深さが1下がる)
        for child in object.children:
            self.parse_scene_recursive(file, child, level + 1)
    
    def parse_scene_recursive_json(self, data_parent, object, level):
        #シーンのオブジェクト1個分のjsonオブジェクト生成
        json_object = dict()
        #オブジェクト種類
        json_object["type"] = object.type
        #オブジェクト名
        json_object["name"] = object.name

        #その他の情報をパック
        #オブジェクトのローカルトランスフォームから平行移動、回転、スケールを抽出
        trans, rot, scale = object.matrix_local.decompose()
        #回転をQuaternionからEulerに変換
        rot = rot.to_euler()
        #ラジアンから度数法に変換
        rot.x = math.degrees(rot.x)
        rot.y = math.degrees(rot.y)
        rot.z = math.degrees(rot.z)
        #トランスフォーム情報をディクショナリに登録
        transform = dict()
        transform["translation"] = (trans.x, trans.y, trans.z)
        transform["rotation"] = (rot.x, rot.y, rot.z)
        transform["scaling"] = (scale.x, scale.y, scale.z)
        #まとめて1個分のjsonオブジェクトに登録
        json_object["transform"] = transform

        #カスタムプロパティ'無効オプション'
        if "disabled" in object:
            json_object["disabled"] = object["disabled"]

        #カスタムプロパティ'file_name'
        if "file_name" in object:
            json_object["file_name"] = object["file_name"]

        #カスタムプロパティ'Collider'
        if "collider" in object:
            collider = dict()
            collider["type"] = object["collider"]
            collider["center"] = object["collider_center"].to_list()
            collider["size"] = object["collider_size"].to_list()
            json_object["collider"] = collider

        #1個分のjsonオブジェクトを親オブジェクトに登録
        data_parent.append(json_object)

        #直接子供リストを走査
        if len(object.children) > 0:
            #子ノードリストを作成
            json_object["children"] = list()
            #子ノードへ進む
            for child in object.children:
                self.parse_scene_recursive_json(json_object["children"], child, level + 1)
