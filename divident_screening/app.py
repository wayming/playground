from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
import glob
from datetime import datetime
import uuid
from logger import logger, set_ticker

app = Flask(__name__)

# Ensure data directories exist
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, 'raw'), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, 'json'), exist_ok=True)

# Import our scraper and scorer
from asx_scraper import scrape_stock
from asx_scorer import ScoringSystem

# 内存缓存: symbol -> (timestamp, score_result)
_score_cache = {}
_cache_dir = os.path.join(DATA_DIR, 'cache')
os.makedirs(_cache_dir, exist_ok=True)

def _get_cache_path(symbol: str) -> str:
    return os.path.join(_cache_dir, f"{symbol}.json")

def _get_file_timestamp(json_file: str) -> float:
    """获取文件修改时间"""
    return os.path.getmtime(json_file)

def _load_cached_score(symbol: str, json_file: str) -> dict | None:
    """加载缓存的评分，如果缓存过期则返回 None"""
    cache_path = _get_cache_path(symbol)
    if not os.path.exists(cache_path):
        return None

    try:
        # 检查 JSON 文件是否比缓存更新
        json_mtime = _get_file_timestamp(json_file)
        cache_mtime = _get_file_timestamp(cache_path)

        if json_mtime > cache_mtime:
            # 数据文件更新了，需要重新计算
            return None

        with open(cache_path, 'r') as f:
            return json.load(f)
    except:
        return None

