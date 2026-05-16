const UploadHandler = {
    currentFile: null,
    currentImageId: null,
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
        const processBtn = document.getElementById('processBtn');
        if (processBtn) {
            processBtn.addEventListener('click', () => this.processImage());
        }
        
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const filterType = btn.dataset.filter;
                if (filterType) this.applyFilter(filterType);
            });
        });
        
        // Rotate buttons
        document.querySelectorAll('.rotate-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const angle = parseInt(btn.dataset.rotate);
                if (angle) this.rotateImage(angle);
            });
        });
        
        // Quality slider
        const qualitySlider = document.getElementById('quality');
        const qualityValue = document.getElementById('qualityValue');
        if (qualitySlider) {
            qualitySlider.addEventListener('input', () => {
                qualityValue.textContent = qualitySlider.value;
            });
        }
    },
    
    handleFile(file) {
        if (!file || !file.type.startsWith('image/')) {
            this.showToast('Please select an image file', 'error');
            return;
        }
        
        if (file.size > 10 * 1024 * 1024) {
            this.showToast('File too large (max 10MB)', 'error');
            return;
        }
        
        this.currentFile = file;
        this.currentImageId = null;
        this.currentProcessedId = null;
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            const originalPreview = document.getElementById('originalPreview');
            if (originalPreview) originalPreview.src = e.target.result;
        };
        reader.readAsDataURL(file);
        
        // Clear processed preview
        const processedPreview = document.getElementById('processedPreview');
        if (processedPreview) processedPreview.src = '';
        
        // Show processing options
        const processingOptions = document.getElementById('processingOptions');
        if (processingOptions) processingOptions.classList.remove('hidden');
        
        const myImagesSection = document.getElementById('myImagesSection');
        if (myImagesSection) myImagesSection.classList.add('hidden');
        
        this.showToast('Image loaded! Configure processing options and click Process.', 'success');
    },
    
    async processImage() {
        if (!this.currentFile) {
            this.showToast('Please select an image first', 'error');
            return;
        }
        
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) loadingOverlay.classList.remove('hidden');
        
        const formData = new FormData();
        formData.append('image', this.currentFile);
        
        // Get resize options
        const width = document.getElementById('resizeWidth')?.value;
        const height = document.getElementById('resizeHeight')?.value;
        const maintainAspect = document.getElementById('maintainAspect')?.checked || true;
        const quality = document.getElementById('quality')?.value || 85;
        const generateThumbnails = document.getElementById('generateThumbnails')?.checked || false;
        
        if (width) formData.append('width', width);
        if (height) formData.append('height', height);
        formData.append('maintain_aspect', maintainAspect);
        formData.append('quality', quality);
        formData.append('generate_thumbnails', generateThumbnails);
        
        try {
            const result = await api.uploadImage(formData);
            this.showToast('Image processed successfully!', 'success');
            
            // Store the image IDs
            this.currentImageId = result.id;
            
            // Show processed preview
            const processedPreview = document.getElementById('processedPreview');
            if (processedPreview) {
                if (result.processed && result.processed.url_full) {
                    processedPreview.src = result.processed.url_full;
                    this.currentProcessedId = result.processed.id;
                } else if (result.url_full) {
                    processedPreview.src = result.url_full;
                }
            }
            
            // Refresh images gallery
            await this.loadImages();
            
            // Show my images section
            const myImagesSection = document.getElementById('myImagesSection');
            if (myImagesSection) myImagesSection.classList.remove('hidden');
            
        } catch (error) {
            console.error('Process error:', error);
            this.showToast(error.message || 'Failed to process image', 'error');
        } finally {
            if (loadingOverlay) loadingOverlay.classList.add('hidden');
        }
    },
    
    async applyFilter(filterType) {
        // Use the processed image ID if available, otherwise use the original image ID
        const imageId = this.currentProcessedId || this.currentImageId;
        
        if (!imageId) {
            this.showToast('Please process an image first', 'error');
            return;
        }
        
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) loadingOverlay.classList.remove('hidden');
        
        try {
            const result = await api.applyFilter(imageId, filterType);
            
            // Update the processed preview
            const processedPreview = document.getElementById('processedPreview');
            if (processedPreview && result.url_full) {
                processedPreview.src = result.url_full;
            }
            
            // Update the processed ID for subsequent operations
            if (result.id) {
                this.currentProcessedId = result.id;
            }
            
            this.showToast(`${filterType} filter applied!`, 'success');
            
            // Refresh images gallery
            await this.loadImages();
            
        } catch (error) {
            console.error('Filter error:', error);
            this.showToast(error.message || `Failed to apply ${filterType} filter`, 'error');
        } finally {
            if (loadingOverlay) loadingOverlay.classList.add('hidden');
        }
    },
    
    async rotateImage(angle) {
        const imageId = this.currentProcessedId || this.currentImageId;
        
        if (!imageId) {
            this.showToast('Please process an image first', 'error');
            return;
        }
        
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) loadingOverlay.classList.remove('hidden');
        
        try {
            const result = await api.rotateImage(imageId, angle);
            
            const processedPreview = document.getElementById('processedPreview');
            if (processedPreview && result.url_full) {
                processedPreview.src = result.url_full;
            }
            
            if (result.id) {
                this.currentProcessedId = result.id;
            }
            
            this.showToast(`Image rotated ${angle}°!`, 'success');
            await this.loadImages();
            
        } catch (error) {
            console.error('Rotate error:', error);
            this.showToast(error.message || `Failed to rotate image`, 'error');
        } finally {
            if (loadingOverlay) loadingOverlay.classList.add('hidden');
        }
    },
    
    async loadImages() {
        try {
            const images = await api.getImages();
            const container = document.getElementById('imagesGrid');
            
            if (!container) return;
            
            if (!images.results || images.results.length === 0) {
                container.innerHTML = '<div class="col-span-full text-center text-gray-400 py-8">No images uploaded yet</div>';
                return;
            }
            
            container.innerHTML = images.results.map(img => `
                <div class="bg-gray-800 rounded-xl overflow-hidden group">
                    <img src="${img.url_full}" alt="${img.original_name}" class="w-full h-48 object-cover">
                    <div class="p-3">
                        <p class="text-sm truncate" title="${img.original_name}">${img.original_name.substring(0, 30)}${img.original_name.length > 30 ? '...' : ''}</p>
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
            this.showToast('Failed to load images', 'error');
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
            
            // Clear current selection if this was the active image
            if (this.currentImageId === imageId) {
                this.currentImageId = null;
                this.currentProcessedId = null;
                this.currentFile = null;
                const originalPreview = document.getElementById('originalPreview');
                const processedPreview = document.getElementById('processedPreview');
                if (originalPreview) originalPreview.src = '';
                if (processedPreview) processedPreview.src = '';
                const processingOptions = document.getElementById('processingOptions');
                if (processingOptions) processingOptions.classList.add('hidden');
            }
        } catch (error) {
            this.showToast(error.message || 'Failed to delete image', 'error');
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