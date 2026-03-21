*银行基本面六维度量化模型
1. NIM (净息差) - 衡量定价权

    计算公式：
    NIM=Net Interest Income / (Gross Loans + Total Investments + Cash & Equivalents)

    数据取值 (FY 2025)： 24,023/(1,015,883+258,997+54,381)=1.81%

    量化标准： 1.8%−2.1% 为优。CBA 刚好踩在优良线的底端，说明其贷款定价与资金成本控制极其平衡。

2. CET1 Ratio (一级资本充足率) - 危机抵御力

    计算公式：
    CET1 Ratio=Total Common Equity / Total Assets

    数据说明： JSON 中没有 RWA，但你有 Equity (78,776)。澳洲银行监管极其严格，CBA 官方 CET1 通常维持在 12% 以上。

    量化标准： >11.5% 为安全。若数据源无此项，可观察 Total Common Equity / Total Assets 是否 >5% 作为最底层的财务杠杆安全垫。

3. Cost-to-Income Ratio (成本收入比) - 运营效率

    计算公式：
    Cost-to-Income=Total Non-Interest Expense / Revenues Before Loan Losses

    数据取值 (FY 2025)： 12,996/28,290=45.94%

    量化标准： <45%。CBA 目前略高于 45%，但在全球大型银行中仍处于领先地位。

4. ROE (净资产收益率) - 综合盈利能力

    计算公式：
    ROE=Net Income to Common / Total Common Equity

    数据取值 (FY 2025)： 10,116/78,776=12.84%

    量化标准： 11%−13% 为目标区间。CBA 的表现非常精准地落在了你的目标范围内，体现了极其稳定的盈利输出。

5. Bad Debt / Gross Loans (不良贷款率) - 资产质量

    计算公式：
    由于数据中没有直接的“Non-performing Loans (NPL)”，我们使用当年拨备占比作为代理指标：
    Credit Risk Metric=Provision for Loan Losses / Gross Loans

    数据取值 (FY 2025)： 726/1,015,883=0.071%

    量化标准： <0.15%。计算结果为 0.07%，远低于 0.15% 的预警线，说明 CBA 的风控极佳，资产质量几乎没有死穴。

6. Payout Ratio (股息支付率) - 股东回报与安全

    计算公式：
    Payout Ratio=(Dividend Per Share × Basic Shares Outstanding) / Net Income to Common

    数据取值 (FY 2025)： (4.85×1,672)/10,116=80.16%

    量化标准： 70%−80%。CBA 维持在 80% 的上限，说明其非常慷慨地回馈股东，同时保留了 20% 的利润用于内生性增长或应对监管。

7. LVR - 贷款价值比
    数据取值 (FY 2025)： search by DeepSeek API
    

**图示：
1. 逻辑映射表（可视化设计的核心）

在绘图前，我们需要根据你提供的量化标准定义颜色：
指标	绿色 (优)	黄色 (一般)	红色 (预警)	极性 (Polarity)
NIM	> 1.95%	1.8% - 1.95%	< 1.8%	越高越好
CET1	> 12.5%	11.5% - 12.5%	< 11.5%	越高越好
Cost-to-Income	< 43%	43% - 46%	> 46%	越低越好
ROE	> 12%	11% - 12%	< 11%	越高越好
Bad Debt	< 0.1%	0.1% - 0.15%	> 0.15%	越低越好
Payout Ratio	70% - 80%	60% - 70%	> 85% 或 < 50%

2. 叠合雷达图 (Overlaid Radar Chart)

如果你只想对比 2-3 只 最核心的股票（比如 CBA vs NAB），雷达图能展示出“基因差异”。例如，CBA 的图形可能在 ROE 和 Bad Debt 方向非常饱满，而另一家可能在 NIM 方向更突出。


