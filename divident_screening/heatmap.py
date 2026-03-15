import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. 准备数据 - 建议先用英文 Key 避免乱码
data = {
    'PE_Ratio': [25, 60, 15, 45, 30],
    'ROE%': [22, 18, 5, 30, 12],
    'Rev_Growth%': [15, 45, -5, 80, 10],
    'Net_Margin%': [20, 12, 2, 25, 8],
    'Div_Yield%': [1.5, 0, 4.0, 0, 2.5],
    'Cash_Flow': [80, 40, 20, 95, 50]
}
stocks = ['Stock_A', 'Stock_B', 'Stock_C', 'Stock_D', 'Stock_E']
df = pd.DataFrame(data, index=stocks)

# 2. 数据标准化
df_norm = (df - df.min()) / (df.max() - df.min())

# 3. 绘图设置
plt.figure(figsize=(10, 6))

# 使用 RdYlGn 颜色条，数值标注保留 1 位小数
sns.heatmap(df_norm, annot=df, fmt=".1f", cmap="RdYlGn", cbar=True)

plt.title("Stock Metrics Comparison Heatmap")

# 重要：不要用 plt.show()，改为保存图片
plt.savefig('stock_heatmap.png', dpi=300, bbox_inches='tight')
print("Graph: /workspace/stock_heatmap.png")