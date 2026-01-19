class FeatureToTextConverter:
    @staticmethod
    def convert_to_text(features):
        text_description = []
        
        text_description.append("眼底图像分析报告")
        text_description.append("=" * 50)
        
        text_description.append("\n【图像质量评估】")
        quality = features.get('image_quality', {})
        text_description.append(f"- 图像清晰度: {quality.get('sharpness', 0):.2f}")
        text_description.append(f"- 图像亮度: {quality.get('brightness', 0):.2f}")
        text_description.append(f"- 图像对比度: {quality.get('contrast', 0):.2f}")
        text_description.append(f"- 整体质量: {quality.get('quality', '未知')}")
        
        text_description.append("\n【视网膜血管分析】")
        vessels = features.get('blood_vessels', {})
        text_description.append(f"- 血管密度: {vessels.get('vessel_density', 0):.2f}%")
        text_description.append(f"- 血管形态: {vessels.get('vessel_pattern', '未知')}")
        abnormalities = vessels.get('abnormalities', [])
        if abnormalities and abnormalities[0] != '无明显异常':
            text_description.append(f"- 血管异常: {', '.join(abnormalities)}")
        else:
            text_description.append("- 血管异常: 无明显异常")
        
        text_description.append("\n【视盘分析】")
        disc = features.get('optic_disc', {})
        text_description.append(f"- 视盘检测: {'已检测到' if disc.get('detected', False) else '未检测到'}")
        text_description.append(f"- 视盘面积比例: {disc.get('area_ratio', 0):.2f}%")
        text_description.append(f"- 视盘状态: {disc.get('condition', '未知')}")
        text_description.append(f"- 视盘边缘: {disc.get('edges', '未知')}")
        
        text_description.append("\n【黄斑区分析】")
        macula = features.get('macula', {})
        text_description.append(f"- 黄斑亮度比: {macula.get('brightness_ratio', 0):.2f}")
        text_description.append(f"- 黄斑状态: {macula.get('condition', '未知')}")
        text_description.append(f"- 黄斑纹理: {macula.get('texture', '未知')}")
        
        text_description.append("\n【病变检测】")
        lesions = features.get('lesions', {})
        
        cotton_wool = lesions.get('cotton_wool_spots', {})
        text_description.append(f"- 棉絮斑: {'检测到' if cotton_wool.get('detected', False) else '未检测到'}")
        if cotton_wool.get('detected', False):
            text_description.append(f"  数量: {cotton_wool.get('count', 0)}")
            text_description.append(f"  严重程度: {cotton_wool.get('severity', '未知')}")
        
        neovascular = lesions.get('neovascularization', {})
        text_description.append(f"- 新生血管: {'检测到' if neovascular.get('detected', False) else '未检测到'}")
        if neovascular.get('detected', False):
            text_description.append(f"  数量: {neovascular.get('count', 0)}")
            text_description.append(f"  严重程度: {neovascular.get('severity', '未知')}")
        
        text_description.append("\n【其他异常】")
        
        exudates = features.get('exudates', {})
        text_description.append(f"- 硬性渗出: {'检测到' if exudates.get('detected', False) else '未检测到'}")
        if exudates.get('detected', False):
            text_description.append(f"  数量: {exudates.get('count', 0)}")
            text_description.append(f"  总面积: {exudates.get('total_area', 0):.2f} 像素")
            text_description.append(f"  严重程度: {exudates.get('severity', '未知')}")
        
        hemorrhages = features.get('hemorrhages', {})
        text_description.append(f"- 出血点: {'检测到' if hemorrhages.get('detected', False) else '未检测到'}")
        if hemorrhages.get('detected', False):
            text_description.append(f"  数量: {hemorrhages.get('count', 0)}")
            text_description.append(f"  总面积: {hemorrhages.get('total_area', 0):.2f} 像素")
            text_description.append(f"  严重程度: {hemorrhages.get('severity', '未知')}")
        
        microaneurysms = features.get('microaneurysms', {})
        text_description.append(f"- 微血管瘤: {'检测到' if microaneurysms.get('detected', False) else '未检测到'}")
        if microaneurysms.get('detected', False):
            text_description.append(f"  数量: {microaneurysms.get('count', 0)}")
            text_description.append(f"  严重程度: {microaneurysms.get('severity', '未知')}")
        
        return "\n".join(text_description)
    
    @staticmethod
    def generate_diagnosis_prompt(features_text):
        prompt = f"""
你是一位专业的眼科医生，专门负责糖尿病视网膜病变的诊断。请根据以下眼底图像分析报告，给出专业的诊断意见。

{features_text}

请按照以下格式回答：

诊断结果：[正常/轻度糖尿病视网膜病变/中度糖尿病视网膜病变/重度糖尿病视网膜病变/增殖性糖尿病视网膜病变]

详细分析：
请根据上述分析结果，详细说明视网膜的各个部分的情况，包括血管、视盘、黄斑区以及各种病变的发现情况。

风险评估：[低风险/中风险/高风险/极高风险]
请根据检测到的病变情况，评估患者的风险等级。

建议：[针对当前情况的医疗建议]
请给出具体的医疗建议，包括是否需要进一步检查、治疗方案建议、随访频率等。

请用中文回答，保持专业和准确。
"""
        return prompt
    
    @staticmethod
    def extract_diagnosis_from_response(response):
        import re
        
        diagnosis = {
            'result': '未知',
            'risk_level': '未知',
            'analysis': {},
            'recommendations': []
        }
        
        result_match = re.search(r'诊断结果[：:]\s*(.+?)(?:\n|$)', response)
        if result_match:
            diagnosis['result'] = result_match.group(1).strip()
        
        risk_match = re.search(r'风险评估[：:]\s*(.+?)(?:\n|$)', response)
        if risk_match:
            diagnosis['risk_level'] = risk_match.group(1).strip()
        
        recommendation_match = re.search(r'建议[：:]\s*(.+?)(?:\n|$)', response, re.DOTALL)
        if recommendation_match:
            diagnosis['recommendations'] = [rec.strip() for rec in recommendation_match.group(1).split('。') if rec.strip()]
        
        analysis_section = re.search(r'详细分析[：:](.+?)(?:风险评估|建议|$)', response, re.DOTALL)
        if analysis_section:
            diagnosis['analysis']['full_analysis'] = analysis_section.group(1).strip()
        
        return diagnosis