*矿企更看重成本控制（AISC）和现金流强度（FCF Yield）。
力拓 (RIO.AX) 矿业六维度量化分析
1. AISC (全维持成本) - 成本曲线控制

    计算公式： 由于财报 JSON 通常不直接给出 AISC（需结合具体产量），我们使用运营成本率作为替代量化参数：
    Operating Cost Ratio = (Cost of Revenue + Sustaining Capex) / Revenue

    量化参数： 根据数据，RIO 的 Cost of Revenue 为 41,428M，Revenue 为 57,638M。虽然总成本率在上升，但 RIO 皮尔巴拉铁矿石的现金成本长期处于 $20/吨 以下，稳居全球行业前 15%。

    结论： 通过。即便矿价下跌 50%，RIO 依然有极厚利润空间。

3. Production Guidance (产量指引) - 营收护城河

    计算公式：

        Construction Growth (在建工程增速) = (Current CIP - Prior CIP) / Prior CIP

        CAPEX Intensity (资本支出强度) = CIP / Total PPE
        (注：CIP 代表在建工程。该比例越高，说明公司未来“翻新”和“扩产”的动力越强)

    量化方式： 通过 CIP 的异常增长 预判未来 Revenue（营收） 的放量。矿企的营收护城河不在于当下的卖货量，而在于是否有足够的新矿山在建，以对冲老矿山的品位衰减。

    数据取值 (FY 2025)：

        营收增速：Revenue Growth (YoY) 为 7.42%，显示目前经营稳健。

        在建储备：CIP 从 10,925M 激增至 16,764M，增速高达 53.4%。

        资产占比：CIP 占 PPE（房产厂房设备）的比重从 15.9% 提升至 19.9%。

    结论： 通过。力拓正处于资本开支的“超级周期”。53% 的在建工程增速远超营收增速，这意味着公司不是在吃老本，而是在大规模布局新产能（如西芒杜铁矿、库鲁里钾肥等）。这确保了公司在未来 3-5 年即使面临矿价波动，也能通过“增量”来保住营收总规模，护城河具备极强的扩张潜力。

4. Underlying NPAT (核心净利润) - 剔除减值后的真相

    计算公式：
    Underlying NPAT = Net Income - Asset Writedown - Other Unusual Items
    
    数据取值 (FY 2025)： * Reported Net Income: 9,966M

        Asset Writedown: -341M (需加回)

    计算： 9,966+341=10,307M

    结论： RIO 的减值逐年收窄（2023 年曾高达 1,167M），说明资产组合清理已接近尾声，103 亿左右的利润是坚实的。

6. FCF Yield (自由现金流收益率) - 牛市含金量

    计算公式：
    FCF Yield = (Free Cash Flow / Market Capitalization) * 100%

    数据取值 (FY 2025)： 4,497/206,124=2.18%

    量化标准： 你的标准是 > 8%。

    结论： 未通过 (目前仅 2.18%)。注意，RIO 2025 年的资本开支（Capex）高达 12,335M（同比大增 28%），说明公司正处于资本投入期而非成熟收割期。这对分红会有短期压力。

7. Net Debt / EBITDA (净杠杆率) - 周期御寒力

    计算公式：
    Net Debt / EBITDA = (Total Debt - Cash & Equivalents) / EBITDA

    数据取值 (FY 2025)：

        Net Debt: 14,328M

        EBITDA: 20,285M

    计算结果： 0.71x

    量化标准： < 1.0x

    结论： 通过。即便在激进扩张期，杠杆率仍远低于 1.0x，极其安全。

10. Dividend Policy (分红政策) - 利润分配逻辑

    计算公式：
    Payout Ratio = (Common Dividends Paid / Net Income to Common) * 100%

    数据取值 (FY 2025)： 61.66%

    量化标准： 固定 NPAT 比例（通常 50%+）。

    结论： 通过。RIO 维持了约 60% 的派息率，非常符合矿业巨头“现金奶牛”的本色。

**图示
叠合雷达图 (Overlaid Radar Chart)

