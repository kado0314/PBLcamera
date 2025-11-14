// 1. ファイル選択フィールドとプレビュー要素を取得
const imageInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');

// 2. ファイルが選択されたときのイベントリスナーを設定
imageInput.addEventListener('change', function(event) {
    const file = event.target.files[0];
    
    if (file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
        };
        
        reader.readAsDataURL(file);
    } else {
        imagePreview.src = '';
        imagePreview.style.display = 'none';
    }
});

// カメラ関連の要素取得
const openCameraBtn = document.getElementById('openCameraBtn');
const cameraArea = document.getElementById('cameraArea');
const cameraVideo = document.getElementById('cameraVideo');
const takePhotoBtn = document.getElementById('takePhotoBtn');

let cameraStream = null;

// ① 「撮影」ボタン → カメラ起動
openCameraBtn.addEventListener('click', async () => {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
        cameraVideo.srcObject = cameraStream;

        cameraArea.style.display = "block";
        imagePreview.style.display = "none";
    } catch (err) {
        alert("カメラを起動できませんでした: " + err);
    }
});

// ② 「写真を撮る」→ キャプチャ
takePhotoBtn.addEventListener('click', () => {
    if (!cameraStream) return;

    const canvas = document.createElement('canvas');
    canvas.width = cameraVideo.videoWidth;
    canvas.height = cameraVideo.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(cameraVideo, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL("image/jpeg");

    imagePreview.src = dataUrl;
    imagePreview.style.display = "block";

    fetch(dataUrl)
        .then(res => res.arrayBuffer())
        .then(buffer => {
            const file = new File([buffer], "camera.jpg", { type: "image/jpeg" });
    
            const dt = new DataTransfer();
            dt.items.add(file);

            imageInput.files = dt.files;
        });

    cameraStream.getTracks().forEach(track => track.stop());
    cameraArea.style.display = "none";
});
