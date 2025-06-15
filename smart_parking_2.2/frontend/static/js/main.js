// main.js
// 全局变量
let currentCameraId = 0;
let streamInterval = null;
let cameraListUpdater = null;
let isDrawing = false; // 添加绘图状态变量
let points = []; // 添加存储绘制点的数组
let parkingSpots = []; // 添加存储车位信息的数组

// DOM 元素
const loginBox = document.getElementById('loginBox');
const registerBox = document.getElementById('registerBox');
const mainPanel = document.getElementById('mainPanel');
const videoContainer = document.getElementById('videoContainer');

// 界面切换
document.getElementById('showRegister').addEventListener('click', (e) => {
    e.preventDefault();
    loginBox.classList.add('hidden');
    registerBox.classList.remove('hidden');
});

document.getElementById('showLogin').addEventListener('click', (e) => {
    e.preventDefault();
    registerBox.classList.add('hidden');
    loginBox.classList.remove('hidden');
});

// 退出功能
document.getElementById('logoutButton').addEventListener('click', async () => {
    const token = localStorage.getItem('token');
    const loading = showLoading();
    
    try {
        // 先停止所有定时器和视频流
        clearAllResources();
        
        if (token) {
            const response = await fetch('/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ camera_id: currentCameraId })
            });
            
            if (!response.ok) {
                throw new Error('登出失败');
            }
        }
        
        // 清理前端状态
        resetUIState();
        createNotification('已安全退出', 'success');
    } catch (error) {
        console.error('登出时发生错误:', error);
        createNotification('登出过程中发生错误，请刷新页面', 'error');
    } finally {
        hideLoading(loading);
    }
});

// 新增资源清理函数
function clearAllResources() {
    // 清理视频流相关资源
    const oldImg = document.getElementById('videoStream');
    if (oldImg) {
        oldImg.onerror = null;
        oldImg.src = '';
        oldImg.remove();
    }
    
    // 清理所有定时器
    if (streamInterval) clearInterval(streamInterval);
    if (cameraListUpdater) clearInterval(cameraListUpdater);
    streamInterval = null;
    cameraListUpdater = null;
}

// 新增UI状态重置函数
function resetUIState() {
    localStorage.removeItem('token');
    mainPanel.classList.add('hidden');
    document.querySelector('.auth-container').style.display = 'block';
    loginBox.classList.remove('hidden');
    registerBox.classList.add('hidden');
    
    // 清理摄像头控制面板
    const controls = document.querySelector('.camera-controls');
    if (controls) controls.remove();
}

// 视频流功能
function startVideoStream(token) {
    fetch('/available_cameras', {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(response => response.json())
    .then(data => {
        if(data.available_cameras.length === 0) {
            showError('没有可用的摄像头');
            return;
        }
        currentCameraId = data.current_camera;
        initVideoStream(token, currentCameraId);
        setupCameraControls(data.available_cameras);
        startAutoRecovery();

        cameraListUpdater = setInterval(() => {
            fetch('/available_cameras', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            .then(response => response.json())
            .then(data => {
                const controls = document.querySelector('.camera-controls');
                if (controls) controls.remove();
                setupCameraControls(data.available_cameras);
            });
        }, 10000);
    })
    .catch(error => {
        console.error('摄像头列表获取失败:', error);
        showError('无法获取摄像头信息');
    });
}

// 通知系统
function createNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    // 触发重排以启动动画
    notification.offsetHeight;
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 加载动画
function showLoading() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = '<div class="loading-spinner"></div>';
    document.body.appendChild(overlay);
    setTimeout(() => overlay.classList.add('show'), 0);
    return overlay;
}

function hideLoading(overlay) {
    overlay.classList.remove('show');
    setTimeout(() => overlay.remove(), 300);
}

// 登录功能 - 使用async/await方式，移除旧的then/catch版本
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
        createNotification('请输入用户名和密码', 'error');
        return;
    }

    const loading = showLoading();

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.msg || '登录失败');
        }

        localStorage.setItem('token', data.access_token);
        document.querySelector('.auth-container').style.display = 'none';
        mainPanel.classList.remove('hidden');
        createNotification('登录成功', 'success');
        startVideoStream(data.access_token);
    } catch (error) {
        createNotification(error.message || '登录失败，请稍后重试', 'error');
    } finally {
        hideLoading(loading);
    }
});

