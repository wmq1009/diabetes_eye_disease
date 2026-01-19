# 糖尿病眼病诊断系统

基于本地Ollama大模型的智能视网膜病变检测应用，通过分析眼底照片来诊断糖尿病视网膜病变。

## 功能特性

- 📷 图像上传与预览
- 🤖 基于Ollama大模型的智能诊断
- 👁️ 专业的糖尿病视网膜病变分析
- 📊 详细的诊断报告和医疗建议
- 🎨 现代化的用户界面

## 系统要求

- Python 3.8+
- Ollama (本地部署)
- 8GB+ RAM (用于运行大模型)

## 安装步骤

### 1. 安装Ollama

首先需要安装并启动Ollama服务：

**Windows:**
```bash
# 下载并安装Ollama
# 访问 https://ollama.ai/download 下载Windows版本
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

### 2. 下载视觉模型

启动Ollama后，下载支持图像分析的模型：

```bash
# 下载LLaVA模型（推荐）
ollama pull llava

# 或者下载其他视觉模型
ollama pull llava:13b
```

### 3. 安装Python依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 配置

编辑 `config.py` 文件以自定义配置：

```python
class Config:
    SECRET_KEY = 'your-secret-key'
    OLLAMA_BASE_URL = 'http://localhost:11434'  # Ollama服务地址
    OLLAMA_MODEL = 'llava'  # 使用的模型名称
    UPLOAD_FOLDER = 'uploads'  # 上传文件存储目录
```

## 运行应用

```bash
# 启动Flask应用
python run.py
```

应用将在 `http://localhost:5000` 启动。

## 使用方法

1. **启动Ollama服务**
   ```bash
   ollama serve
   ```

2. **启动Web应用**
   ```bash
   python run.py
   ```

3. **打开浏览器**
   访问 `http://localhost:5000`

4. **上传图像**
   - 点击上传区域或拖拽眼底照片
   - 支持格式：PNG, JPG, JPEG, GIF, BMP

5. **开始诊断**
   - 点击"开始诊断"按钮
   - 等待AI分析完成
   - 查看诊断结果和医疗建议

## 项目结构

```
diabetes_eye_disease/
├── app/
│   ├── __init__.py          # Flask应用工厂
│   ├── routes.py            # 路由定义
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_processor.py    # 图像处理
│   │   ├── ollama_client.py      # Ollama客户端
│   │   └── diagnosis_service.py  # 诊断服务
│   └── templates/
│       └── index.html       # 前端页面
├── uploads/                 # 上传文件存储
├── config.py               # 配置文件
├── requirements.txt         # Python依赖
└── run.py                  # 应用入口
```

## 技术栈

- **后端**: Flask
- **图像处理**: Pillow, NumPy
- **AI模型**: Ollama (LLaVA)
- **前端**: HTML, CSS, JavaScript

## 诊断结果说明

系统会提供以下诊断结果：

- **正常**: 未发现明显病变
- **轻度糖尿病视网膜病变**: 早期病变，需要定期检查
- **中度糖尿病视网膜病变**: 需要密切监测和治疗
- **重度糖尿病视网膜病变**: 需要立即就医
- **增殖性糖尿病视网膜病变**: 严重情况，需要紧急治疗

## 注意事项

⚠️ **重要声明**:

1. 本系统仅用于辅助诊断，不能替代专业医生的诊断
2. 诊断结果仅供参考，请务必咨询专业眼科医生
3. 系统的准确性取决于图像质量和模型性能
4. 请确保上传的是清晰的眼底照片

## 故障排除

### Ollama连接失败

- 确保Ollama服务正在运行: `ollama serve`
- 检查端口是否被占用
- 确认模型已下载: `ollama list`

### 图像上传失败

- 检查文件格式是否支持
- 确认文件大小不超过16MB
- 检查uploads目录权限

### 诊断速度慢

- 确保计算机有足够的内存
- 考虑使用更小的模型版本
- 关闭其他占用资源的程序

## 环境变量

可以通过环境变量配置应用：

```bash
# Windows
set OLLAMA_BASE_URL=http://localhost:11434
set OLLAMA_MODEL=llava

# Linux/macOS
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llava
```

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交问题和改进建议。

## 联系方式

如有问题，请通过GitHub Issues联系。
