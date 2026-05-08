"""
统计计算工具函数 - 每个函数都是纯函数，易于测试和复用。
提供列类型检测和基本统计量计算。
"""

from typing import Dict, Any, List
import pandas as pd
import statistics
from collections.abc import Sequence


def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    检测 DataFrame 每列的数据类型。
    
    根据 pandas 的 dtype 判断列是数值型还是分类型。
    数值型包括: int, float, complex 等数值类型。
    分类型包括: object, string, categorical, boolean 等非数值类型。
    注意: boolean 类型被视为分类型，因为不适合计算均值等统计量。
    
    Args:
        df: 输入的 pandas DataFrame
        
    Returns:
        字典，key 为列名，value 为 'numeric' 或 'categorical'
    """
    column_types = {}
    
    for col_name, dtype in df.dtypes.items():
        # 显式检查 boolean 类型，视为分类型
        if pd.api.types.is_bool_dtype(dtype):
            column_types[col_name] = 'categorical'
        elif pd.api.types.is_numeric_dtype(dtype):
            column_types[col_name] = 'numeric'
        else:
            column_types[col_name] = 'categorical'
    
    return column_types


def calculate_basic_stats(series: pd.Series) -> Dict[str, Any]:
    """
    计算单列数值型数据的基本统计量。
    
    如果序列包含非数值数据，会尝试转换为数值（类似 pd.to_numeric）。
    无法转换的值会被忽略（相当于删除）。
    
    Args:
        series: pandas Series，应为数值型数据
        
    Returns:
        包含以下键的字典:
        - mean: 均值
        - median: 中位数  
        - std: 标准差（样本标准差，ddof=1）
        - min: 最小值
        - max: 最大值
        - q1: 第一四分位数（25%分位数）
        - q3: 第三四分位数（75%分位数）
        - count: 有效数值个数
        - missing: 缺失值个数
        
    Raises:
        ValueError: 如果序列中没有有效数值数据
    """
    # 尝试转换为数值，无法转换的变为 NaN
    numeric_series = pd.to_numeric(series, errors='coerce')
    
    # 移除 NaN 值
    clean_series = numeric_series.dropna()
    
    if len(clean_series) == 0:
        raise ValueError(f"Column '{series.name}' has no valid numeric data")
    
    # 转换为 Python float 列表（便于使用 statistics 模块）
    data = clean_series.tolist()
    
    # 计算统计量
    stats = {
        'mean': statistics.mean(data),
        'median': statistics.median(data),
        'std': statistics.stdev(data) if len(data) > 1 else 0.0,
        'min': min(data),
        'max': max(data),
        'count': len(data),
        'missing': len(series) - len(data),
    }
    
    # 计算四分位数（使用 pandas quantile，更符合数据分析习惯）
    if len(data) >= 4:
        # 使用 pandas Series 的 quantile 方法，默认线性插值
        series_clean = pd.Series(data)
        stats['q1'] = float(series_clean.quantile(0.25))
        stats['q3'] = float(series_clean.quantile(0.75))
    else:
        # 数据太少，用 min 和 max 代替
        stats['q1'] = stats['min']
        stats['q3'] = stats['max']
    
    return stats


def calculate_correlation(df: pd.DataFrame, method: str = 'pearson') -> pd.DataFrame:
    """
    计算 DataFrame 中所有数值列之间的相关性矩阵。
    
    Args:
        df: pandas DataFrame
        method: 相关系数类型，'pearson'（默认）、'kendall' 或 'spearman'
        
    Returns:
        相关性矩阵 DataFrame，索引和列都是数值列名
    """
    # 只选择数值列
    numeric_cols = [col for col, dtype in df.dtypes.items() 
                   if pd.api.types.is_numeric_dtype(dtype)]
    
    if len(numeric_cols) < 2:
        # 数值列不足，返回空 DataFrame
        return pd.DataFrame()
    
    # 计算相关性矩阵
    corr_df = df[numeric_cols].corr(method=method)
    return corr_df