// 注册功能 - 使用async/await方式，移除旧的then/catch版本
document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;

    if (!username || !password) {
        createNotification('请输入用户名和密码', 'error');
        return;
    }

    const loading = showLoading();

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.msg === '注册成功') {
            createNotification('注册成功，请登录', 'success');
            registerBox.classList.add('hidden');
            loginBox.classList.remove('hidden');
        } else {
            createNotification(data.msg, 'error');
        }
    } catch (error) {
        createNotification('注册失败，请稍后重试', 'error');
    } finally {
        hideLoading(loading);
    }
});

// 修改视频流错误处理 - 合并两个initVideoStream函数
function initVideoStream(token, camId = 0) {
    const oldImg = document.getElementById('videoStream');
    if (oldImg) {
        oldImg.onerror = null;
        oldImg.src = '';
        oldImg.remove();
    }
    if (streamInterval) {
        clearInterval(streamInterval);
        streamInterval = null;
    }

    const img = document.createElement('img');
    img.id = 'videoStream';
    img.className = 'live-feed';
    const videoUrl = `/video_feed/${camId}?token=${token}&ts=${Date.now()}`;
    img.src = videoUrl;

    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    const reconnectDelay = 2000;
    let reconnectTimer = null;

    // 在initVideoStream函数中添加加载状态显示
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.textContent = '正在连接摄像头...';
    videoContainer.appendChild(loadingIndicator);
    
    // 合并两个onload处理程序
    img.onload = function() {
        // 移除加载指示器
        if (loadingIndicator) loadingIndicator.remove();
        // 初始化绘图画布
        initDrawingCanvas();
        // 加载车位信息
        loadParkingSpots();
    };

    img.onerror = function() {
        console.error(`视频流加载失败: ${videoUrl}，状态码: ${this.status || '未知'}`);
        if (reconnectAttempts >= maxReconnectAttempts) {
            createNotification(`摄像头 ${camId} 连接失败，请检查设备`, 'error');
            return;
        }
        reconnectAttempts++;
        console.log(`视频流中断，尝试重新连接(${reconnectAttempts}/${maxReconnectAttempts})...`);
        createNotification(`正在尝试重新连接摄像头 ${camId}...`, 'info');
        
        // 清除之前的重连定时器
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
        }
        
        // 使用指数退避策略
        const currentDelay = reconnectDelay * Math.pow(2, reconnectAttempts - 1);
        reconnectTimer = setTimeout(() => {
            this.src = `${videoUrl}&retry=${Date.now()}`;
        }, currentDelay);
    };

    videoContainer.appendChild(img);

    streamInterval = setInterval(() => {
        if (img.naturalWidth === 0) {
            console.log('心跳检测到画面丢失，刷新视频流...');
            img.src = `${videoUrl}&ping=${Date.now()}`;
        }
    }, 3000);
}

function setupCameraControls(cameras) {
    const controls = document.createElement('div');
    controls.className = 'camera-controls';

    cameras.forEach(camId => {
        const btn = document.createElement('button');
        btn.textContent = `摄像头 ${camId}`;
        btn.onclick = () => switchCamera(camId);
        controls.appendChild(btn);
    });

    videoContainer.prepend(controls);
}

function switchCamera(newCamId) {
    if (newCamId === currentCameraId) return;
    const token = localStorage.getItem('token');
    if (!token) return;
    initVideoStream(token, newCamId);
    currentCameraId = newCamId;
}

function startAutoRecovery() {
    setInterval(() => {
        const img = document.getElementById('videoStream');
        if (img && img.naturalWidth === 0) {
            console.log('自动恢复机制触发...');
            const token = localStorage.getItem('token');
            if (token) {
                initVideoStream(token, currentCameraId);
            }
        }
    }, 5000);
}

