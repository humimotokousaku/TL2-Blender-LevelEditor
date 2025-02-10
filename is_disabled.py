import bpy

# カスタムプロパティ['collider']追加
class MYADDON_OT_is_disabled(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_is_disabled"
    bl_label = "Disabled 追加"
    bl_description = "['disabled']カスタムプロパティを追加します"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        #['disabled']カスタムプロパティを追加
        context.object["disabled"] = True

        return {"FINISHED"}

class OBJECT_PT_is_disabled(bpy.types.Panel):
    bl_idname = "OBJECT_PT_is_disabled"
    bl_label = "Disabled"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    #サブメニューの描画
    def draw(self, context):
        #パネルに項目を追加
        if "disabled" in context.object:
            #すでにプロパティがあれば表示
            self.layout.prop(context.object, '["disabled"]', text=self.bl_label)
        else:
            #プロパティがなければ追加ボタンを表示
            self.layout.operator(MYADDON_OT_is_disabled.bl_idname)