def _save_cached_score(symbol: str, score_result: dict):
    """保存评分到缓存"""
    cache_path = _get_cache_path(symbol)
    with open(cache_path, 'w', encoding='UTF8') as f:
        json.dump(score_result, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    symbol = data.get('symbol', '').upper().strip()

    # 设置 ticker 用于日志
    set_ticker(symbol)
    logger.info(f"Starting analysis for {symbol}")

    # Auto-detect industry from scraped data (not from user input)
    industry = None

    if not symbol:
        logger.warning("Empty symbol provided")
        return jsonify({'error': 'Please enter a stock symbol'}), 400

    # Create unique ID for this analysis
    analysis_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    try:
        # Check if data already exists (use latest json file)
        existing_files = glob.glob(os.path.join(DATA_DIR, 'json', f'{symbol}_*.json'))
        json_data = None
        if existing_files:
            # Use latest existing data
            latest_file = sorted(existing_files)[-1]
            with open(latest_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            logger.info(f"Using cached data for {symbol}: {latest_file}")
        else:
            # Scrape new data
            logger.info(f"Scraping new data for {symbol}")
            json_data = scrape_stock(symbol)
            logger.info(f"Scraping completed for {symbol}")

        if not json_data or not json_data.get('income_statement'):
            return jsonify({'error': f'Could not find data for {symbol}. Make sure it\'s a valid ASX stock.'}), 404

        # Only save if we scraped new data (not from cache)
        is_cached = bool(existing_files)
        if not is_cached:
            # Save JSON data
            json_file = os.path.join(DATA_DIR, 'json', f'{symbol}_{timestamp}_{analysis_id}.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
        else:
            # Use existing json file path
            json_file = sorted(existing_files)[-1]
            raw_file = None

        # Auto-detect industry from scraped data
        industry = detect_industry(symbol, json_data)
        logger.info(f"Detected industry: {industry}")

        # Score the stock
        scorer = ScoringSystem(json_data)
        score_result = scorer.score(industry)
        logger.info(f"Scoring completed - Total: {score_result.total_score}/{score_result.max_score}")

        # Prepare response
        response = {
            'symbol': symbol,
            'industry': industry,
            'analysis_id': analysis_id,
            'timestamp': timestamp,
            'score': {
                'total': round(score_result.total_score, 1),
                'max': score_result.max_score,
                'percentage': round(score_result.total_score / score_result.max_score * 100, 1) if score_result.max_score > 0 else 0
            },
            'details': score_result.details,
            'passed_checks': score_result.passed_checks,
            'failed_checks': score_result.failed_checks,
            'ratios': {k: v for k, v in json_data.get('ratios', {}).items()
                      if isinstance(v, dict) and 'Current' in v},
            'json_file': json_file
        }

        # 更新缓存
        cache_data = {
            'symbol': symbol,
            'industry': industry,
            'score': response['score'],
            'details': score_result.details,
            'timestamp': timestamp
        }
        _save_cached_score(symbol, cache_data)

        logger.info(f"Analysis completed successfully for {symbol}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Analysis failed for {symbol}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def history():
    """List all previously analyzed stocks with scores - 使用缓存避免重复计算"""
    json_dir = os.path.join(DATA_DIR, 'json')
    files = sorted(os.listdir(json_dir), reverse=True) if os.path.exists(json_dir) else []

    # Group by symbol, keep latest
    latest = {}
    for f in files:
        if f.endswith('.json'):
            # 修复文件名解析 - 处理 CBA_20260314_073143_839079f8.json 格式
            parts = f.rsplit('_', 3)
            if len(parts) >= 4:
                symbol = parts[0]
                if symbol not in latest:
                    latest[symbol] = f

    # For each stock, read from cache or compute score
    result = []
    for symbol, f in latest.items():
        json_path = os.path.join(json_dir, f)

        # 尝试从缓存加载
        cached = _load_cached_score(symbol, json_path)
        if cached:
            result.append(cached)
            continue

        # 缓存不存在或过期，需要重新计算
        try:
            with open(json_path, 'r') as fp:
                data = json.load(fp)
            # Auto-detect industry from scraped data
            industry = detect_industry(symbol, data)
            scorer = ScoringSystem(data)
            score_result = scorer.score(industry)

            score_data = {
                'symbol': symbol,
                'industry': industry,
                'score': {
                    'total': round(score_result.total_score, 1),
                    'max': score_result.max_score,
                    'percentage': round(score_result.total_score / score_result.max_score * 100, 1) if score_result.max_score > 0 else 0
                },
                'details': score_result.details,
                'timestamp': f.split('_')[1] if len(f.split('_')) > 1 else 'unknown'
            }

            # 保存到缓存
            _save_cached_score(symbol, score_data)
            result.append(score_data)
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    return jsonify(result)


def map_industry_name(industry_name: str) -> str:
    """将 stockanalysis.com 的行业名称映射到内部行业类型"""
    if not industry_name:
        return 'materials'

    industry_lower = industry_name.lower()

    # Banks / Financial
    if 'bank' in industry_lower or 'financial' in industry_lower:
        return 'banks'

    # Materials / Mining / Metals
    if any(kw in industry_lower for kw in ['basic materials', 'metals', 'mining', 'gold', 'coal', 'steel', 'material']):
        return 'materials'

    # Infrastructure / Utilities / Energy / Oil / Gas
    if any(kw in industry_lower for kw in ['utilities', 'energy', 'oil', 'gas', 'infrastructure', 'regulated']):
        return 'infrastructure'

    # Healthcare
    if any(kw in industry_lower for kw in ['healthcare', 'biotechnology', 'pharmaceutical', 'medical']):
        return 'healthcare'

    # Telecom / Communication
    if any(kw in industry_lower for kw in ['telecom', 'communication']):
        return 'telecom'

    # Consumer
    if 'consumer' in industry_lower:
        return 'consumer_staples'

    # 默认
    return 'materials'


def detect_industry(symbol, json_data=None):
    """Auto-detect industry based on stockanalysis.com data, fallback to symbol lookup"""
    # 首先尝试从抓取的数据中获取行业信息
    if json_data and json_data.get('industry'):
        industry_info = json_data['industry']
        industry_name = industry_info.get('industry') or industry_info.get('sector')
        if industry_name:
            mapped = map_industry_name(industry_name)
            print(f"Detected industry from stockanalysis.com: {industry_name} -> {mapped}")
            return mapped
        
    # Fallback: 基于常见 ASX 股票代码检测
    banks = ['CBA', 'NAB', 'ANZ', 'WBC', 'MQG', 'BOQ', 'BEN', 'SUN', 'ZUR']
    materials = ['BHP', 'RIO', 'FMG', 'WSA', 'NCM', 'S32', 'LYC', 'AWC']
    infrastructure = ['APA', 'WDS', 'SCG', 'AST', 'CTD', 'DJI']
    healthcare = ['CSL', 'RHC', 'SHL', 'MSB', 'APE', 'FDV']
    telecom = ['TLS', 'TPG', 'HUB', 'DCN']

    # 清理 symbol - 移除 .AX 后缀和可能的路径
    symbol = symbol.upper().replace('.AX', '')
    # 如果包含下划线（来自文件名解析），只取第一部分
    if '_' in symbol:
        symbol = symbol.split('_')[0]

    if symbol in banks:
        return 'banks'
    elif symbol in materials:
        return 'materials'
    elif symbol in infrastructure:
        return 'infrastructure'
    elif symbol in healthcare:
        return 'healthcare'
    elif symbol in telecom:
        return 'telecom'
    else:
        return 'materials'  # default

@app.route('/data/json/<path:filename>')
def serve_json(filename):
    return send_from_directory(os.path.join(DATA_DIR, 'json'), filename)

@app.route('/data/raw/<path:filename>')
def serve_raw(filename):
    return send_from_directory(os.path.join(DATA_DIR, 'raw'), filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
