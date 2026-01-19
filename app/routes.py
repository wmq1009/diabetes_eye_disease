from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app.services.image_processor import ImageProcessor
from app.services.batch_processor import BatchProcessor

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/api/status')
def status():
    # 简化状态检查，仅返回系统就绪状态
    return jsonify({
        'connected': True,
        'available_models': ['n/a']
    })

@main_bp.route('/api/batch_process', methods=['POST'])
def batch_process():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': '请求数据不能为空'}), 400
        
        folder_path = data.get('folder_path')
        if not folder_path:
            return jsonify({'success': False, 'error': '请提供文件夹路径'}), 400
        
        options = data.get('options', {})
        
        # 创建批量处理器
        batch_processor = BatchProcessor()
        result = batch_processor.process_folder(folder_path, options)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