// 工具函数
function showError(message) {
    createNotification(message, 'error');
}

function showSuccess(message) {
    createNotification(message, 'success');
}

// 更新时间和日期
function updateTimeDate() {
    const now = new Date();
    
    // 更新时间
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    document.getElementById('currentTime').textContent = `${hours}:${minutes}:${seconds}`;
    
    // 更新日期
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
    const weekday = weekdays[now.getDay()];
    document.getElementById('currentDate').textContent = `${year}年${month}月${day}日 ${weekday}`;
}

// 更新车位信息
function updateParkingInfo() {
    // 计算车位统计信息
    const totalSpots = parkingSpots ? parkingSpots.length : 0;
    const occupiedSpots = parkingSpots ? parkingSpots.filter(spot => spot.occupied).length : 0;
    const availableSpots = totalSpots - occupiedSpots;
    
    // 更新DOM元素
    document.getElementById('totalSpots').textContent = totalSpots;
    document.getElementById('occupiedSpots').textContent = occupiedSpots;
    document.getElementById('availableSpots').textContent = availableSpots;
}

// 添加事件监听器
document.addEventListener('DOMContentLoaded', function() {
    const addParkingBtn = document.getElementById('addParkingBtn');
    const clearParkingBtn = document.getElementById('clearParkingBtn');
    
    // 初始化时间显示并设置定时器每秒更新
    updateTimeDate();
    setInterval(updateTimeDate, 1000);
    
    if (addParkingBtn) {
        addParkingBtn.addEventListener('click', startAddingSpot);
    }
    
    if (clearParkingBtn) {
        clearParkingBtn.addEventListener('click', async function() {
            if (confirm('确定要清除所有车位吗？')) {
                try {
                    const response = await fetch(`/parking_spots?camera_id=${currentCameraId}`, {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    });
                    
                    if (response.ok) {
                        showSuccess('所有车位已清除');
                        parkingSpots = [];
                        drawParkingSpots();
                        updateParkingInfo();
                    } else {
                        showError('清除车位失败');
                    }
                } catch (error) {
                    showError('清除车位失败：' + error.message);
                }
            }
        });
    }
});

