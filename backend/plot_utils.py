"""
画图工具函数 - 每个函数返回 base64 编码的 PNG 图片字符串。
支持散点图、直方图、箱式图、热力图。
"""

import base64
import io
from typing import Dict, Any, Optional, List
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，适合服务器环境
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def setup_chinese_font() -> None:
    """
    配置 matplotlib 支持中文显示。
    
    尝试查找系统中文字体（如 SimHei, WenQuanYi Zen Hei 等）。
    如果找不到，则使用 matplotlib 自带的 DejaVu Sans 并显示警告。
    设置 seaborn 的字体为相同字体以保持一致性。
    """
    import matplotlib.font_manager as fm
    
    # 常见中文字体列表，按优先级排序
    chinese_fonts = [
        'SimHei',           # 黑体
        'WenQuanYi Zen Hei', # 文泉驿正黑
        'Noto Sans CJK SC',  # Google Noto 简体中文
        'Droid Sans Fallback',
        'sans-serif',
    ]
    
    # 获取系统可用字体
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    selected_font = None
    for font_name in chinese_fonts:
        if font_name in available_fonts:
            selected_font = font_name
            break
    
    if selected_font:
        plt.rcParams['font.sans-serif'] = [selected_font]
    else:
        # 没有找到中文字体，使用默认配置，但会显示警告
        import warnings
        warnings.warn(
            "No Chinese font found in system. Chinese characters may not display correctly."
            "Consider installing 'fonts-noto-cjk' or 'fonts-wqy-zenhei'."
        )
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    
    # 解决负号显示问题
    plt.rcParams['axes.unicode_minus'] = False
    
    # 设置 seaborn 使用相同的字体配置
    sns.set(font=plt.rcParams['font.sans-serif'][0])


def _figure_to_base64(fig) -> str:
    """
    将 matplotlib 图像对象转换为 base64 编码的 PNG 字符串。
    
    Args:
        fig: matplotlib 图像对象
        
    Returns:
        base64 编码的字符串（不含 data:image/png;base64, 前缀）
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_bytes = buf.getvalue()
    buf.close()
    return base64.b64encode(img_bytes).decode('utf-8')


def plot_scatter(df: pd.DataFrame, x_col: str, y_col: str, 
                title: Optional[str] = None) -> str:
    """
    生成散点图。
    
    Args:
        df: 包含数据的 DataFrame
        x_col: X 轴列名
        y_col: Y 轴列名
        title: 图表标题（可选）
        
    Returns:
        base64 编码的 PNG 图片字符串
        
    Raises:
        ValueError: 如果列不存在或不是数值型
    """
    if x_col not in df.columns or y_col not in df.columns:
        raise ValueError(f"Columns '{x_col}' or '{y_col}' not found in DataFrame")
    
    # 只选择数值数据，忽略 NaN
    plot_df = df[[x_col, y_col]].dropna()
    
    if len(plot_df) == 0:
        raise ValueError(f"No valid data for scatter plot with columns '{x_col}' and '{y_col}'")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(plot_df[x_col], plot_df[y_col], alpha=0.7)
    
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(title or f'Scatter Plot: {x_col} vs {y_col}')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    result = _figure_to_base64(fig)
    plt.close(fig)
    return result


def plot_histogram(series: pd.Series, bins: int = 30, 
                  title: Optional[str] = None) -> str:
    """
    生成直方图。
    
    Args:
        series: 要绘制的数据序列
        bins: 直方图的箱数（默认 30）
        title: 图表标题（可选）
        
    Returns:
        base64 编码的 PNG 图片字符串
        
    Raises:
        ValueError: 如果没有有效数据
    """
    # 转换为数值，忽略无法转换的值
    numeric_series = pd.to_numeric(series, errors='coerce')
    clean_series = numeric_series.dropna()
    
    if len(clean_series) == 0:
        raise ValueError(f"No valid numeric data in column '{series.name}'")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(clean_series, bins=bins, edgecolor='black', alpha=0.7)
    
    ax.set_xlabel(series.name or 'Value')
    ax.set_ylabel('Frequency')
    ax.set_title(title or f'Histogram: {series.name or "Data"}')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    result = _figure_to_base64(fig)
    plt.close(fig)
    return result


def plot_boxplot(df: pd.DataFrame, columns: Optional[List[str]] = None, 
                title: Optional[str] = None) -> str:
    """
    生成箱式图（盒须图）。
    
    Args:
        df: 包含数据的 DataFrame
        columns: 要绘制的列名列表（默认所有数值列）
        title: 图表标题（可选）
        
    Returns:
        base64 编码的 PNG 图片字符串
        
    Raises:
        ValueError: 如果没有数值列或数据不足
    """
    # 选择数值列
    if columns is None:
        columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    
    if not columns:
        raise ValueError("No numeric columns found for boxplot")
    
    # 只选择存在的列
    valid_columns = [col for col in columns if col in df.columns]
    if not valid_columns:
        raise ValueError(f"None of the specified columns {columns} found in DataFrame")
    
    # 移除 NaN 并选择数据
    plot_df = df[valid_columns].dropna()
    
    if len(plot_df) == 0:
        raise ValueError("No valid data for boxplot")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_df.boxplot(ax=ax)
    
    ax.set_title(title or 'Box Plot')
    ax.set_ylabel('Value')
    ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    result = _figure_to_base64(fig)
    plt.close(fig)
    return result


def plot_heatmap(df: pd.DataFrame, method: str = 'pearson', 
                 title: Optional[str] = None) -> str:
    """
    生成相关性热力图。
    
    Args:
        df: 包含数据的 DataFrame
        method: 相关系数类型（'pearson', 'kendall', 'spearman'）
        title: 图表标题（可选）
        
    Returns:
        base64 编码的 PNG 图片字符串
        
    Raises:
        ValueError: 如果数值列不足 2 个
    """
    # 只选择数值列
    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    
    if len(numeric_cols) < 2:
        raise ValueError("Need at least 2 numeric columns for heatmap")
    
    # 计算相关性矩阵
    corr_df = df[numeric_cols].corr(method=method)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_df, annot=True, cmap='coolwarm', center=0, 
                square=True, ax=ax)
    
    ax.set_title(title or f'Correlation Heatmap ({method})')
    
    plt.tight_layout()
    result = _figure_to_base64(fig)
    plt.close(fig)
    return result
