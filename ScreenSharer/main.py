from flask import Flask, Response, request, render_template_string
import io
import time
import mss
from PIL import Image, ImageDraw
import pyautogui
import math
import threading

app = Flask(__name__)


class FPSControlledStreamer:
    def __init__(self):
        self.is_streaming = False
        self.quality = 70
        self.selected_monitor = 1
        self.monitors = []
        self.cursor_style = 'crosshair'
        self.cursor_color = 'red'
        self.cursor_size = 15
        self.show_click_effect = True
        self.last_click_time = 0
        self.click_effect_duration = 0.3
        self.last_monitor_update = 0
        self.monitor_update_interval = 2.0

        # Настройки FPS
        self.target_fps = 25
        self.frame_interval = 1.0 / self.target_fps
        self.last_frame_time = 0
        self.actual_fps = 0
        self.frame_count = 0
        self.fps_update_time = 0

        self.detect_monitors()

    def detect_monitors(self):
        try:
            with mss.mss() as sct:
                self.monitors = sct.monitors
                self.last_monitor_update = time.time()
                print(f"📺 Обновлена информация о мониторах. Найдено: {len(self.monitors)}")
        except Exception as e:
            print(f"❌ Ошибка обнаружения мониторов: {e}")

    def set_fps(self, fps):
        """Устанавливает целевую частоту кадров"""
        self.target_fps = max(1, min(60, fps))  # Ограничиваем от 1 до 60 FPS
        self.frame_interval = 1.0 / self.target_fps
        print(f"🎯 Установлена целевая частота: {self.target_fps} FPS")

    def update_fps_counter(self):
        """Обновляет счетчик реального FPS"""
        current_time = time.time()
        self.frame_count += 1

        if current_time - self.fps_update_time >= 1.0:
            self.actual_fps = self.frame_count
            self.frame_count = 0
            self.fps_update_time = current_time

    def get_monitor_with_retry(self, monitor_index):
        current_time = time.time()

        if current_time - self.last_monitor_update > self.monitor_update_interval:
            self.detect_monitors()

        if monitor_index >= len(self.monitors):
            print(f"⚠️ Индекс монитора {monitor_index} невалиден. Используем монитор 1")
            monitor_index = 1

        return self.monitors[monitor_index]

    def capture_adaptive_screenshot(self, monitor_index):
        try:
            monitor = self.get_monitor_with_retry(monitor_index)

            with mss.mss() as sct:
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                return img, True

        except Exception as e:
            print(f"❌ Ошибка захвата монитора {monitor_index}: {e}")
            self.detect_monitors()
            try:
                monitor = self.get_monitor_with_retry(monitor_index)
                with mss.mss() as sct:
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                    return img, True
            except Exception as e2:
                print(f"❌ Критическая ошибка захвата: {e2}")
                fallback_size = (800, 600)
                img = Image.new('RGB', fallback_size, color='black')
                draw = ImageDraw.Draw(img)
                draw.text((50, 50), f"Ошибка захвата экрана\n{e2}", fill='white')
                return img, False

    def draw_cursor(self, img, monitor_index):
        try:
            cursor_x, cursor_y = pyautogui.position()
            monitor = self.get_monitor_with_retry(monitor_index)
            monitor_left = monitor['left']
            monitor_top = monitor['top']
            monitor_width = monitor['width']
            monitor_height = monitor['height']

            if not (monitor_left <= cursor_x < monitor_left + monitor_width and
                    monitor_top <= cursor_y < monitor_top + monitor_height):
                return img

            rel_x = cursor_x - monitor_left
            rel_y = cursor_y - monitor_top

            if not (0 <= rel_x < img.width and 0 <= rel_y < img.height):
                return img

            draw = ImageDraw.Draw(img)
            size = self.cursor_size

            if self.cursor_style == 'crosshair':
                draw.line([(rel_x, max(0, rel_y - size)), (rel_x, min(img.height - 1, rel_y + size))],
                          fill=self.cursor_color, width=3)
                draw.line([(max(0, rel_x - size), rel_y), (min(img.width - 1, rel_x + size), rel_y)],
                          fill=self.cursor_color, width=3)
                draw.ellipse([(rel_x - 4, rel_y - 4), (rel_x + 4, rel_y + 4)],
                             fill='yellow', outline=self.cursor_color, width=2)

            elif self.cursor_style == 'circle':
                draw.ellipse([(max(0, rel_x - size), max(0, rel_y - size)),
                              (min(img.width - 1, rel_x + size), min(img.height - 1, rel_y + size))],
                             outline=self.cursor_color, width=3)
                draw.ellipse([(rel_x - 2, rel_y - 2), (rel_x + 2, rel_y + 2)],
                             fill=self.cursor_color)

            elif self.cursor_style == 'arrow':
                points = [
                    (rel_x, max(0, rel_y - size)),
                    (max(0, rel_x - size // 2), max(0, rel_y - size // 3)),
                    (max(0, rel_x - size // 4), max(0, rel_y - size // 3)),
                    (max(0, rel_x - size // 4), min(img.height - 1, rel_y + size)),
                    (min(img.width - 1, rel_x + size // 4), min(img.height - 1, rel_y + size)),
                    (min(img.width - 1, rel_x + size // 4), max(0, rel_y - size // 3)),
                    (min(img.width - 1, rel_x + size // 2), max(0, rel_y - size // 3)),
                ]
                draw.polygon(points, fill=self.cursor_color)

            elif self.cursor_style == 'target':
                for i, radius in enumerate([size, size // 2, size // 4]):
                    color = self.cursor_color if i == 0 else 'yellow'
                    bbox = [(max(0, rel_x - radius), max(0, rel_y - radius)),
                            (min(img.width - 1, rel_x + radius), min(img.height - 1, rel_y + radius))]
                    draw.ellipse(bbox, outline=color, width=2)

            if self.show_click_effect:
                current_time = time.time()
                if current_time - self.last_click_time < self.click_effect_duration:
                    elapsed = current_time - self.last_click_time
                    self.draw_click_effect(draw, rel_x, rel_y, elapsed, img.width, img.height)

        except Exception as e:
            print(f"⚠️ Ошибка отрисовки курсора: {e}")

        return img

    def draw_click_effect(self, draw, x, y, elapsed_time, img_width, img_height):
        if elapsed_time > self.click_effect_duration:
            return

        alpha = int(255 * (1 - elapsed_time / self.click_effect_duration))
        if alpha <= 0:
            return

        max_radius = 20
        for radius in range(5, max_radius, 5):
            progress = radius / max_radius
            current_alpha = int(alpha * (1 - progress))
            if current_alpha > 0:
                bbox = [
                    (max(0, x - radius), max(0, y - radius)),
                    (min(img_width - 1, x + radius), min(img_height - 1, y + radius))
                ]
                draw.ellipse(bbox, outline=(255, 255, 0), width=2)

    def generate_frames(self, monitor_index):
        self.last_frame_time = time.time()
        self.fps_update_time = time.time()
        self.frame_count = 0

        while self.is_streaming:
            try:
                current_time = time.time()
                elapsed = current_time - self.last_frame_time

                # Контроль FPS - ждем нужное время между кадрами
                if elapsed < self.frame_interval:
                    time.sleep(self.frame_interval - elapsed)

                self.last_frame_time = time.time()

                # Захватываем скриншот
                img, success = self.capture_adaptive_screenshot(monitor_index)

                if success:
                    img = self.draw_cursor(img, monitor_index)

                # Обновляем счетчик FPS
                self.update_fps_counter()

                # Конвертируем в JPEG
                img_io = io.BytesIO()
                img.save(img_io, 'JPEG', quality=self.quality, optimize=True)
                img_io.seek(0)

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + img_io.read() + b'\r\n')

            except Exception as e:
                print(f"❌ Критическая ошибка в генераторе кадров: {e}")
                time.sleep(0.1)


streamer = FPSControlledStreamer()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Screen Stream with FPS Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }

        html, body {
            width: 100%;
            height: 100%;
            overflow: hidden;
        }

        body { 
            font-family: Arial; 
            background: #1a1a1a; 
            color: white;
            display: flex;
            flex-direction: column;
        }

        .container { 
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 10px;
            background: #2b2b2b;
            min-height: 100vh;
        }

        .fullscreen-mode .container {
            padding: 0;
            background: #000;
        }

        .controls { 
            padding: 15px; 
            background: #3a3a3a; 
            border-radius: 8px;
            margin-bottom: 10px;
            flex-shrink: 0;
        }

        .fullscreen-mode .controls {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.9);
            margin: 0;
            border-radius: 0;
            z-index: 1000;
            padding: 10px;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .fullscreen-mode .controls:hover {
            opacity: 1;
        }

        button { 
            padding: 10px 15px; 
            margin: 3px; 
            font-size: 14px; 
            cursor: pointer; 
            border: none; 
            border-radius: 5px;
            transition: all 0.2s ease;
        }

        button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }

        .btn-start { background: #28a745; color: white; }
        .btn-stop { background: #dc3545; color: white; }
        .btn-option { background: #5a6268; color: white; }
        .btn-fullscreen { background: #ff6b35; color: white; }
        .btn-refresh { background: #17a2b8; color: white; }

        .btn-exit-fullscreen { background: #dc3545; color: white; display: none; }
        .fullscreen-mode .btn-fullscreen { display: none; }
        .fullscreen-mode .btn-exit-fullscreen { display: inline-block; }

        select, input { 
            padding: 8px; 
            margin: 0 3px; 
            background: #4a4a4a; 
            color: white; 
            border: 1px solid #6c757d; 
            border-radius: 4px;
            font-size: 14px;
        }

        .video-container {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #000;
            border-radius: 8px;
            overflow: hidden;
            min-height: 0;
        }

        #video { 
            width: 100%;
            height: 100%;
            object-fit: fill;
            display: block;
        }

        .fullscreen-mode .video-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            border-radius: 0;
            z-index: 999;
        }

        .fullscreen-mode #video {
            width: 100vw;
            height: 100vh;
            object-fit: fill;
        }

        .status { 
            padding: 10px; 
            background: #495057; 
            border-radius: 5px;
            margin-top: 10px;
            flex-shrink: 0;
        }

        .fullscreen-mode .status {
            display: none;
        }

        .cursor-controls { 
            display: flex; 
            flex-wrap: wrap; 
            gap: 8px; 
            margin: 10px 0; 
        }

        .fullscreen-mode .cursor-controls {
            display: none;
        }

        .control-group { 
            background: #404040; 
            padding: 8px; 
            border-radius: 5px;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .fps-controls {
            background: #2d3748;
            padding: 8px;
            border-radius: 5px;
            margin-left: 10px;
        }

        .fps-slider-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .fps-slider {
            width: 100px;
            height: 5px;
            background: #4a5568;
            border-radius: 5px;
            outline: none;
        }

        .fps-value {
            min-width: 40px;
            text-align: center;
            font-weight: bold;
        }

        .fps-indicator {
            background: #805ad5;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin-left: 5px;
        }

        .fps-low { background: #e53e3e; }
        .fps-medium { background: #d69e2e; }
        .fps-high { background: #38a169; }

        .resolution-info {
            background: #155724;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 12px;
            margin-left: 10px;
        }

        .scaling-controls {
            background: #2d3748;
            padding: 8px;
            border-radius: 5px;
            margin-left: 10px;
        }

        .scaling-btn {
            padding: 6px 10px;
            font-size: 12px;
            background: #4a5568;
        }

        .scaling-btn.active {
            background: #3182ce;
        }

        .compact-controls {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
        }

        .control-section {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .performance-info {
            background: #2d3748;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 11px;
            margin-top: 5px;
        }

        @media (max-width: 768px) {
            .controls {
                padding: 10px;
            }

            .compact-controls {
                flex-direction: column;
                align-items: stretch;
            }

            .control-section {
                justify-content: center;
                margin: 2px 0;
            }

            button {
                padding: 8px 12px;
                font-size: 12px;
            }

            .fps-slider {
                width: 80px;
            }
        }

        .fullscreen-indicator {
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(255, 107, 53, 0.9);
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            z-index: 1002;
            display: none;
        }

        .fullscreen-mode .fullscreen-indicator {
            display: block;
        }
    </style>
</head>
<body>
    <div class="fullscreen-indicator">🔴 Прямой эфир (F11 - выход)</div>

    <div class="container" id="mainContainer">
        <div class="controls">
            <div class="compact-controls">
                <div class="control-section">
                    <select id="monitorSelect">
                        {% for i in range(monitors_count) %}
                        <option value="{{ i }}">Монитор {{ i + 1 }}</option>
                        {% endfor %}
                    </select>

                    <select id="qualitySelect">
                        <option value="30">Низкое</option>
                        <option value="50" selected>Среднее</option>
                        <option value="70">Высокое</option>
                        <option value="90">Макс.</option>
                    </select>
                </div>

                <div class="control-section">
                    <button class="btn-start" onclick="startStream()">▶ Старт</button>
                    <button class="btn-stop" onclick="stopStream()">⏹ Стоп</button>
                    <button class="btn-refresh" onclick="forceRefresh()">🔄 Обновить</button>
                    <button class="btn-fullscreen" onclick="toggleFullscreen()">📺 Полный экран</button>
                    <button class="btn-exit-fullscreen" onclick="exitFullscreen()">❌ Выйти</button>
                </div>

                <div class="control-section">
                    <div class="fps-controls">
                        <strong>FPS:</strong>
                        <div class="fps-slider-container">
                            <input type="range" id="fpsSlider" class="fps-slider" 
                                   min="1" max="60" value="25" 
                                   oninput="updateFPSValue(this.value)">
                            <span id="fpsValue" class="fps-value">25</span>
                            <span id="actualFPS" class="fps-indicator fps-medium">25</span>
                        </div>
                    </div>

                    <div class="scaling-controls">
                        <strong>Масштаб:</strong>
                        <button class="scaling-btn active" onclick="setScaling('fill')">🔄 Заполнение</button>
                        <button class="scaling-btn" onclick="setScaling('fit')">📐 Вписать</button>
                        <button class="scaling-btn" onclick="setScaling('stretch')">🔲 Растянуть</button>
                    </div>

                    <span class="resolution-info" id="resolutionInfo">
                        📏 <span id="currentResolution">-</span>
                    </span>
                </div>

                <div class="control-section">
                    <label>
                        <input type="checkbox" id="clickEffect" checked onchange="toggleClickEffect()">
                        Эффект клика
                    </label>
                </div>
            </div>

            <div class="performance-info">
                💡 <strong>Рекомендации по FPS:</strong> 
                <span style="color: #e53e3e;">1-15</span> - низкая нагрузка, 
                <span style="color: #d69e2e;">16-30</span> - баланс, 
                <span style="color: #38a169;">31-60</span> - плавность
            </div>
        </div>

        <div class="cursor-controls">
            <div class="control-group">
                <strong>Курсор:</strong>
                <button class="btn-option" onclick="setCursorStyle('crosshair')">✚</button>
                <button class="btn-option" onclick="setCursorStyle('circle')">⭕</button>
                <button class="btn-option" onclick="setCursorStyle('arrow')">➡</button>
                <button class="btn-option" onclick="setCursorStyle('target')">🎯</button>
            </div>

            <div class="control-group">
                <strong>Цвет:</strong>
                <button class="btn-option" onclick="setCursorColor('red')" style="background: #dc3545;">Кр</button>
                <button class="btn-option" onclick="setCursorColor('blue')" style="background: #007bff;">Сн</button>
                <button class="btn-option" onclick="setCursorColor('green')" style="background: #28a745;">Зл</button>
                <button class="btn-option" onclick="setCursorColor('yellow')" style="background: #ffc107; color: black;">Жл</button>
            </div>

            <div class="control-group">
                <strong>Размер:</strong>
                <button class="btn-option" onclick="changeCursorSize(-3)">➖</button>
                <span id="sizeDisplay">15px</span>
                <button class="btn-option" onclick="changeCursorSize(3)">➕</button>
            </div>
        </div>

        <div class="video-container">
            <img id="video" src="" alt="Трансляция появится здесь" onload="updateResolutionInfo()">
        </div>

        <div class="status" id="status">
            💡 Выберите монитор и нажмите "Старт" для начала трансляции
        </div>
    </div>

    <script>
        let currentMonitor = 1;
        let cursorStyle = 'crosshair';
        let cursorColor = 'red';
        let cursorSize = 15;
        let clickEffect = true;
        let isFullscreen = false;
        let currentScaling = 'fill';
        let currentFPS = 25;
        let resolutionCheckInterval;
        let fpsUpdateInterval;

        function startStream() {
            currentMonitor = document.getElementById('monitorSelect').value;
            const quality = document.getElementById('qualitySelect').value;

            const video = document.getElementById('video');
            video.src = `/stream?monitor=${currentMonitor}&quality=${quality}&style=${cursorStyle}&color=${cursorColor}&size=${cursorSize}&click_effect=${clickEffect}&fps=${currentFPS}&t=${new Date().getTime()}`;

            document.getElementById('status').innerHTML = 
                `🎥 <strong>Трансляция активна</strong> | Монитор: ${parseInt(currentMonitor) + 1} | FPS: ${currentFPS}`;

            startResolutionMonitoring();
            startFPSMonitoring();
        }

        function stopStream() {
            document.getElementById('video').src = '';
            document.getElementById('status').innerHTML = '⏹ <strong>Трансляция остановлена</strong>';
            stopResolutionMonitoring();
            stopFPSMonitoring();
        }

        function forceRefresh() {
            if (document.getElementById('video').src) {
                const currentSrc = document.getElementById('video').src;
                document.getElementById('video').src = '';
                setTimeout(() => {
                    document.getElementById('video').src = currentSrc.split('?')[0] + '?t=' + new Date().getTime();
                }, 100);
            }
        }

        function updateFPSValue(fps) {
            currentFPS = parseInt(fps);
            document.getElementById('fpsValue').textContent = currentFPS;

            // Обновляем индикатор FPS
            const indicator = document.getElementById('actualFPS');
            indicator.textContent = currentFPS;

            // Меняем цвет в зависимости от FPS
            indicator.className = 'fps-indicator ';
            if (currentFPS <= 15) {
                indicator.classList.add('fps-low');
            } else if (currentFPS <= 30) {
                indicator.classList.add('fps-medium');
            } else {
                indicator.classList.add('fps-high');
            }

            // Отправляем новый FPS на сервер
            fetch(`/set_fps?fps=${currentFPS}`);

            // Перезапускаем поток если он активен
            if (document.getElementById('video').src) {
                restartIfActive();
            }
        }

        function setCursorStyle(style) {
            cursorStyle = style;
            restartIfActive();
        }

        function setCursorColor(color) {
            cursorColor = color;
            restartIfActive();
        }

        function changeCursorSize(delta) {
            cursorSize = Math.max(5, Math.min(30, cursorSize + delta));
            document.getElementById('sizeDisplay').textContent = cursorSize + 'px';
            restartIfActive();
        }

        function toggleClickEffect() {
            clickEffect = document.getElementById('clickEffect').checked;
            restartIfActive();
        }

        function setScaling(mode) {
            currentScaling = mode;
            const video = document.getElementById('video');
            const buttons = document.querySelectorAll('.scaling-btn');

            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');

            switch(mode) {
                case 'fill':
                    video.style.objectFit = 'fill';
                    break;
                case 'fit':
                    video.style.objectFit = 'contain';
                    break;
                case 'stretch':
                    video.style.objectFit = 'cover';
                    break;
            }
        }

        function restartIfActive() {
            if (document.getElementById('video').src) {
                stopStream();
                setTimeout(startStream, 300);
            }
        }

        function updateResolutionInfo() {
            const video = document.getElementById('video');
            if (video.naturalWidth && video.naturalHeight) {
                document.getElementById('currentResolution').textContent = 
                    `${video.naturalWidth}×${video.naturalHeight}`;
            }
        }

        function startResolutionMonitoring() {
            resolutionCheckInterval = setInterval(updateResolutionInfo, 2000);
        }

        function stopResolutionMonitoring() {
            if (resolutionCheckInterval) {
                clearInterval(resolutionCheckInterval);
            }
        }

        function startFPSMonitoring() {
            // Обновляем реальный FPS с сервера
            fpsUpdateInterval = setInterval(() => {
                fetch('/get_fps')
                    .then(response => response.json())
                    .then(data => {
                        if (data.actual_fps > 0) {
                            const indicator = document.getElementById('actualFPS');
                            indicator.textContent = data.actual_fps;

                            // Обновляем цвет индикатора реального FPS
                            indicator.className = 'fps-indicator ';
                            if (data.actual_fps <= 15) {
                                indicator.classList.add('fps-low');
                            } else if (data.actual_fps <= 30) {
                                indicator.classList.add('fps-medium');
                            } else {
                                indicator.classList.add('fps-high');
                            }
                        }
                    });
            }, 2000);
        }

        function stopFPSMonitoring() {
            if (fpsUpdateInterval) {
                clearInterval(fpsUpdateInterval);
            }
        }

        // Полноэкранный режим
        function toggleFullscreen() {
            const container = document.querySelector('.video-container');
            if (!isFullscreen) {
                if (container.requestFullscreen) container.requestFullscreen();
                else if (container.webkitRequestFullscreen) container.webkitRequestFullscreen();
                else if (container.msRequestFullscreen) container.msRequestFullscreen();
                isFullscreen = true;
                document.body.classList.add('fullscreen-mode');
            } else {
                exitFullscreen();
            }
        }

        function exitFullscreen() {
            if (document.exitFullscreen) document.exitFullscreen();
            else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
            else if (document.msExitFullscreen) document.msExitFullscreen();
            isFullscreen = false;
            document.body.classList.remove('fullscreen-mode');
        }

        // Обработчики клавиш
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && isFullscreen) exitFullscreen();
            if (e.key === 'F11') { e.preventDefault(); toggleFullscreen(); }
            if (e.key === 'f' || e.key === 'F') { e.preventDefault(); toggleFullscreen(); }
            if (e.key === 'r' || e.key === 'R') { e.preventDefault(); forceRefresh(); }
        });

        document.addEventListener('fullscreenchange', handleFullscreenChange);
        document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
        document.addEventListener('msfullscreenchange', handleFullscreenChange);

        function handleFullscreenChange() {
            isFullscreen = !!(document.fullscreenElement || 
                            document.webkitFullscreenElement || 
                            document.msFullscreenElement);
            if (!isFullscreen) document.body.classList.remove('fullscreen-mode');
        }

        // Обновляем информацию о разрешении
        document.getElementById('video').addEventListener('load', updateResolutionInfo);

        // Автоматически стартуем трансляцию при загрузке
        window.addEventListener('load', function() {
            setTimeout(startStream, 1000);
        });
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        monitors_count=len(streamer.monitors)
    )


@app.route('/stream')
def stream():
    monitor = request.args.get('monitor', default=1, type=int)
    quality = request.args.get('quality', default=70, type=int)
    cursor_style = request.args.get('style', default='crosshair')
    cursor_color = request.args.get('color', default='red')
    cursor_size = request.args.get('size', default=15, type=int)
    click_effect = request.args.get('click_effect', default='true') == 'true'
    fps = request.args.get('fps', default=25, type=int)

    # Устанавливаем FPS
    streamer.set_fps(fps)

    streamer.selected_monitor = monitor
    streamer.quality = quality
    streamer.cursor_style = cursor_style
    streamer.cursor_color = cursor_color
    streamer.cursor_size = cursor_size
    streamer.show_click_effect = click_effect
    streamer.is_streaming = True

    return Response(
        streamer.generate_frames(monitor),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/set_fps')
def set_fps():
    fps = request.args.get('fps', default=25, type=int)
    streamer.set_fps(fps)
    return {'success': True, 'target_fps': streamer.target_fps}


@app.route('/get_fps')
def get_fps():
    return {'actual_fps': streamer.actual_fps, 'target_fps': streamer.target_fps}


if __name__ == '__main__':
    print("=" * 60)
    print("🎮 Трансляция с НАСТРОЙКОЙ FPS запущена!")
    print("💡 Диапазон FPS: 1-60 кадров/секунду")
    print("🌐 Откройте в браузере: http://localhost:5000")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=False)