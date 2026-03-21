⛏️ 矿业基本面七维度量化模型 (逻辑公式版)
1. AISC (全维持成本分位) - 行业地位

    白话意义： 决定了你在成本曲线上的位置。矿价跌的时候，别人亏钱你赚钱。

    Excel 公式： (Cost of Revenue + Sustaining Capex) / Revenue

    判定逻辑 (AISC_Score)：

        10分： < 60% (全球成本最低的前 25%，如 RIO 铁矿)

        7分： 60% - 75% (行业平均水平)

        4分： 75% - 85% (高成本边际矿)

        0分： > 85% (极度危险，周期下行必死)


2. Reserves Life (储量寿命) - 资产成色 (新增)

    白话意义： 家里有矿不稀奇，稀奇的是能挖一辈子。这是矿企的“保质期”。

    Excel 公式： Total Proved Reserves / Annual Production Volume

    判定逻辑 (Life_Score)：

        10分： > 20年 (如 RIO 皮尔巴拉铁矿，几乎无穷无尽)

        7分： 12 - 20年 (稳健，有充足时间寻找新矿)

        4分： 7 - 12年 (中规中矩，必须加大勘探投入)

        0分： < 5年 (面临枯竭，资产减值风险极大)

3. Capex Intensity (资本支出强度) - 增长后劲

    白话意义： 钱是用来修补旧机器，还是用来盖新厂房？衡量扩张野心。

    Excel 公式： Construction In Progress / Property, Plant & Equipment

    判定逻辑 (Capex_Score)：

        10分： > 15% (扩张周期，RIO 19.9% 属于此类)

        7分： 8% - 15% (常规更新与温和扩张)

        4分： 3% - 8% (仅维持现状)

        0分： < 3% (吃老本，产能即将萎缩)

4. Underlying ROE (核心收益率) - 管理真相

    白话意义： 剔除资产减值后的真实赚钱效率，看管理层是不是在做无用功。

    Excel 公式： (Net Income + Asset Writedown) / Total Common Equity

    判定逻辑 (ROE_Score)：

        10分： > 25% (顶级矿商，资源与管理双优)

        7分： 15% - 25% (矿业优等生)

        4分： 8% - 15% (平庸)

        0分： < 5% (资本浪费)

5. FCF Yield (自由现金流收益率) - 含金量

    白话意义： 市值里有多少是每年能实打实流进兜里的钱。

    Excel 公式： Free Cash Flow / Market Capitalization

    判定逻辑 (FCF_Score)：

        10分： > 10% (疯狂印钞机)

        7分： 6% - 10% (成熟稳健，合理区间)

        4分： 2% - 5% (建设期/投入期，RIO 2.18% 处于此区间)

        0分： < 0 (烧钱模式)

6. Net Debt / EBITDA (净杠杆率) - 抗震指数

    白话意义： 哪怕矿价跌到泥土里，能不能扛过寒冬不破产。

    Excel 公式： (Total Debt - Cash & Equivalents) / EBITDA

    判定逻辑 (Leverage_Score)：

        10分： < 0.5x (财务极度自由)

        7分： 0.5x - 1.2x (安全，RIO 0.71x 属于此列)

        3分： 1.5x - 2.5x (杠杆偏高，注意周期拐点)

        0分： > 3.0x (危险边缘)

7. Payout Ratio (分红政策) - 回报诚意

    白话意义： 愿不愿意把利润分给股东，是否符合“分红股”定位。

    Excel 公式： Common Dividends Paid / Net Income to Common

    判定逻辑 (Payout_Score)：
要求结果中
        10分： 50% - 70% (健康的现金奶牛)

        7分： 40% - 50% (平衡增长与回报)

        4分： < 30% (铁公鸡)

        0分： > 100% (入不敷出，借钱分红，极度危险)

📊 最终权重分配 (矿业总分公式)

由于矿业是“老天爷赏饭吃”+“财务不出错”，权重分配如下：
Total Score = (AISC * 0.2) + (Life * 0.2) + (Capex * 0.15) + (ROE * 0.15) + (FCF * 0.1) + (Leverage * 0.1) + (Payout * 0.1)