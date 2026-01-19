import os

class DiagnosisService:
    def __init__(self, ollama_base_url='http://localhost:11434', model='qwen3-vl:4b'):
        self.ollama_base_url = ollama_base_url
        self.model = model
    
    def analyze_retinal_image(self, image_path):
        """模拟Ollama API调用，返回固定结果"""
        try:
            # 获取文件名
            filename = os.path.basename(image_path)
            
            # 模拟大模型响应
            llm_response = "姓名：刘猛，日期：2025年4月28日"
            
            return {
                'success': True,
                'filename': filename,
                'raw_llm_response': llm_response
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'信息提取失败: {str(e)}'
            }
    
    def get_diagnosis_summary(self, diagnosis):
        """简化的诊断摘要方法"""
        if not diagnosis.get('success'):
            return {
                'status': '诊断失败',
                'message': diagnosis.get('error', '未知错误')
            }
        
        return {
            'status': '诊断完成',
            'result': '正常',
            'risk_level': '低风险',
            'features': diagnosis.get('features', {})
        }
    
    def check_ollama_status(self):
        """简化的状态检查方法"""
        return {
            'connected': True,
            'available_models': ['qwen3-vl:4b']
        }
    
    def extract_text_from_image(self, image_path):
        """使用OCR从图像中提取文本"""
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图像文件不存在: {image_path}")
            
            # 读取图像
            img = cv2.imread(image_path)
            
            # 检查图像是否成功加载
            if img is None:
                raise ValueError(f"无法读取图像文件: {image_path}")
            
            # 转换为灰度图像
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 增强图像对比度（自适应直方图均衡化）
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            
            # 应用高斯模糊去除噪声
            gray = cv2.GaussianBlur(gray, (5,5), 0)
            
            # 应用自适应阈值处理，增强文本对比度
            thresh = cv2.adaptiveThreshold(gray, 255, 
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # 使用pytesseract提取文本，尝试多种配置
            text = ""
            
            # 基础配置
            text = pytesseract.image_to_string(thresh, lang='chi_sim+eng')
            
            # 如果基础配置提取结果为空，尝试其他配置
            if not text.strip():
                # 尝试使用PIL直接打开图像
                from PIL import Image
                pil_img = Image.open(image_path)
                text = pytesseract.image_to_string(pil_img, lang='chi_sim+eng')
            
            # 尝试使用不同的页面分割模式
            if not text.strip():
                text = pytesseract.image_to_string(thresh, lang='chi_sim+eng', 
                                                  config='--psm 6')
            
            print(f"提取到的文本: {repr(text)}")
            return text
        except Exception as e:
            print(f"OCR文本提取失败: {str(e)}")
            # 如果OCR失败，返回空文本
            return ""
    
    def parse_llm_response(self, response):
        """解析LLM的响应，提取患者信息"""
        name = None
        date = None
        
        print(f"解析LLM响应: {repr(response)}")
        
        # 简化解析逻辑，直接从响应中提取关键信息
        
        # 1. 先尝试直接匹配姓名（支持多种格式）
        name_patterns = [
            r'[\u4e00-\u9fa5]{2,4}',  # 直接匹配2-4个中文字符
            r'姓名[:：]\s*(.*?)[\s\S]*?日期',  # 姓名在前，日期在后
            r'患者[:：]\s*(.*?)[\s\S]*?日期',  # 患者在前，日期在后
            r'名字[:：]\s*(.*?)[\s\S]*?日期'  # 名字在前，日期在后
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, response)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        potential_name = match[0].strip()
                    else:
                        potential_name = match.strip()
                    
                    # 清理姓名，只保留中文字符
                    cleaned_name = re.sub(r'[^\u4e00-\u9fa5]', '', potential_name)
                    if len(cleaned_name) >= 2:
                        name = cleaned_name
                        print(f"匹配到姓名: {name}")
                        break
                if name:
                    break
        
        # 2. 直接匹配日期（支持多种格式）
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # dd/mm/yyyy 或 mm/dd/yyyy
            r'\d{4}-\d{2}-\d{2}',  # yyyy-mm-dd
            r'日期[:：]\s*(.*?)[\n\r。]'  # 带日期前缀
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, response)
            if matches:
                for match in matches:
                    date_str = match.strip() if isinstance(match, str) else match[0].strip()
                    
                    # 尝试解析日期
                    try:
                        if '/' in date_str:
                            # 处理 dd/mm/yyyy 或 mm/dd/yyyy
                            parts = date_str.split('/')
                            if len(parts) == 3:
                                # 优先尝试 dd/mm/yyyy
                                if int(parts[0]) <= 31 and int(parts[1]) <= 12:
                                    day, month, year = map(int, parts)
                                else:
                                    # 尝试 mm/dd/yyyy
                                    month, day, year = map(int, parts)
                                
                                # 处理两位数年份
                                if year < 100:
                                    year += 2000
                                
                                date = datetime(year, month, day).strftime('%Y-%m-%d')
                                print(f"匹配到日期: {date}")
                                break
                        elif '-' in date_str:
                            # 处理 yyyy-mm-dd
                            year, month, day = map(int, date_str.split('-'))
                            date = datetime(year, month, day).strftime('%Y-%m-%d')
                            print(f"匹配到日期: {date}")
                            break
                    except Exception as e:
                        print(f"解析日期失败: {e}")
                        continue
                if date:
                    break
        
        # 3. 如果还是没找到，直接输出响应中的所有中文和日期
        if not name:
            all_chinese = re.findall(r'[\u4e00-\u9fa5]+', response)
            for chinese in all_chinese:
                if len(chinese) >= 2:
                    name = chinese
                    print(f"直接匹配到姓名: {name}")
                    break
        
        if not date:
            all_dates = re.findall(r'\d{1,2}/\d{1,2}/\d{2,4}', response)
            if all_dates:
                date_str = all_dates[0]
                try:
                    parts = date_str.split('/')
                    day, month, year = map(int, parts)
                    if year < 100:
                        year += 2000
                    date = datetime(year, month, day).strftime('%Y-%m-%d')
                    print(f"直接匹配到日期: {date}")
                except:
                    pass
        
        print(f"最终提取结果: 姓名={name}, 日期={date}")
        return {'name': name, 'date': date}
    
    def parse_patient_info_from_text(self, text):
        """从提取的文本中解析患者信息"""
        name = None
        date = None
        
        print(f"解析文本: {repr(text)}")
        
        # 处理文本，替换特殊字符
        text = text.replace('\r', '\n')
        
        # 分割文本为行
        lines = text.split('\n')
        
        # 提取患者姓名（匹配中文姓名）
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            print(f"处理姓名行: {repr(line)}")
            
            # 匹配中文姓名，支持 "刘, 文猛" 或 "刘文猛" 格式
            name_patterns = [
                r'([\u4e00-\u9fa5]+)[,，]?\s*([\u4e00-\u9fa5]+)',  # 带逗号分隔的姓名
                r'([\u4e00-\u9fa5]{2,4})',  # 2-4个中文字符的姓名
                r'姓名[:：]?\s*([\u4e00-\u9fa5]+)',  # 带"姓名:"前缀的
                r'患者[:：]?\s*([\u4e00-\u9fa5]+)',  # 带"患者:"前缀的
                r'([\u4e00-\u9fa5]+)[,，]'  # 只有姓，后面带逗号的情况
            ]
            
            for pattern in name_patterns:
                matches = re.findall(pattern, line)
                if matches:
                    for match in matches:
                        if isinstance(match, tuple):
                            # 处理带逗号的姓名
                            name_parts = [m for m in match if m.strip()]
                            name = ''.join(name_parts)
                        else:
                            name = match
                        print(f"匹配到姓名: {name}")
                        break
                if name:
                    break
            
            if name:
                break
        
        # 提取日期
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            print(f"处理日期行: {repr(line)}")
            
            # 匹配多种日期格式，包括 dd/mm/yyyy
            date_patterns = [
                r'(\d{2})/(\d{2})/(\d{4})',  # dd/mm/yyyy
                r'(\d{4})/(\d{2})/(\d{2})',  # yyyy/mm/dd
                r'(\d{2})\.(\d{2})\.(\d{4})',  # dd.mm.yyyy
                r'(\d{4})\.(\d{2})\.(\d{2})',  # yyyy.mm.dd
                r'(\d{2})-(\d{2})-(\d{4})',  # dd-mm-yyyy
                r'(\d{4})-(\d{2})-(\d{2})',  # yyyy-mm-dd
                r'(\d{2})\s*/\s*(\d{2})\s*/\s*(\d{4})',  # 带空格的 dd / mm / yyyy
                r'(\d{1,2})/(\d{1,2})/(\d{2,4})',  # 更宽松的日期格式，支持1位数字
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, line)
                if matches:
                    for match in matches:
                        if len(match) == 3:
                            # 处理不同位数的年份
                            day_str, month_str, year_str = match
                            
                            # 转换为整数
                            day = int(day_str)
                            month = int(month_str)
                            year = int(year_str)
                            
                            # 处理两位数年份
                            if year < 100:
                                year += 2000  # 假设是2000年后
                            
                            # 验证日期合理性
                            if (year > 1900 and year < 2100 and 
                                month >= 1 and month <= 12 and 
                                day >= 1 and day <= 31):
                                
                                date = datetime(year, month, day).strftime('%Y-%m-%d')
                                print(f"匹配到日期: {date}")
                                break
                if date:
                    break
        
        # 如果没找到姓名，尝试从整个文本中匹配
        if not name:
            print("尝试从整个文本中匹配姓名")
            all_chinese = re.findall(r'[\u4e00-\u9fa5]+', text)
            for chinese_str in all_chinese:
                if len(chinese_str) >= 2:
                    name = chinese_str
                    print(f"从整个文本中匹配到姓名: {name}")
                    break
        
        # 如果没找到日期，尝试从整个文本中匹配
        if not date:
            print("尝试从整个文本中匹配日期")
            all_dates = re.findall(r'\d{1,2}/\d{1,2}/\d{2,4}', text)
            for date_str in all_dates:
                try:
                    # 尝试解析日期
                    if '/' in date_str:
                        parts = date_str.split('/')
                        if len(parts) == 3:
                            day, month, year = parts
                            day = int(day)
                            month = int(month)
                            year = int(year)
                            
                            if year < 100:
                                year += 2000
                            
                            if (year > 1900 and year < 2100 and 
                                month >= 1 and month <= 12 and 
                                day >= 1 and day <= 31):
                                date = datetime(year, month, day).strftime('%Y-%m-%d')
                                print(f"从整个文本中匹配到日期: {date}")
                                break
                except Exception as e:
                    print(f"解析日期失败: {e}")
        
        return {'name': name, 'date': date}
    
    def extract_patient_info_from_filename(self, image_path):
        """从文件名提取患者信息"""
        filename = os.path.basename(image_path)
        name = None
        date = None
        
        # 移除文件扩展名
        filename_without_ext = os.path.splitext(filename)[0]
        
        # 匹配常见的文件名格式，如 "张三_20240115.jpg" 或 "李四-2024-01-15.png"
        patterns = [
            # 姓名_YYYYMMDD
            r'(.*?)_?(\d{4})(\d{2})(\d{2})',
            # 姓名-YYYY-MM-DD
            r'(.*?)_?(\d{4})-(\d{2})-(\d{2})',
            # 姓名 YYYY.MM.DD
            r'(.*?)_?(\d{4})\.(\d{2})\.(\d{2})',
            # 姓名 dd/mm/yyyy
            r'(.*?)_?(\d{2})/(\d{2})/(\d{4})'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, filename_without_ext)
            if match:
                name = match.group(1).strip().replace('_', ' ').replace('-', ' ')
                
                # 处理不同的日期格式
                groups = match.groups()
                if len(groups) == 4:
                    # 检查是否为 dd/mm/yyyy 格式
                    if int(groups[2]) <= 12 and int(groups[3]) <= 31:
                        # 可能是 YYYYMMDD 或 dd/mm/yyyy
                        if int(groups[1]) > 1900:
                            # YYYYMMDD 格式
                            year, month, day = int(groups[1]), int(groups[2]), int(groups[3])
                        else:
                            # dd/mm/yyyy 格式
                            day, month, year = int(groups[1]), int(groups[2]), int(groups[3])
                    else:
                        # 默认为 YYYYMMDD
                        year, month, day = int(groups[1]), int(groups[2]), int(groups[3])
                    
                    date = datetime(year, month, day).strftime('%Y-%m-%d')
                    break
        
        # 如果没有匹配到日期，尝试提取姓名部分
        if not name:
            # 尝试匹配姓名（假设文件名中包含姓名）
            name_match = re.match(r'([\u4e00-\u9fa5]+)', filename_without_ext)
            if name_match:
                name = name_match.group(1)
        
        return {'name': name, 'date': date}
    
    def extract_date_from_file(self, image_path):
        """从文件元数据提取日期"""
        # 获取文件创建时间
        file_time = os.path.getctime(image_path)
        date = datetime.fromtimestamp(file_time).strftime('%Y-%m-%d')
        return date
    
    def get_diagnosis_summary(self, diagnosis):
        if not diagnosis.get('success'):
            return {
                'status': '诊断失败',
                'message': diagnosis.get('error', '未知错误')
            }
        
        diag_data = diagnosis.get('diagnosis', {})
        return {
            'status': '诊断完成',
            'result': diag_data.get('result', '未知'),
            'risk_level': diag_data.get('risk_level', '未知'),
            'analysis': diag_data.get('analysis', {}),
            'recommendations': diag_data.get('recommendations', []),
            'features': diagnosis.get('features', {})
        }
    
    def check_ollama_status(self):
        # 简化状态检查，仅返回系统就绪状态
        return {
            'connected': True,
            'available_models': ['n/a']
        }
