document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const statusContainer = document.getElementById('status-container');
    const resultContainer = document.getElementById('result-container');
    const progressBar = document.getElementById('progress-bar');
    const statusText = document.getElementById('status-text');
    const downloadBtn = document.getElementById('download-btn');
    const errorMessage = document.getElementById('error-message');

    // 文件对象
    let selectedFile = null;
    // 生成的文件名
    let generatedFileName = null;

    // 点击上传区域触发文件选择
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    // 拖拽事件处理
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('highlight');
    });

    uploadArea.addEventListener('dragleave', function() {
        uploadArea.classList.remove('highlight');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('highlight');
        
        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    // 文件选择处理
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length) {
            handleFileSelect(fileInput.files[0]);
        }
    });

    // 处理文件选择
    function handleFileSelect(file) {
        // 检查文件类型
        const fileType = file.name.split('.').pop().toLowerCase();
        if (!['ppt', 'pptx', 'pdf'].includes(fileType)) {
            showError('不支持的文件格式。请上传 PPT, PPTX 或 PDF 文件。');
            return;
        }

        // 检查文件大小 (限制为20MB)
        if (file.size > 20 * 1024 * 1024) {
            showError('文件大小超过限制。请上传小于20MB的文件。');
            return;
        }

        // 清除错误消息
        hideError();
        
        // 更新UI
        selectedFile = file;
        uploadArea.innerHTML = `
            <div class="upload-icon">
                <i class="bi bi-file-earmark"></i>
            </div>
            <p class="upload-text">${file.name}</p>
            <p class="file-types">${(file.size / 1024 / 1024).toFixed(2)} MB</p>
        `;
        uploadBtn.disabled = false;
    }

    // 上传按钮点击事件
    uploadBtn.addEventListener('click', function() {
        if (!selectedFile) return;
        
        // 创建FormData对象
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        // 更新UI状态
        uploadBtn.disabled = true;
        statusContainer.classList.add('show');
        progressBar.style.width = '10%';
        
        // 更新状态文本
        statusText.textContent = '正在上传文件...';
        
        // 发送请求
        fetch('/process', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                // 根据HTTP状态码提供更具体的错误信息
                if (response.status === 400) {
                    throw new Error('请求参数错误，请检查文件格式');
                } else if (response.status === 413) {
                    throw new Error('文件太大，无法处理');
                } else if (response.status === 500) {
                    throw new Error('服务器内部错误，请稍后再试');
                } else {
                    throw new Error(`服务器响应错误 (${response.status})`);
                }
            }
            progressBar.style.width = '50%';
            statusText.textContent = '正在处理文件...';
            return response.json();
        })
        .then(data => {
            progressBar.style.width = '80%';
            statusText.textContent = '生成Word文档...';
            
            // 模拟处理时间，给用户更好的反馈
            setTimeout(() => {
                progressBar.style.width = '100%';
                statusText.textContent = '处理完成！';
                
                if (data.success) {
                    // 处理成功
                    generatedFileName = data.output_file;
                    
                    // 显示结果区域
                    setTimeout(() => {
                        statusContainer.classList.remove('show');
                        resultContainer.classList.add('show');
                    }, 500);
                } else {
                    // 处理失败
                    throw new Error(data.error || '处理文件时出错');
                }
            }, 800);
        })
        .catch(error => {
            console.error('Error:', error);
            progressBar.style.width = '0%';
            statusContainer.classList.remove('show');
            showError(error.message || '上传或处理文件时出错');
            uploadBtn.disabled = false;
            
            // 重置上传区域，允许用户重新选择文件
            resetUploadArea();
        });
    });

    // 下载按钮点击事件
    downloadBtn.addEventListener('click', function() {
        if (!generatedFileName) return;
        
        // 创建下载链接
        const downloadUrl = `/download/${generatedFileName}`;
        window.location.href = downloadUrl;
    });

    // 显示错误消息
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.add('show');
        
        // 3秒后自动隐藏错误消息
        setTimeout(() => {
            hideError();
        }, 5000);
    }

    // 隐藏错误消息
    function hideError() {
        errorMessage.textContent = '';
        errorMessage.classList.remove('show');
    }
    
    // 重置上传区域
    function resetUploadArea() {
        uploadArea.innerHTML = `
            <div class="upload-icon">
                <i class="bi bi-cloud-arrow-up"></i>
            </div>
            <p class="upload-text">点击或拖拽文件到此处上传</p>
            <p class="file-types">支持的文件格式: .ppt, .pptx, .pdf</p>
        `;
        fileInput.value = '';
        selectedFile = null;
    }
});