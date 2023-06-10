from html import escape
from PIL import Image

def convert_to_html(payload):
    html = "<h3>Payload情報:</h3>"
    html += "<ul>"
    for key, value in payload.items():
        html += f"<li>{escape(key)}: {escape(str(value))}</li>"
    html += "</ul>"
    return html

def get_image_metadata(image):
    # 引数が正しいか確認
    if image is None:
        print("get_image_metadata: image is None")
        return None, None
    metadata = image.info.get('parameters')
    with open('metadata.txt', 'w') as file:
        file.write(metadata)
    with open('metadata.txt', 'r') as file:
        content = file.read()

    # "Negative prompt:" のインデックスを取得
    negative_prompt_index = content.find("Negative prompt:")
    steps_index = content.find("Steps:")

    if steps_index != -1:
        # "Steps:" の後の部分を取り出す
        steps_section = content[steps_index:].strip()
    else:
        steps_section = "Stepsが見つかりませんでした"

    if negative_prompt_index != -1:
        # "Negative prompt:" の前の文章全体を取り出す
        prompt = content[:negative_prompt_index].strip()

        # "Negative prompt:" の後の行から "Steps:" の前の行までの部分を取り出す
        start_index = negative_prompt_index + len("Negative prompt:")
        end_index = content.index("Steps:") if steps_index != -1 else negative_prompt_index
        negative_prompt = content[start_index:end_index].strip()
    else:
        prompt = content[:steps_index].strip()
        negative_prompt = ""
    # 結果を表示
    print("prompt:")
    print(prompt)
    print("Negative promptが見つかりませんでした" if negative_prompt_index == -1 else "Negative prompt:")
    print(negative_prompt)
    print("Steps section:")
    print(steps_section)

    settings = steps_section.split(", ")
    payload = {'prompt': prompt, 'negative_prompt': negative_prompt}
    for setting in settings:
        key, value = setting.split(": ", 1)
        key = key.lower()
        if value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass
        payload[key] = value
    width, height = map(int, payload.pop('size').split('x'))
    payload['width'] = width
    payload['height'] = height
    payload['seed'] = -1
    if "Hires upscale" in payload:
        payload["hr_scale"] = payload["Hires upscale"]
    if "Hires upscaler" in payload:
        payload["hr_upscaler"] = payload["Hires upscaler"]
    if "hr_scale" in payload and "hr_upscaler" in payload:
        payload["enable_hr"] = True
    if "Denoising strength" in payload:
        payload["denoising_strength"] = payload["Denoising strength"]
    if "CFG scale" in payload:
        payload["cfg_scale"] = payload["CFG scale"]
    keys_to_keep = ["enable_hr", "denoising_strength", "firstphase_width", "firstphase_height", "hr_scale", "hr_upscaler", "hr_second_pass_steps", "hr_resize_x", "hr_resize_y", "prompt", "styles", "seed", "subseed", "subseed_strength", "seed_resize_from_h", "seed_resize_from_w", "sampler_name", "batch_size", "n_iter", "steps", "cfg_scale", "width", "height", "restore_faces", "tiling", "do_not_save_samples", "do_not_save_grid", "negative_prompt", "eta", "s_churn", "s_tmax", "s_tmin", "s_noise", "override_settings", "override_settings_restore_afterwards", "script_args", "script_name", "sampler_index"]
    payload = {k: v for k, v in payload.items() if k in keys_to_keep}
    
    payload_html = convert_to_html(payload)
    return payload, payload_html
