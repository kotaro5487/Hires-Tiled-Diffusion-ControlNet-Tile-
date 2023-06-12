# Hires-Tiled-Diffusion-ControlNet-Tile-
Hires[Tiled Diffusion &amp; ControlNet Tile]
multidiffusion-upscaler-for-automatic1111 + sd-webui-controlnet
https://github.com/Mikubill/sd-webui-controlnet
https://github.com/pkuliyi2015/multidiffusion-upscaler-for-automatic1111

AUTOMATIC1111/stable-diffusion-webuiの拡張機能です。
生成済みの画像を拡張機能の画像入力欄に放り込んだら、
txt2imgで画像を生成した後、自動的にimg2imgでmultidiffusion-upscalerとsd-webui-controlnet
を組み合わせて拡大します。
最終目標は、multidiffusion-upscaler-for-automatic1111 + sd-webui-controlnetを
hires機能みたいに使ってtxt2imgで高解像度高品質の画像を生成することですが、
今の知識では作れなかったので、APIで実行できるようにしました。

インストール
AUTOMATIC1111/stable-diffusion-webuiの拡張機能欄の
URLからインストールに下記URLを入力してインストールして下さい。
https://github.com/kotaro5487/Hires-Tiled-Diffusion-ControlNet-Tile-

webui-user.batのset COMMANDLINE_ARGS=に--apiオプションを追加して下さい。


使い方
1.上部の画像入力欄に生成済みの画像を入れて下さい
生成に必要な情報を取り込みます。
2.バッチサイズやバッチカウント等必要な情報を入力して下さい。
3.実行ボタンを押すと、拡大した上で画像を生成します。
4.生成された画像は下部の実行ボタンでフォルダを開くことが出来ます。