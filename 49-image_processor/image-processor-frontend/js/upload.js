const UploadHandler = {
    currentFile: null,
    currentProcessedId: null,
    
    init() {
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const browseBtn = document.getElementById('browseBtn');
        
        browseBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => this.handleFile(e.target.files[0]));
        
        // Drag and drop events
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                this.handleFile(file);
            } else {
                this.showToast('Please drop an image file', 'error');
            }
        });
        
        // Processing options
        document.getElementById('processBtn').addEventListener('click', () => this.processImage());
        
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => this.applyFilter(btn.dataset.filter));
        });
        
        // Rotate buttons
        document.querySelectorAll('.rotate-btn').forEach(btn => {
            btn.addEventListener('click', () => this.rotateImage(parseInt(btn.dataset.rotate)));
        });
        
        // Quality slider
        const qualitySlider = document.getElementById('quality');
        const qualityValue = document.getElementById('qualityValue');
        qualitySlider.addEventListener('input', () => {
            qualityValue.textContent = qualitySlider.value;
        });
    },
    
    handleFile(file) {
        if (!file.type.startsWith('image/')) {
            this.showToast('Please select an image file', 'error');
            return;
        }
        
        if (file.size > 10 * 1024 * 1024) {
            this.showToast('File too large (max 10MB)', 'error');
            return;
        }
        
        this.currentFile = file;
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('originalPreview').src = e.target.result;
        };
        reader.readAsDataURL(file);
        
        // Show processing options
        document.getElementById('processingOptions').classList.remove('hidden');
        document.getElementById('myImagesSection').classList.add('hidden');
        
        this.showToast('Image loaded! Configure processing options and click Process.', 'success');
    },
    
    async processImage() {
        if (!this.currentFile) {
            this.showToast('Please select an image first', 'error');
            return;
        }
        
        const loadingOverlay = document.getElementById('loadingOverlay');
        loadingOverlay.classList.remove('hidden');
        
        const formData = new FormData();
        formData.append('image', this.currentFile);
        
        // Get resize options
        const width = document.getElementById('resizeWidth').value;
        const height = document.getElementById('resizeHeight').value;
        const maintainAspect = document.getElementById('maintainAspect').checked;
        const quality = document.getElementById('quality').value;
        const generateThumbnails = document.getElementById('generateThumbnails').checked;
        
        if (width) formData.append('width', width);
        if (height) formData.append('height', height);
        formData.append('maintain_aspect', maintainAspect);
        formData.append('quality', quality);
        formData.append('generate_thumbnails', generateThumbnails);
        
        try {
            const result = await api.uploadImage(formData);
            this.showToast('Image processed successfully!', 'success');
            
            // Show processed preview
            if (result.processed && result.processed.url_full) {
                document.getElementById('processedPreview').src = result.processed.url_full;
                this.currentProcessedId = result.processed.id;
            } else {
                document.getElementById('processedPreview').src = result.original_url;
            }
            
            // Refresh images gallery
            await this.loadImages();
            
        } catch (error) {
            this.showToast(error.message, 'error');
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    },
    
    async applyFilter(filterType) {
        if (!this.currentProcessedId && !this.currentFile) {
            this.showToast('Please process an image first', 'error');
            return;
        }
        
        const loadingOverlay = document.getElementById('loadingOverlay');
        loadingOverlay.classList.remove('hidden');
        
        try {
            let imageId = this.currentProcessedId;
            if (!imageId) {
                // First process the image
                await this.processImage();
                imageId = this.currentProcessedId;
            }
            
            const result = await api.applyFilter(imageId, filterType);
            document.getElementById('processedPreview').src = result.url_full;
            this.showToast(`${filterType} filter applied!`, 'success');
            
        } catch (error) {
            this.showToast(error.message, 'error');
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    },
    
    async rotateImage(angle) {
        if (!this.currentProcessedId && !this.currentFile) {
            this.showToast('Please process an image first', 'error');
            return;
        }
        
        const loadingOverlay = document.getElementById('loadingOverlay');
        loadingOverlay.classList.remove('hidden');
        
        try {
            let imageId = this.currentProcessedId;
            if (!imageId) {
                await this.processImage();
                imageId = this.currentProcessedId;
            }
            
            const result = await api.rotateImage(imageId, angle);
            document.getElementById('processedPreview').src = result.url_full;
            this.showToast(`Image rotated ${angle}°!`, 'success');
            
        } catch (error) {
            this.showToast(error.message, 'error');
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    },
    
    async loadImages() {
        try {
            const images = await api.getImages();
            const container = document.getElementById('imagesGrid');
            
            if (!images.results || images.results.length === 0) {
                container.innerHTML = '<div class="col-span-full text-center text-gray-400 py-8">No images uploaded yet</div>';
                return;
            }
            
            container.innerHTML = images.results.map(img => `
                <div class="bg-gray-800 rounded-xl overflow-hidden group">
                    <img src="${img.url_full}" alt="${img.original_name}" class="w-full h-48 object-cover">
                    <div class="p-3">
                        <p class="text-sm truncate">${img.original_name}</p>
                        <p class="text-xs text-gray-400">${img.width}x${img.height} • ${(img.file_size / 1024).toFixed(1)}KB</p>
                        <div class="flex justify-between mt-2">
                            <button onclick="UploadHandler.downloadImage('${img.url_full}', '${img.original_name}')" class="text-xs text-purple-400 hover:text-purple-300">
                                <i class="fas fa-download"></i> Download
                            </button>
                            <button onclick="UploadHandler.deleteImage(${img.id})" class="text-xs text-red-400 hover:text-red-300">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Error loading images:', error);
        }
    },
    
    downloadImage(url, filename) {
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    },
    
    async deleteImage(imageId) {
        if (!confirm('Are you sure you want to delete this image?')) return;
        
        try {
            await api.deleteImage(imageId);
            this.showToast('Image deleted successfully!', 'success');
            await this.loadImages();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    },
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 animate-fade-in ${
            type === 'success' ? 'bg-green-600' : type === 'error' ? 'bg-red-600' : 'bg-blue-600'
        } text-white`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
};

window.UploadHandler = UploadHandler;