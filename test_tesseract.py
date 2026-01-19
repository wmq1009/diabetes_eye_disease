import pytesseract
from PIL import Image
import cv2

# 测试Tesseract OCR
print('正在测试Tesseract OCR...')

# 打印Tesseract版本
try:
    print(f'Tesseract版本: {pytesseract.get_tesseract_version()}')
except Exception as e:
    print(f'获取Tesseract版本失败: {e}')

# 打印Tesseract命令路径
try:
    print(f'Tesseract命令路径: {pytesseract.pytesseract.tesseract_cmd}')
except Exception as e:
    print(f'获取Tesseract命令路径失败: {e}')

# 测试简单的文本提取
try:
    # 创建一个简单的测试图像
    import numpy as np
    test_image = np.zeros((100, 400, 3), dtype=np.uint8)
    test_image[:] = 255  # 白色背景
    
    # 在图像上绘制文本
    cv2.putText(test_image, '测试文本 Test Text', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # 保存测试图像
    cv2.imwrite('test_image.png', test_image)
    print('创建测试图像成功')
    
    # 使用Tesseract提取文本
    extracted_text = pytesseract.image_to_string('test_image.png', lang='chi_sim+eng')
    print(f'提取的文本: "{extracted_text.strip()}"')
    
    if extracted_text.strip():
        print('Tesseract OCR 工作正常!')
    else:
        print('Tesseract OCR 未能提取文本')
        
except Exception as e:
    print(f'Tesseract OCR 测试失败: {e}')

# 测试上传的图片
try:
    import os
    uploads_dir = 'uploads'
    image_files = [f for f in os.listdir(uploads_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if image_files:
        test_image_path = os.path.join(uploads_dir, image_files[0])
        print(f'测试上传的图片: {test_image_path}')
        
        # 使用Tesseract提取文本
        extracted_text = pytesseract.image_to_string(test_image_path, lang='chi_sim+eng')
        print(f'从上传图片提取的文本: "{extracted_text.strip()}"')
        
        if extracted_text.strip():
            print('成功从上传图片提取文本!')
        else:
            print('未能从上传图片提取文本')
    else:
        print('上传目录中没有图片文件')
        
except Exception as e:
    print(f'测试上传图片失败: {e}')
