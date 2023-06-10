from PIL import Image, PngImagePlugin
import pprint
from tqdm import tqdm
import datetime
import os
import webuiapi
import requests
import json
import re

url = "http://127.0.0.1:7860"

def generate_initial_images(payload, batch_size, count_size, pre_upscaled_image, output_folder):
    api = webuiapi.WebUIApi()
    results = []
    for _ in tqdm(range(count_size), desc='Rendering Initial Images'):
        payload['batch_size'] = batch_size
        result = api.txt2img(**payload)
        results.append(result)
        if pre_upscaled_image:
                pnginfo = PngImagePlugin.PngInfo()
                pnginfo.add_text("parameters", result.info['infotexts'][0])
                now = datetime.datetime.now()
                date_string = now.strftime("%Y%m%d_%H%M%S")
                new_filename = os.path.join("{}.png".format(date_string))
                output_path = os.path.join(output_folder, new_filename)
                result.image.save(output_path, pnginfo=pnginfo)
    images = [image for result in results for image in result.images]
    return images


def prepare_high_res_settings(payload, encoder_size, decoder_size, Scale_Factor, noise_inverse):
    payload_copy = dict(payload)
    keys_to_keep = ["prompt", "negative_prompt", "width", "height"]
    keys_to_remove = [key for key in payload_copy.keys() if key not in keys_to_keep]
    for key in keys_to_remove:
        del payload_copy[key]
    unit1 = webuiapi.ControlNetUnit(module='tile_colorfix', model='control_v11f1e_sd15_tile [a371b31b]', pixel_perfect=True)
    width = payload['width']
    height = payload['height']
    Tiled_Diffusion_payload = {
        "enabled": True,
        "method": "MultiDiffusion",
        "overwrite_size": True,
        "keep_input_size": True,
        "image_width": width,
        "image_height": height,
        "tile_width": 96,
        "tile_height": 96,
        "overlap": 48,
        "tile_batch_size": 4,
        "upscaler_name": "4x-AnimeSharp",
        "scale_factor": Scale_Factor,
        "noise_inverse": noise_inverse,
        "noise_inverse_steps": 10,
        "noise_inverse_retouch": 1,
        "noise_inverse_renoise_strength": 0,
        "noise_inverse_renoise_kernel": 64,
        "control_tensor_cpu": False,
        "enable_bbox_control": False,
        "draw_background": False,
        "causal_layers": False,
        "bbox_control_states": []
}
    Tiled_VAE_payload = {
        "enabled": True,
        "encoder_tile_size": encoder_size,
        "decoder_tile_size": decoder_size,
        "vae_to_gpu": True,
        "fast_decoder": True,
        "fast_encoder": True,
        "color_fix": False
}
    Tiled_Diffusion_payload_list = list(Tiled_Diffusion_payload.values())
    Tiled_VAE_payload_list = list(Tiled_VAE_payload.values())
    payload_copy.update({
        "images": [],  # この部分は後で更新されます
        "denoising_strength": 0.75,
        "seed": -1,
        "steps": 50,
        "cfg_scale": 7,
        "controlnet_units": [unit1],
        "alwayson_scripts": {
            "Tiled Diffusion": {
            "args": Tiled_Diffusion_payload_list
            },
            "Tiled VAE": {
            "args": Tiled_VAE_payload_list
            }
        }
})
    return payload_copy

def extract_tags(infotext):
    lines = infotext.split('\n')
    tags = []

    # First line
    tags.extend([tag.strip() for tag in lines[0].split(',') if tag.strip()])

    # Second line
    if not lines[1].startswith('Negative prompt:'):
        match = re.search(r'(Model: [^,]+)', lines[1])
        if match:
            tags.append(match.group(1).strip())

    # Third line, if exists
    if len(lines) > 2:
        match = re.search(r'(Model: [^,]+)', lines[2])
        if match:
            tags.append(match.group(1).strip())

    return tags

def upscale_and_save_images(images, payload_copy, Eagle_Send, output_folder):
    image_list = []
    api = webuiapi.WebUIApi()
    pprint.pprint(payload_copy, indent=4, sort_dicts=False)
    total_images = len(images)
    for i, image in tqdm(enumerate(images), total=total_images, desc='Upscaling and Saving Images'):
        payload_copy["images"] = [image]
        result2 = api.img2img(**payload_copy)
        pnginfo2 = PngImagePlugin.PngInfo()
        pnginfo2.add_text("parameters", result2.info['infotexts'][0])
        now = datetime.datetime.now()
        date_string = now.strftime("%Y%m%d_%H%M%S")
        new_filename = os.path.join("{}.png".format(date_string))
        output_path = os.path.join(output_folder, new_filename)
        result2.image.save(output_path, pnginfo=pnginfo2)

        tags = extract_tags(result2.info['infotexts'][0])
        full_path = os.path.abspath(output_path)
        # Eagle App POST request
        data = {
            "path": full_path,
            "name": new_filename,
            "annotation": result2.info['infotexts'][0],
            "tags": tags
        }
        requestOptions = {
            'headers': {'Content-Type': 'application/json'},
            'data': json.dumps(data)
        }
        if Eagle_Send:
            response = requests.post("http://localhost:41595/api/item/addFromPath", **requestOptions)
            print(response.json())
        
        if is_iterable(result2.image):
            # イテラブルな場合はそのまま追加
            image_list.extend(result2.image)
        else:
            # イテラブルでない場合はリストに変換して追加
            image_list.append(result2.image)

    return image_list

def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False

def main_generate(payload1, batch_size, count_size, encoder_size, decoder_size, Scale_Factor, Eagle_Send, pre_upscaled_image, noise_inverse):
    payload = json.loads(payload1)
    now = datetime.datetime.now()
    folder_name = now.strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join('outputs', 'Hires-Tiled-Diffusion-ControlNet-Tile-', folder_name)
    os.makedirs(output_folder, exist_ok=True)
    images = generate_initial_images(payload, batch_size, count_size, pre_upscaled_image, output_folder)
    payload_copy = prepare_high_res_settings(payload, encoder_size, decoder_size, Scale_Factor, noise_inverse)
    image_output = upscale_and_save_images(images, payload_copy, Eagle_Send, output_folder)
    return image_output, output_folder