// 修改loadParkingSpots函数，添加车位信息更新
async function loadParkingSpots() {
    try {
        const response = await fetch(`/parking_spots?camera_id=${currentCameraId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            parkingSpots = await response.json();
            drawParkingSpots();
            updateParkingInfo(); // 更新车位信息显示
        }
    } catch (error) {
        showError('加载车位信息失败：' + error.message);
    }
}

// 修改saveParkingSpot函数，添加车位信息更新
async function saveParkingSpot() {
    const spotName = prompt('请输入车位编号：');
    if (!spotName) {
        cancelAddingSpot();
        return;
    }
    
    try {
        console.log('保存车位数据:', {
            name: spotName,
            coordinates: points,
            camera_id: currentCameraId
        });
        
        const response = await fetch('/parking_spots', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                name: spotName,
                coordinates: points,
                camera_id: currentCameraId
            })
        });
        
        if (response.ok) {
            showSuccess('车位添加成功');
            loadParkingSpots(); // 这将同时更新绘图和车位信息
        } else {
            const errorData = await response.json();
            console.error('车位添加失败:', errorData);
            showError('车位添加失败: ' + (errorData.error || '未知错误'));
        }
    } catch (error) {
        console.error('车位添加异常:', error);
        showError('车位添加失败：' + error.message);
    } finally {
        cancelAddingSpot();
    }
}

// 绘制所有车位
function drawParkingSpots() {
    const canvas = document.getElementById('drawingCanvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    parkingSpots.forEach(spot => {
        ctx.beginPath();
        ctx.moveTo(spot.coordinates[0].x, spot.coordinates[0].y);
        spot.coordinates.forEach(point => {
            ctx.lineTo(point.x, point.y);
        });
        ctx.closePath();
        ctx.strokeStyle = '#00ff00';
        ctx.stroke();
        
        // 添加车位编号和删除按钮
        ctx.fillStyle = '#00ff00';
        ctx.fillText(spot.name, spot.coordinates[0].x, spot.coordinates[0].y - 5);
    });
}

// 开始绘制
function startDrawing(e) {
    if (!isDrawing) return;
    
    const canvas = document.getElementById('drawingCanvas');
    const rect = canvas.getBoundingClientRect();
    
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // 清除之前的绘制
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 重新绘制已有的车位
    drawParkingSpots();
}

// 完成绘制
function finishDrawing() {
    if (!isDrawing) return;
    
    if (points.length === 4) {
        // 完成四个点的绘制，保存车位
        saveParkingSpot();
    }
}

// 清除画布
function clearCanvas() {
    const canvas = document.getElementById('drawingCanvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 重新绘制已有的车位
    drawParkingSpots();
}

// 开始添加车位
function startAddingSpot() {
    isDrawing = true;
    points = [];
    
    // 显示取消按钮
    const cancelBtn = document.getElementById('cancelSpotBtn');
    if (cancelBtn) cancelBtn.style.display = 'inline-block';
    
    // 设置画布事件监听
    const canvas = document.getElementById('drawingCanvas');
    canvas.addEventListener('click', addPoint);
    
    // 提示用户
    createNotification('请在视频上点击4个点来定义车位区域', 'info');
}

// 添加点
function addPoint(e) {
    if (!isDrawing) return;
    
    const canvas = document.getElementById('drawingCanvas');
    const rect = canvas.getBoundingClientRect();
    
    // 计算相对于canvas的坐标，考虑缩放因素
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;
    
    points.push({x, y});
    
    // 绘制当前点
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ff0000';
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI * 2);
    ctx.fill();
    
    // 如果已经有多个点，绘制连线
    if (points.length > 1) {
        ctx.strokeStyle = '#ff0000';
        ctx.beginPath();
        ctx.moveTo(points[points.length - 2].x, points[points.length - 2].y);
        ctx.lineTo(x, y);
        ctx.stroke();
    }
    
    // 如果已经有4个点，自动完成绘制
    if (points.length === 4) {
        // 连接第一个点和最后一个点
        ctx.beginPath();
        ctx.moveTo(points[3].x, points[3].y);
        ctx.lineTo(points[0].x, points[0].y);
        ctx.stroke();
        
        // 完成绘制
        finishDrawing();
    }
}

// 取消添加车位
function cancelAddingSpot() {
    isDrawing = false;
    points = [];
    
    // 隐藏取消按钮
    const cancelBtn = document.getElementById('cancelSpotBtn');
    if (cancelBtn) cancelBtn.style.display = 'none';
    
    // 移除画布事件监听
    const canvas = document.getElementById('drawingCanvas');
    canvas.removeEventListener('click', addPoint);
    
    // 清除画布上的临时绘制
    clearCanvas();
}

// 初始化绘图画布
function initDrawingCanvas() {
    const videoImg = document.getElementById('videoStream');
    if (!videoImg) return;
    
    // 创建或获取画布
    let canvas = document.getElementById('drawingCanvas');
    if (!canvas) {
        canvas = document.createElement('canvas');
        canvas.id = 'drawingCanvas';
        canvas.className = 'drawing-canvas';
        const videoWrapper = document.getElementById('videoWrapper');
        if (videoWrapper) {
            videoWrapper.appendChild(canvas);
        } else {
            videoContainer.appendChild(canvas);
        }
    }
    
    // 等待视频加载完成后设置画布大小
    if (videoImg.complete) {
        canvas.width = videoImg.naturalWidth || videoImg.width;
        canvas.height = videoImg.naturalHeight || videoImg.height;
    } else {
        videoImg.onload = function() {
            canvas.width = videoImg.naturalWidth || videoImg.width;
            canvas.height = videoImg.naturalHeight || videoImg.height;
        };
    }
    
    // 重置绘图状态
    isDrawing = false;
    points = [];
    
    // 隐藏取消按钮
    const cancelBtn = document.getElementById('cancelSpotBtn');
    if (cancelBtn) cancelBtn.style.display = 'none';
}