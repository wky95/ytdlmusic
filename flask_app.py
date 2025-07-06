from flask import Flask, request, send_file, render_template, redirect, url_for, flash
import yt_dlp
import subprocess
import io

app = Flask(__name__)
app.secret_key = 'your-secret-key'

def normalize_time(t):
    parts = t.split(':')
    parts = [int(p) for p in parts]

    if len(parts) == 2:  # mm:ss
        h, m, s = 0, parts[0], parts[1]
    elif len(parts) == 3:  # hh:mm:ss
        h, m, s = parts
    else:
        raise ValueError("時間格式錯誤")
    return f"{h:02}:{m:02}:{s:02}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/audio', methods=['POST'])
def download_mp3():
    url = request.form.get('url')
    start = request.form.get('start')  
    end = request.form.get('end')      
    try:
        url = url.split("&list")[0]
        ydl_opts = {'geo_bypass': True, 'format': 'bestaudio/best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info['title']

        # 動態建立 ffmpeg 指令
        ffmpeg_cmd = ['ffmpeg']

        # ➕ 如果有設定裁剪時間就加上
        if start:
            start = normalize_time(start)
            print(start)
            ffmpeg_cmd += ['-ss', start]
        if end:
            end = normalize_time(end)
            print(end)
            ffmpeg_cmd += ['-to', end]

        ffmpeg_cmd += [
            '-i', audio_url,
            '-f', 'mp3',
            '-ab', '320000',
            '-vn',
            '-loglevel', 'quiet',
            'pipe:1'
        ]

        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE)
        mp3_data = process.stdout.read()
        process.wait()

        if process.returncode != 0:
            raise Exception("ffmpeg failed")

        return send_file(
            io.BytesIO(mp3_data),
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=f"{title}.mp3"
        )

    except Exception as e:
        print("Error:", e)
        flash('下載或轉換過程發生錯誤')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
