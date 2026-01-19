import cv2
import pytesseract
import re
from datetime import datetime
import os
from app.services.ollama_client import OllamaClient

class TextExtractor:
    def __init__(self):
        # 初始化Ollama客户端
        self.ollama_client = OllamaClient(model='qwen3-vl:4b')
        # 检查Ollama连接
        if self.ollama_client.check_connection():
            print('Ollama 大模型连接成功')
        else:
            print('警告: Ollama 大模型未连接，请确保Ollama服务正在运行')
    
    def extract_info(self, image_path):
        """从图片中提取姓名和日期"""
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                raise Exception(f"文件不存在: {image_path}")
            
            # 检查文件大小
            if os.path.getsize(image_path) == 0:
                raise Exception("文件为空")
            
            # 1. 首先尝试使用Ollama大模型提取信息
            name = None
            date = None
            extracted_text = ""
            
            # 构建提取姓名和日期的prompt
            prompt = "请从这张图片中提取出姓名和日期。输出格式为：\n姓名：[姓名]\n日期：[日期]\n\n只需要提取的信息，不要其他多余的文字。"
            
            # 使用Ollama分析图片
            try:
                ollama_response = self.ollama_client.analyze_image(image_path, prompt)
                extracted_text = f"[Ollama]: {ollama_response}"
                
                # 解析Ollama的响应
                if ollama_response and not ollama_response.startswith('Error'):
                    name, date = self._parse_ollama_response(ollama_response)
            except Exception as e:
                extracted_text += f"[Ollama Error]: {str(e)}"
                # 继续执行，尝试其他方法
            
            # 2. 如果Ollama失败，尝试使用Tesseract OCR
            if not name or not date:
                try:
                    # 读取图片
                    image = cv2.imread(image_path)
                    if image is not None:
                        # 预处理图片以提高OCR accuracy
                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        
                        # 尝试多种预处理方法
                        preprocessing_methods = [
                            ('thresh', cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]),
                            ('blur', cv2.GaussianBlur(gray, (5, 5), 0)),
                            ('adaptive', cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)),
                            ('median', cv2.medianBlur(gray, 3))
                        ]
                        
                        for method_name, processed_image in preprocessing_methods:
                            try:
                                text = pytesseract.image_to_string(processed_image, lang='chi_sim+eng')
                                if text:
                                    extracted_text += f"[{method_name}]: {text}\n"
                                    # 尝试从OCR文本中提取信息
                                    if not name or not date:
                                        temp_name = self._extract_name(text)
                                        temp_date = self._extract_date(text)
                                        if temp_name:
                                            name = temp_name
                                        if temp_date:
                                            date = temp_date
                            except Exception as e:
                                pass
                except Exception as e:
                    pass
            
            # 3. 如果所有方法都失败，尝试从文件名和文件元数据中提取信息
            if not name or not date:
                name_from_file, date_from_file = self._extract_from_file_info(image_path)
                if not name:
                    name = name_from_file
                if not date:
                    date = date_from_file
            
            return {
                'name': name,
                'date': date,
                'extracted_text': extracted_text
            }
            
        except Exception as e:
            # 即使出现异常，也尝试从文件信息中提取
            try:
                name_from_file, date_from_file = self._extract_from_file_info(image_path)
                return {
                    'name': name_from_file,
                    'date': date_from_file,
                    'error': str(e)
                }
            except:
                return {
                    'name': None,
                    'date': None,
                    'error': str(e)
                }
    
    def _parse_ollama_response(self, response):
        """解析Ollama大模型的响应，提取姓名和日期"""
        name = None
        date = None
        
        try:
            # 尝试从响应中提取姓名
            name_match = re.search(r'姓名[：:]\s*([^\n]+)', response)
            if name_match:
                name = name_match.group(1).strip()
                # 清理姓名
                name = re.sub(r'[^\u4e00-\u9fa5A-Za-z\s]', '', name)
                name = name.strip()
            
            # 尝试从响应中提取日期
            date_match = re.search(r'日期[：:]\s*([^\n]+)', response)
            if date_match:
                date_str = date_match.group(1).strip()
                # 清理并标准化日期
                date = self._normalize_date(date_str)
            
            # 如果没有找到标准格式，尝试直接从响应中提取
            if not name:
                # 尝试提取中文姓名
                chinese_names = re.findall(r'[\u4e00-\u9fa5]{2,4}', response)
                if chinese_names:
                    name = max(chinese_names, key=len)
            
            if not date:
                # 尝试提取日期
                date = self._extract_date(response)
            
        except Exception as e:
            pass
        
        return name, date
    
    def _extract_from_file_info(self, image_path):
        """从文件名和文件元数据中提取信息"""
        name = None
        date = None
        
        try:
            # 从文件名中提取信息
            filename = os.path.basename(image_path)
            filename_without_ext = os.path.splitext(filename)[0]
            
            # 尝试从文件名中提取日期
            date_patterns = [
                r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
                r'(\d{8})',  # 8位数字日期
                r'(\d{4})[/-\.](\d{2})[/-\.](\d{2})',  # YYYY-MM-DD
                r'(\d{2})[/-\.](\d{2})[/-\.](\d{4})',  # MM-DD-YYYY
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, filename_without_ext)
                if matches:
                    for match in matches:
                        if isinstance(match, tuple):
                            if len(match) == 3:
                                if len(match[0]) == 4:
                                    year, month, day = match
                                else:
                                    month, day, year = match
                                if self._is_valid_date(year, month, day):
                                    date = f"{year}{month}{day}"
                                    break
                        elif len(match) == 8:
                            year = match[:4]
                            month = match[4:6]
                            day = match[6:]
                            if self._is_valid_date(year, month, day):
                                date = match
                                break
                    if date:
                        break
            
            # 从文件名中提取可能的姓名
            # 移除日期部分后尝试提取姓名
            if date:
                filename_clean = re.sub(date, '', filename_without_ext)
            else:
                filename_clean = filename_without_ext
            
            # 清理文件名
            filename_clean = re.sub(r'[\d_\-\.]+', ' ', filename_clean)
            filename_clean = filename_clean.strip()
            
            # 尝试提取中文姓名
            chinese_names = re.findall(r'[\u4e00-\u9fa5]{2,4}', filename_clean)
            if chinese_names:
                name = max(chinese_names, key=len)
            
            # 尝试提取英文姓名
            elif filename_clean:
                # 简单的英文姓名提取
                name_candidates = re.findall(r'[A-Za-z]+', filename_clean)
                if name_candidates:
                    name = ' '.join(name_candidates)
            
            # 如果还是没有提取到姓名，使用文件名（不含扩展名）作为姓名
            if not name:
                name = filename_without_ext
            
            # 从文件元数据中提取日期
            if not date:
                try:
                    # 获取文件创建时间
                    create_time = os.path.getctime(image_path)
                    date_obj = datetime.fromtimestamp(create_time)
                    date = date_obj.strftime('%Y%m%d')
                except Exception as e:
                    pass
            
        except Exception as e:
            pass
        
        return name, date
    
    def _extract_name(self, text):
        """从文本中提取姓名"""
        # 增强的姓名提取规则
        name_patterns = [
            r'姓名[:：]\s*([\u4e00-\u9fa5]+)',
            r'名字[:：]\s*([\u4e00-\u9fa5]+)',
            r'Name[:：]\s*([A-Za-z\s]+)',
            r'Patient[:：]\s*([A-Za-z\s]+)',
            r'患者[:：]\s*([\u4e00-\u9fa5]+)',
            r'[\u4e00-\u9fa5]{2,4}'  # 2-4个中文字符
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    name = match.strip()
                    # 清理姓名
                    name = re.sub(r'[^\u4e00-\u9fa5A-Za-z\s]', '', name)
                    name = name.strip()
                    if len(name) >= 2:
                        return name
        
        # 尝试从所有文本中提取可能的姓名
        # 寻找连续的中文字符或英文字符
        chinese_names = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        if chinese_names:
            return max(chinese_names, key=len)
        
        # 尝试英文姓名
        english_names = re.findall(r'[A-Z][a-z]+\s+[A-Z][a-z]+', text)
        if english_names:
            return english_names[0]
        
        return None
    
    def _extract_date(self, text):
        """从文本中提取日期"""
        # 增强的日期提取规则
        date_patterns = [
            r'(\d{4})[/-\.](\d{2})[/-\.](\d{2})',  # YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD
            r'(\d{2})[/-\.](\d{2})[/-\.](\d{4})',  # MM-DD-YYYY, MM/DD/YYYY, MM.DD.YYYY
            r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
            r'(\d{8})',  # 8位数字日期
            r'(\d{2})[/-\.](\d{2})[/-\.](\d{2})',  # MM-DD-YY, MM/DD/YY
            r'日期[:：]\s*(\d{4}[/-\.]\d{2}[/-\.]\d{2})',  # 日期: YYYY-MM-DD
            r'Date[:：]\s*(\d{2}[/-\.]\d{2}[/-\.]\d{4})',  # Date: MM/DD/YYYY
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        if len(match) == 3:
                            # 处理 YYYY-MM-DD 或 MM-DD-YYYY 格式
                            if len(match[0]) == 4:
                                # YYYY-MM-DD
                                year, month, day = match
                            else:
                                # MM-DD-YYYY
                                month, day, year = match
                            
                            # 验证日期有效性
                            if self._is_valid_date(year, month, day):
                                return f"{year}{month}{day}"
                        elif len(match) == 1:
                            # 处理完整日期字符串
                            date_str = match[0]
                            # 清理日期字符串
                            cleaned_date = re.sub(r'[^\d]', '', date_str)
                            if len(cleaned_date) == 8:
                                year = cleaned_date[:4]
                                month = cleaned_date[4:6]
                                day = cleaned_date[6:]
                                if self._is_valid_date(year, month, day):
                                    return cleaned_date
                    else:
                        # 处理单个匹配
                        date_str = match
                        cleaned_date = re.sub(r'[^\d]', '', date_str)
                        if len(cleaned_date) == 8:
                            year = cleaned_date[:4]
                            month = cleaned_date[4:6]
                            day = cleaned_date[6:]
                            if self._is_valid_date(year, month, day):
                                return cleaned_date
                        elif len(cleaned_date) == 6:
                            # 处理 YYMMDD 格式
                            year = '20' + cleaned_date[:2]
                            month = cleaned_date[2:4]
                            day = cleaned_date[4:]
                            if self._is_valid_date(year, month, day):
                                return year + month + day
        
        return None
    
    def _is_valid_date(self, year, month, day):
        """验证日期是否有效"""
        try:
            # 确保月份和日期是两位数
            month = month.zfill(2)
            day = day.zfill(2)
            datetime(int(year), int(month), int(day))
            return True
        except:
            return False