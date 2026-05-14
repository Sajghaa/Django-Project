from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import io
import os
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
import uuid

class ImageProcessor:
    """Image processing utilities"""
    
    @staticmethod
    def get_image_dimensions(image_path):
        """Get image dimensions"""
        with Image.open(image_path) as img:
            return img.size
    
    @staticmethod
    def resize_image(image_file, width=None, height=None, maintain_aspect=True, quality=85):
        """
        Resize image to specified dimensions
        """
        try:
            # Open image
            img = Image.open(image_file)
            
            # Get original dimensions
            original_width, original_height = img.size
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Calculate new dimensions
            if maintain_aspect and (width or height):
                if width and height:
                    # Calculate aspect ratios
                    width_ratio = width / original_width
                    height_ratio = height / original_height
                    ratio = min(width_ratio, height_ratio)
                    new_width = int(original_width * ratio)
                    new_height = int(original_height * ratio)
                elif width:
                    ratio = width / original_width
                    new_width = width
                    new_height = int(original_height * ratio)
                elif height:
                    ratio = height / original_height
                    new_width = int(original_width * ratio)
                    new_height = height
                else:
                    new_width, new_height = original_width, original_height
            elif width and height:
                new_width, new_height = width, height
            else:
                new_width, new_height = original_width, original_height
            
            # Resize image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            format = img.format or 'JPEG'
            resized_img.save(output, format=format, quality=quality, optimize=True)
            output.seek(0)
            
            return output, new_width, new_height, format
            
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")
    
    @staticmethod
    def apply_grayscale(image_file):
        """Convert image to grayscale"""
        img = Image.open(image_file)
        grayscale_img = ImageOps.grayscale(img)
        
        output = io.BytesIO()
        grayscale_img.save(output, format=img.format or 'JPEG', optimize=True)
        output.seek(0)
        
        return output
    
    @staticmethod
    def apply_blur(image_file, radius=2):
        """Apply Gaussian blur"""
        img = Image.open(image_file)
        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=radius))
        
        output = io.BytesIO()
        blurred_img.save(output, format=img.format or 'JPEG', optimize=True)
        output.seek(0)
        
        return output
    
    @staticmethod
    def apply_sharpen(image_file):
        """Apply sharpen filter"""
        img = Image.open(image_file)
        sharpened_img = img.filter(ImageFilter.SHARPEN)
        
        output = io.BytesIO()
        sharpened_img.save(output, format=img.format or 'JPEG', optimize=True)
        output.seek(0)
        
        return output
    
    @staticmethod
    def apply_sepia(image_file):
        """Apply sepia filter"""
        img = Image.open(image_file)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Apply sepia filter
        width, height = img.size
        pixels = img.load()
        
        for py in range(height):
            for px in range(width):
                r, g, b = img.getpixel((px, py))
                
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                pixels[px, py] = (min(tr, 255), min(tg, 255), min(tb, 255))
        
        output = io.BytesIO()
        img.save(output, format='JPEG', optimize=True)
        output.seek(0)
        
        return output
    
    @staticmethod
    def rotate_image(image_file, angle):
        """Rotate image by angle degrees"""
        img = Image.open(image_file)
        rotated_img = img.rotate(angle, expand=True)
        
        output = io.BytesIO()
        rotated_img.save(output, format=img.format or 'JPEG', optimize=True)
        output.seek(0)
        
        return output
    
    @staticmethod
    def flip_image(image_file, direction='horizontal'):
        """Flip image horizontally or vertically"""
        img = Image.open(image_file)
        
        if direction == 'horizontal':
            flipped_img = ImageOps.mirror(img)
        else:
            flipped_img = ImageOps.flip(img)
        
        output = io.BytesIO()
        flipped_img.save(output, format=img.format or 'JPEG', optimize=True)
        output.seek(0)
        
        return output
    
    @staticmethod
    def crop_image(image_file, left, top, right, bottom):
        """Crop image to specified rectangle"""
        img = Image.open(image_file)
        cropped_img = img.crop((left, top, right, bottom))
        
        output = io.BytesIO()
        cropped_img.save(output, format=img.format or 'JPEG', optimize=True)
        output.seek(0)
        
        return output
    
    @staticmethod
    def adjust_brightness(image_file, factor):
        """Adjust brightness (factor: 0.0 to 2.0)"""
        img = Image.open(image_file)
        enhancer = ImageEnhance.Brightness(img)
        adjusted_img = enhancer.enhance(factor)
        
        output = io.BytesIO()
        adjusted_img.save(output, format=img.format or 'JPEG', optimize=True)
        output.seek(0)
        
        return output
    
    @staticmethod
    def adjust_contrast(image_file, factor):
        """Adjust contrast (factor: 0.0 to 2.0)"""
        img = Image.open(image_file)
        enhancer = ImageEnhance.Contrast(img)
        adjusted_img = enhancer.enhance(factor)
        
        output = io.BytesIO()
        adjusted_img.save(output, format=img.format or 'JPEG', optimize=True)
        output.seek(0)
        
        return output
    
    @staticmethod
    def compress_image(image_file, quality=85):
        """Compress image by reducing quality"""
        img = Image.open(image_file)
        
        output = io.BytesIO()
        img.save(output, format=img.format or 'JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return output
    
    @staticmethod
    def convert_format(image_file, target_format='JPEG'):
        """Convert image to different format"""
        img = Image.open(image_file)
        
        # Convert RGBA to RGB for JPEG
        if target_format == 'JPEG' and img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1])
            img = rgb_img
        
        output = io.BytesIO()
        img.save(output, format=target_format, optimize=True)
        output.seek(0)
        
        return output, target_format.lower()