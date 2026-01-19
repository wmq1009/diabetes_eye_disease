import os
import re
from datetime import datetime
from app.services.image_processor import ImageProcessor
from app.services.text_extractor import TextExtractor

class BatchProcessor:
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.text_extractor = TextExtractor()
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    
    def process_folder(self, folder_path, options):
        """处理文件夹中的所有图片"""
        if not os.path.exists(folder_path):
            return {'success': False, 'error': f'文件夹不存在: {folder_path}'}
        
        if not os.path.isdir(folder_path):
            return {'success': False, 'error': f'路径不是文件夹: {folder_path}'}
        
        # 提取选项
        overwrite = options.get('overwrite', True)
        recursive = options.get('recursive', True)
        preview = options.get('preview', True)
        
        # 收集所有图片文件
        image_files = self._collect_image_files(folder_path, recursive)
        
        if not image_files:
            return {'success': False, 'error': '文件夹中没有找到支持的图片文件'}
        
        # 处理每个图片
        results = []
        total_files = len(image_files)
        success_count = 0
        error_count = 0
        
        for i, image_path in enumerate(image_files):
            try:
                result = self._process_single_image(image_path, overwrite)
                results.append(result)
                if result['status'] == 'success':
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                results.append({
                    'original_name': os.path.basename(image_path),
                    'status': 'error',
                    'error': str(e)
                })
                error_count += 1
        
        # 返回处理结果
        return {
            'success': True,
            'total_files': total_files,
            'success_files': success_count,
            'error_files': error_count,
            'files': results
        }
    
    def _collect_image_files(self, folder_path, recursive):
        """收集文件夹中的所有图片文件"""
        image_files = []
        
        if recursive:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if self._is_supported_image(file):
                        image_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path) and self._is_supported_image(file):
                    image_files.append(file_path)
        
        return image_files
    
    def _is_supported_image(self, filename):
        """检查文件是否为支持的图片格式"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.supported_extensions
    
    def _process_single_image(self, image_path, overwrite):
        """处理单个图片文件"""
        original_name = os.path.basename(image_path)
        
        try:
            # 提取图片中的姓名和日期
            extracted_info = self.text_extractor.extract_info(image_path)
            
            if not extracted_info.get('name') or not extracted_info.get('date'):
                return {
                    'original_name': original_name,
                    'status': 'error',
                    'error': '无法从图片中提取姓名和日期'
                }
            
            # 生成新文件名
            new_filename = self._generate_new_filename(extracted_info, image_path)
            
            # 确保新文件名有正确的扩展名
            ext = os.path.splitext(original_name)[1]
            new_filename_with_ext = f"{new_filename}{ext}"
            
            # 生成新文件路径
            directory = os.path.dirname(image_path)
            new_path = os.path.join(directory, new_filename_with_ext)
            
            # 检查是否需要覆盖
            if os.path.exists(new_path) and not overwrite:
                return {
                    'original_name': original_name,
                    'status': 'error',
                    'error': '新文件名已存在，且未选择覆盖选项'
                }
            
            # 重命名文件
            os.rename(image_path, new_path)
            
            return {
                'original_name': original_name,
                'new_name': new_filename_with_ext,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'original_name': original_name,
                'status': 'error',
                'error': str(e)
            }
    
    def _generate_new_filename(self, extracted_info, original_path):
        """生成新的文件名，格式为：姓名_日期"""
        name = extracted_info.get('name', '未知').strip()
        date_str = extracted_info.get('date', '').strip()
        
        # 清理姓名，移除非法字符
        name = re.sub(r'[\\/:*?"<>|]', '', name)
        
        # 清理日期，确保格式正确
        date = self._normalize_date(date_str)
        
        # 生成基础文件名
        base_filename = f"{name}_{date}"
        
        # 确保文件名唯一
        directory = os.path.dirname(original_path)
        counter = 1
        new_filename = base_filename
        
        while True:
            # 检查文件是否存在
            test_path = os.path.join(directory, f"{new_filename}{os.path.splitext(original_path)[1]}")
            if not os.path.exists(test_path) or test_path == original_path:
                break
            
            # 如果存在，添加计数器
            new_filename = f"{base_filename}_{counter}"
            counter += 1
        
        return new_filename
    
    def _normalize_date(self, date_str):
        """标准化日期格式为YYYYMMDD"""
        # 尝试匹配不同的日期格式
        date_patterns = [
            (r'(\d{4})/(\d{2})/(\d{2})', '%Y/%m/%d'),
            (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),
            (r'(\d{4})\.(\d{2})\.(\d{2})', '%Y.%m.%d'),
            (r'(\d{2})/(\d{2})/(\d{4})', '%m/%d/%Y'),
            (r'(\d{2})-(\d{2})-(\d{4})', '%m-%d-%Y'),
            (r'(\d{2})\.(\d{2})\.(\d{4})', '%m.%d.%Y'),
            (r'(\d{4})(\d{2})(\d{2})', '%Y%m%d')
        ]
        
        for pattern, date_format in date_patterns:
            match = re.match(pattern, date_str)
            if match:
                try:
                    date_obj = datetime.strptime(date_str, date_format)
                    return date_obj.strftime('%Y%m%d')
                except:
                    continue
        
        # 如果无法解析，返回当前日期
        return datetime.now().strftime('%Y%m%d')