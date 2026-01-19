import requests
import json

# 测试批量处理API
def test_batch_process():
    url = 'http://127.0.0.1:5000/api/batch_process'
    
    # 测试数据
    data = {
        'folder_path': 'e:\\diabetes_eye_disease\\uploads',
        'options': {
            'overwrite': True,
            'recursive': True,
            'preview': True
        }
    }
    
    try:
        print('正在测试批量处理API...')
        print(f'测试文件夹: {data["folder_path"]}')
        
        response = requests.post(url, json=data, timeout=30)
        
        print(f'响应状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print('处理结果:')
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f'错误响应: {response.text}')
            
    except Exception as e:
        print(f'测试失败: {str(e)}')

if __name__ == '__main__':
    test_batch_process()