import modules.scripts as scripts
import gradio as gr
import os
from PIL import Image
import json

from modules import script_callbacks
from scripts.extension_script import get_image_metadata
from scripts.Generate_standard import main_generate

# 画像が変更されたときの処理
def update_html(image):
    if image is None:
        print("update_html: image is None")
        return
    payload, payload_html = get_image_metadata(image)
    html = payload_html
    payload1 = json.dumps(payload)
    return html, payload1



# コンポーネントを作成
def on_ui_tabs():
    image_upload = None

    with gr.Blocks(analytics_enabled=False) as ui_component:
        with gr.Row():
            image_upload = gr.Image(elem_id="pngload_image", label="UploadImage", source="upload", interactive=True, type="pil")
            batch_size = gr.Slider(
                minimum=1,
                maximum=49,
                step=1,
                value=1,
                label="BatchSize"
            )
            count_size = gr.Slider(
                minimum=1,
                maximum=100,
                step=1,
                value=1,
                label="CountSize"
            )
            encoder_size = gr.Slider(
                minimum=256,
                maximum=4096,
                step=16,
                value=2800,
                label="EncoderSize"
            )
            decoder_size = gr.Slider(
                minimum=48,
                maximum=512,
                step=16,
                value=192,
                label="DecoderSize"
            )
            Scale_Factor = gr.Slider(
                minimum=1.0,
                maximum=8.0,
                step=0.1,
                value=2,
                label="ScaleFactor"
            )
            Eagle_Send = gr.Checkbox(label='Eagle_Send', value=True)
        with gr.Column(variant='panel'):
            html = gr.HTML()
            payload1 = gr.Textbox(label="payload", visible=False)

        with gr.Column(variant='panel'):
            button = gr.Button(label = "Generate")
            image_output = gr.Gallery(label="OutputImage", height=1920)

            button.click(
            fn=main_generate,
            inputs=[payload1, batch_size, count_size, encoder_size, decoder_size, Scale_Factor, Eagle_Send],
            outputs=[image_output],
        )

        
        

        image_upload.change(
            fn=update_html,
            inputs=[image_upload],
            outputs=[html ,payload1],
        )

    return [(ui_component, "Hires[Tiled Diffusion & ControlNet Tile]", "extension_template_tab")]



# 作成したコンポーネントをwebuiに登録
script_callbacks.on_ui_tabs(on_ui_tabs)