如果你对比的股票在 3 只以内，叠合雷达图能展示出各家公司的“基因差异”。

    视觉效果：RIO 是橙色区域，BHP 是蓝色区域。

    洞察点：如果 RIO 的面积在“杠杆”方向比 BHP 大，说明 RIO 更安全；如果在“FCF Yield”方向缩进去，说明 RIO 正在大量砸钱搞建设。


* 针对基建与公用事业行业的“收租”逻辑，核心在于评估其垄断溢价能力、债务偿还安全性以及资产变现效率。

以下是基于您提供的 APA 原始数据，为您整理的 6 大指标完整量化计算公式及 APA (TTM) 实际测算过程：
## 基建行业 6 刀考察：量化计算指南
### 第 4 刀：EBITDA Margin (运营利润率)

核心逻辑： 衡量基础设施资产在剔除融资成本和非现金折旧后的原始盈利能力。

    计算公式：
    EBITDA Margin = (EBITDA / Revenue) * 100%
    
    APA (TTM) 测算：
    1,960/3,197=61.31%

        量化结论： 合格 (优)。符合基建股高毛利、固定运营成本低的特征。

### 第 6 刀：Cash Conversion (现金转化率)

核心逻辑： 考察 EBITDA 中有多少能真正转化为手里的现金流，排除会计账面水分。

    计算公式：
    CCash Conversion = (Operating Cash Flow / EBITDA) * 100%

    APA (TTM) 测算：
    1,196/1,960=61.02%

        量化结论： 不合格。基建优等生要求 OCF 紧贴 EBITDA。APA 此处差距过大，说明利息和税收的现金流出严重侵蚀了运营成果。

### 第 7 刀：Interest Cover Ratio (利息覆盖率)

核心逻辑： 核心“安全带”。衡量息税前利润对利息支出的覆盖倍数，反映抗加息风险能力。

    计算公式：
    Interest Cover = EBIT (Operating Income) / |Interest Expense|

    APA (TTM) 测算：
    982/682=1.44x

        量化结论： 极差。远低于 3x 的标准。说明在当前利率环境下，APA 赚的钱勉强只够付利息，安全垫极薄。

### 第 11 刀：EV / EBITDA (企业价值倍数)

核心逻辑： 基建股前期投入大、折旧高，PE 会失真。EV/EBITDA 考虑了债务，是更真实的估值。

    计算公式：
    EV / EBITDA = (Market Cap + Total Debt - Cash) / EBITDA

    APA (Current) 测算：
    (12,073+13,224−170)/1,960=12.82x

    (注：数据中 ratios 给出为 12.67x，微小差异源于现金抵扣项取值)

    量化结论： 合格。处于 12x - 15x 舒适区间，估值未过热。

### 第 12 刀：CPI Linkage (抗通胀能力)

核心逻辑： 基建是重资产行业，必须能把通胀成本转嫁给终端用户。

    量化方式：
    通常无法直接从财报数字计算，需查阅 "Notes to Financial Statements" 中的 "Revenue Contracts" 部分。

    APA 考察方式： 查看是否有 "Indexation clauses" 或 "CPI linked pricing"。

        APA 现状： 约 80%-90% 的天然气管道收入受 CPI 调节或受监管保护。

        量化标准： 越高越好，100% 为满分。

### 第 1 刀：Contract Length (平均特许经营权/合同期限)

核心逻辑： 决定了“收租”生意的稳定性，期限越长，DCF 模型下的终值越稳。

    量化方式：
    计算加权平均合同剩余期限 (WWACE - Weighted Average Contract Expiry)。

    测算依据：
    WACE=∑(单个合同剩余年限×总收入该合同贡献收入​)

    APA 现状： 核心资产期限一般在 10-15 年左右。

    量化结论： 中等。未达到 20 年的“优等生”终极门槛，需关注合同续签风险。

** 图示
叠合雷达图 (Overlaid Radar Chart) —— 适合 2-3 只股深度对标

