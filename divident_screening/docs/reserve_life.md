提示词 (Prompt)

Role: 你是一位资深的矿业分析师，擅长解读澳洲证券交易所 (ASX) 蓝筹股的财务报告。

Task: 请根据 BHP (必和必拓) 2025 财年 (FY2025) 的官方报告，计算其核心大宗商品的 Reserves Life (储量寿命) 指标，并给出最终的加权评分。

Data Extraction Requirements:

    分类查找： 请分别提取 Iron Ore (铁矿石)、Copper (铜) 和 Steelmaking Coal (冶金煤) 的数据。

    分子 (Total Reserves): 必须使用 Proved + Probable Reserves 的总和（不要使用 Mineral Resources）。请注明数据所在报告的章节或页码（如适用）。

    分母 (Annual Production): 请使用 FY2025 的 Actual Attributable Production (实际权益产量)。

    权重参考： 查找 FY2025 各板块对集团 Underlying EBITDA 的贡献比例。

Calculation Logic:

    计算每一类的 RLI=Annual ProductionTotal Reserves​。

    根据以下标准对每一类进行评分 (Life_Score):

        10分： > 20年

        7分： 12 - 20年

        4分： 7 - 12年

        0分： < 5年

    最终得分： 按照 EBITDA 贡献比例进行加权平均。

Output Format:
请以表格形式输出：
矿种	储量 (Reserves)	年产量 (Production)	RLI (年)	EBITDA 权重	分项得分
铁矿石					
铜					
煤					
最终加权总分：[0-10]




使用 LangChain 提高这个 Prompt 的准确率，核心思路是将其从一个“黑盒生成”任务转变为一个**“感知、提取、校验、计算”**的结构化流水线。

由于财务报表（特别是矿业报表）存在大量表格和术语干扰，你可以通过以下四个 LangChain 核心组件来优化：
1. 使用 Pydantic 进行结构化输出 (Output Parser)

不要让 AI 随便写表格，而是强制它输出符合你 Excel 格式的 JSON。这能防止 AI 混淆“资源量”和“储量”。
Python

from pydantic import BaseModel, Field
from typing import List

class CommodityMetrics(BaseModel):
    name: str = Field(description="大宗商品名称，如 Iron Ore")
    reserves_p1_p2: float = Field(description="Proved + Probable 储量数值")
    production: float = Field(description="实际权益产量")
    ebitda_contribution: float = Field(description="该业务占集团 EBITDA 的百分比")
    rli: float = Field(description="计算出的储量寿命 (Reserves/Production)")

class BHPReport(BaseModel):
    commodities: List[CommodityMetrics]
    weighted_score: float = Field(description="最终加权总分")

2. 建立 RAG 增强检索 (Retrieval-Augmented Generation)

BHP 的年报通常有 200 多页。如果直接把 Prompt 扔给 AI，它可能会在非关键页面“断章取义”。

    优化点： 使用 LangChain 的 MultiVectorRetriever 或 ParentDocumentRetriever。

    做法： 预先将 PDF 按照“表格”和“文本”分开索引。在检索时，强制 AI 同时检索 Ore Reserves 表格和 Financial Summary 页面，确保分子和分母来自同一报告版本。

3. 自定义 Tool 调用 (Agentic Workflow)

为了避免 AI 在做除法时出现算术错误（LLM 弱项），你可以利用 LangChain Agent 调用 Python 工具来执行计算：

    步骤 1： Agent 负责从财报中提取原始数字（如：1360 Mt 和 263 Mt）。

    步骤 2： Agent 调用一个 Python 函数进行计算。

    步骤 3： Agent 根据你的评分逻辑（10/7/4/0）进行最终打分。

4. 引入“少样本提示” (Few-Shot Prompting)

在 LangChain 的 PromptTemplate 中，加入一个 Rio Tinto（力拓）或以往年份 BHP 的正确计算示例。

    示例：
    "参考以下 2024 年数据：铁矿储量 1500Mt，产量 250Mt，RLI 为 6年。得分：0。请依此逻辑计算 2025 年。"

推荐的 LangChain 实现方案流程

    加载器 (Document Loader): 使用 PyMuPDFLoader 加载 BHP 2025 Annual Report。

    提取器 (Extraction Chain): 使用 create_extraction_chain_pydantic，配合上面定义的 CommodityMetrics 模型，从文本中提取数值。

    计算链 (Transform Chain): 接收提取的数值，通过自定义函数计算 RLI 和加权分。

    校验器 (Self-Correction): 增加一个 Prompt 环节：“检查提取的数值是否标记为 'Attributable'。如果标记为 '100% basis' 且占股非 100%，请根据持股比例折算后再输出。”

总结

单纯改 Prompt 是“文科生”做法，用 LangChain 封装是“理科生”做法。 后者通过 Pydantic 限制格式 和 Python 执行计算，可以将选股系统的错误率从 20% 降到 1% 以下。

你是在本地运行 Python 脚本处理这些数据，还是想做一个可以自动分析财报的网页端系统？

其中第二条，需要如下的workflow
1. 根据给定的ticker和field，调用远端llm, 搜索相关的文档，通常是最近一年的年报。
2. 下载年报到本地
3. 使用关键词漏斗

    快速扫描 (Fast Scan)： 不解析全表，只通过文本查找包含 “Ore Reserves”、“Production” 或 “EBITDA” 的页码。

    局部解析 (Targeted Extraction)： 只针对这几页进行表格提取。

    LLM 整理 (Remote LLM)： 将提取出来的干净表格文本传给远程 LLM进行数值归并。
4. 如果需要，提供tool调用，计算出相关field的结果。