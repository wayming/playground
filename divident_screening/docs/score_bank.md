🏦 银行基本面打分系统 (量化公式版)
1. NIM (净息差) - 赚钱能力

    白话意义： 银行的“进销差价”，越高说明吃利差的能力越强。

    计算公式： = Net Interest Income / (Gross Loans + Total Investments + Cash & Equivalents)

    判定逻辑：

        10分：>= 2.1%

        7分：1.8% - 2.1%

        4分：1.6% - 1.8%

        0分：< 1.6% (淘汰)
            
2. CET1 Ratio (一级资本) - 防御能力

    白话意义： 压箱底的保命钱，应对金融危机的底气。

    计算公式： = Common Equity Tier 1 Capital / Risk Weighted Assets

    判定逻辑：

        10分：>= 6.5% (或官方 CET1 >= 12.5%)

        7分：5.5% - 6.5% (或官方 11% - 12.5%)

        0分：< 5.0% (或官方 < 10.5%) (违规风险)
             
3. Cost-to-Income (成本收入比) - 效率

    白话意义： 赚100块钱要花多少水电费和人工。越低说明越精简高效。

    计算公式： = Total Non-Interest Expense / Revenues Before Loan Losses

    判定逻辑：

        10分：< 43%

        7分：43% - 47%

        4分：48% - 52%

        0分：> 55% (臃肿)

4. ROE (净资产收益率) - 回报

    白话意义： 股东投入1块钱，一年能收回多少钱。

    计算公式： = Net Income to Common / Total Common Equity

    判定逻辑：

        10分：>= 14%

        7分：11% - 13.9%

        4分：8% - 10.9%

        0分：< 7% (效率极低)

5. Credit Risk (坏账风险) - 资产质量

    白话意义： 每借出去100块钱，有多少是预计收不回来的。

    计算公式： = Provision for Loan Losses / Gross Loans

    判定逻辑：

        10分：< 0.10%

        7分：0.11% - 0.20%

        4分：0.21% - 0.40%

        0分：> 0.50% (雷区)

6. Payout Ratio (分红率) - 诚意

    白话意义： 赚到的钱里有多少是真金白银发给股东的。

    计算公式： = (Dividend Per Share * Basic Shares Outstanding) / Net Income to Common

    判定逻辑：

        10分：70% - 75% (黄金平衡点)

        7分：76% - 85% (慷慨)

        4分：50% - 69% (保留增长)

        0分：> 95% (不可持续)

7 辅助维度：LVR (贷款价值比) - 资产底牌

    白话意义： 房子值 100 万，银行借出去多少？如果只借了 50 万（LVR 50%），哪怕澳洲房价跌 30%，银行的本金依然稳如泰山。这是退休股的“终极防弹衣”。

    计算公式： = Group Average LVR

    判定逻辑 (LVR_Score)：

        10分： < 50% (极度安全，CBA 典型水平)

        7分： 50% - 60% (标准稳健)

        4分： 60% - 70% (风险敞口增大)

        0分： > 75% (高杠杆，房价下跌时有系统性风险)

📊 综合权重计算 (Total Score)

    Score = (NIM_Score * 0.2) + (CET1_Score * 0.2) + (CIR_Score * 0.15) + (ROE_Score * 0.15) + (Credit_Score * 0.2) + (Payout_Score * 0.1)

    Score = IF(LVR > 75%, Score * 0.5, Score)