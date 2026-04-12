#!/usr/bin/env python3
"""
ASX Stock Scoring System - 12刀打分体系

Thin wrapper，调用各个行业 scorer 模块进行评分，返回结构化数据。
图形展示由前端负责。
"""

import json
import argparse
import logging
from typing import Dict, Any, List
from dataclasses import dataclass, field

# Import scoring modules
from scorers.banks import calculate_banks_score
from scorers.materials import calculate_materials_score
from scorers.infrastructure import calculate_infrastructure_score
from scorers.consumer import calculate_consumer_score

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScoreResult:
    ticker: str
    industry: str
    total_score: float = 0
    max_score: float = 0
    details: List[Dict[str, Any]] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    debug_logs: List[str] = field(default_factory=list)

    def log(self, message: str):
        """添加调试日志"""
        self.debug_logs.append(f"[{self.ticker}] {message}")
        logger.debug(f"{self.ticker}: {message}")


class ScoringSystem:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.ticker = data.get('ticker', '')

    def _prepare_data(self) -> Dict[str, Any]:
        """
        将原始数据整理为统一的格式供各个 scorer 使用。

        保持原始结构 (ratios/income_statement/balance_sheet/cash_flow)，
        让各个 scorer 的 get_value 函数能够正确提取数据。

        每个数据项优先使用 TTM 值，其次是 Current，最后是年度数据。
        """
        result = {'ticker': self.ticker}

        # 定义数据源 sections
        sections = ['ratios', 'income_statement', 'balance_sheet', 'cash_flow', 'extra']

        for section in sections:
            source = self.data.get(section, {})
            if not source:
                continue

            result[section] = {}
            for key, value in source.items():
                if isinstance(value, dict):
                    # 优先级: TTM > Current > FY 2025 > Annual Report
                    if 'TTM' in value:
                        result[section][key] = value['TTM']
                    elif 'Current' in value:
                        result[section][key] = value['Current']
                    elif 'FY 2025' in value:
                        result[section][key] = value['FY 2025']
                    elif 'Annual Report 2025' in value:
                        result[section][key] = value['Annual Report 2025']
                else:
                    result[section][key] = value

        return result

    def score_banks(self) -> ScoreResult:
        """银行评分 - 调用 banks scorer"""
        prepared_data = self._prepare_data()
        score_data = calculate_banks_score(prepared_data)

        return self._convert_to_score_result(score_data, "Banks")

    def score_materials(self) -> ScoreResult:
        """矿企评分 - 调用 materials scorer"""
        prepared_data = self._prepare_data()
        score_data = calculate_materials_score(prepared_data)

        return self._convert_to_score_result(score_data, "Materials")

    def score_infrastructure(self) -> ScoreResult:
        """基建评分 - 调用 infrastructure scorer"""
        prepared_data = self._prepare_data()
        score_data = calculate_infrastructure_score(prepared_data)

        return self._convert_to_score_result(score_data, "Infrastructure")

    def score_consumer_staples(self) -> ScoreResult:
        """必需消费评分 - 调用 consumer scorer"""
        prepared_data = self._prepare_data()
        score_data = calculate_consumer_score(prepared_data)

        return self._convert_to_score_result(score_data, "Consumer Staples")

    def _convert_to_score_result(self, score_data: Dict[str, Any], industry: str) -> ScoreResult:
        """
        将 scorer 返回的数据转换为 ScoreResult 格式。
        """
        result = ScoreResult(
            ticker=score_data.get('ticker', self.ticker),
            industry=industry,
            total_score=score_data.get('total_score', 0),
            max_score=score_data.get('max_score', 10)
        )

        # 转换 metrics 为 details 列表
        metrics = score_data.get('metrics', {})
        for metric_name, metric_data in metrics.items():
            weight = metric_data.get('weight', 0)

            # 跳过权重为 0 的指标 (如 LVR 惩罚项)
            if weight == 0 and metric_name != 'LVR':
                continue

            detail = {
                'metric': metric_name,
                'value': self._format_value(metric_data.get('value')),
                'score': metric_data.get('score', 0),
                'max': 10,
                'benchmark': metric_data.get('benchmark', ''),
                'description': metric_data.get('description', ''),
            }

            # 添加单位 (如果有)
            if 'unit' in metric_data:
                detail['unit'] = metric_data['unit']

            result.details.append(detail)

            # 根据级别判断是否通过
            level = metric_data.get('level', '')
            if level in ('excellent', 'good') or (isinstance(metric_data.get('score', 0), (int, float)) and metric_data.get('score', 0) >= 7):
                result.passed_checks.append(metric_name)

        # 检查 LVR 惩罚
        if score_data.get('lvr_penalty', False):
            result.log("LVR > 75%, 总分折半")

        return result

    def _format_value(self, value: Any) -> str:
        """格式化值为字符串"""
        if value is None:
            return "N/A"
        if isinstance(value, (int, float)):
            return f"{value:.2f}"
        return str(value)

    def score(self, industry: str) -> ScoreResult:
        """根据行业类型调用对应的评分函数"""
        industry = industry.lower()

        if 'bank' in industry or '金融' in industry:
            result = self.score_banks()
        elif 'material' in industry or 'mining' in industry or '矿' in industry:
            result = self.score_materials()
        elif 'infrastructure' in industry or 'infra' in industry or 'utilities' in industry or '基建' in industry or '公用' in industry:
            result = self.score_infrastructure()
        elif 'consumer' in industry or 'staples' in industry or '消费' in industry:
            result = self.score_consumer_staples()
        elif 'health' in industry or '医' in industry or 'pharma' in industry:
            raise ValueError("Healthcare 行业暂未实现，请使用 banks/materials/infrastructure/consumer")
        elif 'tele' in industry or '通信' in industry:
            raise ValueError("Telecom 行业暂未实现，请使用 banks/materials/infrastructure/consumer")
        else:
            raise ValueError(f"未知行业: {industry}")

        logging.info(f"Completed industry-specific scoring for {self.ticker} in {industry}")
        return result


def score_to_dict(result: ScoreResult) -> Dict[str, Any]:
    """将 ScoreResult 转换为可序列化的字典，供 API / CLI 输出"""
    percentage = (result.total_score / result.max_score * 100) if result.max_score > 0 else 0
    return {
        'ticker': result.ticker,
        'industry': result.industry,
        'score': {
            'total': round(result.total_score, 1),
            'max': result.max_score,
            'percentage': round(percentage, 1),
        },
        'details': result.details,
        'passed_checks': result.passed_checks,
        'failed_checks': result.failed_checks,
    }


def generate_comparison_data(results: List[ScoreResult]) -> List[Dict[str, Any]]:
    """生成多股票对比的结构化数据（供前端渲染）"""
    return [score_to_dict(r) for r in results]


def main():
    parser = argparse.ArgumentParser(description='ASX股票12刀打分系统')
    parser.add_argument('data_file', help='财务数据JSON文件')
    parser.add_argument('industry', help='行业类型: banks/materials/infrastructure/consumer')
    parser.add_argument('-o', '--output', help='输出JSON结果文件')

    args = parser.parse_args()

    with open(args.data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    scorer = ScoringSystem(data)
    result = scorer.score(args.industry)

    output = json.dumps(score_to_dict(result), indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        logger.info(f"结果已保存: {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