雷达图能完美展示基建股的“稳健程度”。一个完美的基建股雷达图应该是一个巨大的、均匀的六边形。

    指标处理：

        利息覆盖率 (Interest Cover)：标准是 3x，APA 只有 1.44x，这会在图上形成一个严重的内缩。

        现金转化率 (Cash Conversion)：反映盈利质量。

        WACE (合同期限)：反映护城河深度。



* 消费
## 必需消费行业 6 刀考察：WES 量化计算指南
### 第 1 刀：Market Share (市场占有率)

量化方式： 通常无法通过单一公司财报算出。需要对比全澳洲零售/超市行业总规模。

    计算方法： Market Share = WES Annual Revenue / Industry Total Revenue

    WES 现状： 在澳洲硬件零售（Bunnings）和折扣百货（Kmart）领域具有绝对垄断或领先地位。

    数据观察： WES TTM 营收为 46,422.0，FY2021-2025 营收持续增长，说明其在通胀环境下依然保持了极强的市场攫取能力。

### 第 4 刀：EBIT Margin (息税前利润率)

核心逻辑： 零售业是微利生意，主要看能否在扣除运营成本后锁住利润。

    计算公式：
    EBIT Margin = (Operating Income (EBIT) / Revenue) * 100%

    WES (TTM) 测算：
    4,073/46,422=8.77%

    量化结论： 优等生 (超标)。该指标远高于超市类 4.5% - 6% 的基准，说明 WES 旗下的 Bunnings 和 Kmart 拥有比普通超市更高的利润溢价和成本控制能力。

### 第 5 刀：ROE (净资产收益率)

核心逻辑： 衡量管理层利用股东出的钱赚取利润的效率。

    计算公式：
    ROE = (Net Income / Shareholders’ Equity) * 100%

    WES (TTM) 测算：
    3,062/7,856=38.98%

    (注：数据表中 ratios 给出为 36.39%，由于股权部分取值点不同有微差)

    量化结论： 优等生。远超 > 25% 的基准。这说明 WES 完美利用了高周转和适度杠杆来放大股东回报。

### 第 7 刀：Inventory Days (库存周转天数)

核心逻辑： 零售业的生死线。货在仓库里多待一天，钱就多亏一天。

    计算公式：
    Inventory Days = (Inventory / Cost of Revenue) * 365

    WES (TTM) 测算：
    (6,771/30,796)×365=80.26 天

    量化结论： 不合格 (需结合子行业)。超市基准是 25-30 天，但 WES 含有大量非食品（五金、家具、家电），此类商品自然周转较慢。若将其视为超市，则库存积压严重；若视为百货，则属正常范畴。

### 第 10 刀：Franking Credits (红利抵免)

核心逻辑： 澳洲投资者的底牌，100% Fully Franked 意味着公司在澳洲境内交足了税。

    量化方式： 查看派息公告中的 "Franked Amount"。

    WES 现状： 历史上 WES 几乎始终保持 100% Fully Franked。

    计算验证： 其 Effective Tax Rate（有效税率）TTM 为 27.8%，非常接近澳洲 30% 的企业所得税率，支持 100% 的抵免水平。

### 第 11 刀：Forward PE (远期市盈率)

核心逻辑： 估值锚点。防守型资产在不确定性时期往往更贵。

    计算公式：
    Forward PE = Current Market Price / Next Year’s Estimated EPS

    WES (Current) 测算：
    由数据直接读取：28.52x

    量化结论： 偏贵。基准为 20x - 24x，目前的 28.52x 说明市场已经给出了极高的“避风港溢价”。

**图示
叠合雷达图 (The Retail Fingerprint)

适合 2-3 只股的深度对标。

    指标分布：

        Market Share (市场地位)

        EBIT Margin (盈利能力)

        ROE (资本回报率)

        Inventory Days (取反处理)：为了让图表一致，天数越少（周转快），得分越高。

        Franking Credits (税务透明度/股东回报)

        Forward PE (取反处理)：PE 越低，得分越高（越便宜）。