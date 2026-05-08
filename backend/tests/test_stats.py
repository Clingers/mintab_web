"""
单元测试 for stats_utils.py。
测试所有函数的正常情况、边界情况和错误处理。
"""

import pytest
import pandas as pd
import sys
import os

# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stats_utils import detect_column_types, calculate_basic_stats, calculate_correlation


# Fixtures
@pytest.fixture
def sample_df():
    """创建一个样本 DataFrame 用于测试"""
    return pd.DataFrame({
        'age': [25, 30, 35, 40, 45],
        'salary': [50000, 60000, 70000, 80000, 90000],
        'department': ['HR', 'IT', 'IT', 'HR', 'IT'],
        'score': [85.5, 90.0, 78.5, 92.0, 88.5],
    })


@pytest.fixture
def numeric_series():
    """数值型 Series"""
    return pd.Series([1, 2, 3, 4, 5], name='test')


@pytest.fixture
def series_with_none():
    """包含 None/NaN 的 Series"""
    return pd.Series([1, None, 3, None, 5], name='test')


# ========== detect_column_types 测试 ==========

class TestDetectColumnTypes:
    """测试 detect_column_types 函数"""
    
    def test_detects_numeric_columns(self, sample_df):
        """应该正确识别数值列"""
        types = detect_column_types(sample_df)
        assert types['age'] == 'numeric'
        assert types['salary'] == 'numeric'
        assert types['score'] == 'numeric'
    
    def test_detects_categorical_columns(self, sample_df):
        """应该正确识别分类型列"""
        types = detect_column_types(sample_df)
        assert types['department'] == 'categorical'
    
    def test_all_columns_present(self, sample_df):
        """返回的字典应包含 DataFrame 的所有列"""
        types = detect_column_types(sample_df)
        assert set(types.keys()) == set(sample_df.columns)
    
    def test_empty_dataframe(self):
        """空 DataFrame 应返回空字典"""
        df = pd.DataFrame()
        types = detect_column_types(df)
        assert types == {}
    
    def test_mixed_types(self):
        """混合类型的 DataFrame"""
        df = pd.DataFrame({
            'int_col': [1, 2, 3],
            'float_col': [1.1, 2.2, 3.3],
            'str_col': ['a', 'b', 'c'],
            'bool_col': [True, False, True],
        })
        types = detect_column_types(df)
        assert types['int_col'] == 'numeric'
        assert types['float_col'] == 'numeric'
        assert types['str_col'] == 'categorical'
        assert types['bool_col'] == 'categorical'  # boolean 被视为分类


# ========== calculate_basic_stats 测试 ==========

class TestCalculateBasicStats:
    """测试 calculate_basic_stats 函数"""
    
    def test_returns_all_required_keys(self, numeric_series):
        """返回的字典应包含所需的统计键"""
        stats = calculate_basic_stats(numeric_series)
        required_keys = ['mean', 'median', 'std', 'min', 'max', 'count', 'missing', 'q1', 'q3']
        for key in required_keys:
            assert key in stats, f"Missing key: {key}"
    
    def test_correct_mean(self, numeric_series):
        """均值计算正确"""
        stats = calculate_basic_stats(numeric_series)
        assert stats['mean'] == 3.0  # (1+2+3+4+5)/5 = 3
    
    def test_correct_median(self, numeric_series):
        """中位数计算正确"""
        stats = calculate_basic_stats(numeric_series)
        assert stats['median'] == 3.0
    
    def test_correct_std(self, numeric_series):
        """标准差计算正确（样本标准差）"""
        stats = calculate_basic_stats(numeric_series)
        # 样本标准差：sqrt(((1-3)^2 + (2-3)^2 + (3-3)^2 + (4-3)^2 + (5-3)^2)/4) = sqrt(10/4) = sqrt(2.5) ≈ 1.5811
        assert abs(stats['std'] - 1.5811388300841898) < 0.0001
    
    def test_correct_min_max(self, numeric_series):
        """最小值和最大值正确"""
        stats = calculate_basic_stats(numeric_series)
        assert stats['min'] == 1
        assert stats['max'] == 5
    
    def test_count_excludes_missing(self, series_with_none):
        """count 应排除缺失值"""
        stats = calculate_basic_stats(series_with_none)
        assert stats['count'] == 3  # 只有 3 个非 None 值
        assert stats['missing'] == 2  # 2 个 None
    
    def test_with_all_none(self):
        """全 None 的序列应抛出 ValueError"""
        series = pd.Series([None, None, None], name='test')
        with pytest.raises(ValueError, match="no valid numeric data"):
            calculate_basic_stats(series)
    
    def test_with_empty_series(self):
        """空序列应抛出 ValueError"""
        series = pd.Series([], dtype='float64', name='test')
        with pytest.raises(ValueError):
            calculate_basic_stats(series)
    
    def test_quartiles(self, numeric_series):
        """四分位数计算正确"""
        stats = calculate_basic_stats(numeric_series)
        # 对于 [1,2,3,4,5]，Q1=2, Q3=4
        assert stats['q1'] == 2.0
        assert stats['q3'] == 4.0
    
    def test_quartiles_small_sample(self):
        """样本量小时（<4）用 min/max 代替"""
        series = pd.Series([10, 20], name='test')
        stats = calculate_basic_stats(series)
        assert stats['q1'] == 10  # min
        assert stats['q3'] == 20  # max
    
    def test_accepts_pandas_series(self):
        """接受 pandas Series 作为输入"""
        series = pd.Series([100, 200, 300], name='values')
        stats = calculate_basic_stats(series)
        assert stats['count'] == 3
        assert stats['mean'] == 200.0


# ========== calculate_correlation 测试 ==========

class TestCalculateCorrelation:
    """测试 calculate_correlation 函数"""
    
    def test_returns_correlation_matrix(self, sample_df):
        """返回相关性矩阵 DataFrame"""
        numeric_df = sample_df[['age', 'salary', 'score']]
        corr = calculate_correlation(numeric_df)
        assert isinstance(corr, pd.DataFrame)
        assert set(corr.columns) == {'age', 'salary', 'score'}
        assert set(corr.index) == {'age', 'salary', 'score'}
    
    def test_perfect_positive_correlation(self):
        """完全正相关的两个数列"""
        df = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 6, 8, 10],  # y = 2x
        })
        corr = calculate_correlation(df)
        assert abs(corr.loc['x', 'y'] - 1.0) < 0.0001
        assert abs(corr.loc['y', 'x'] - 1.0) < 0.0001
    
    def test_perfect_negative_correlation(self):
        """完全负相关的两个数列"""
        df = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [10, 8, 6, 4, 2],  # y = -2x + 12
        })
        corr = calculate_correlation(df)
        assert abs(corr.loc['x', 'y'] - (-1.0)) < 0.0001
    
    def test_no_correlation(self):
        """无相关的两个数列"""
        df = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [5, 1, 4, 2, 3],  # 随机排列
        })
        corr = calculate_correlation(df)
        # 相关性应接近 0
        assert abs(corr.loc['x', 'y']) < 0.5
    
    def test_insufficient_numeric_columns(self):
        """数值列不足 2 个时返回空 DataFrame"""
        df = pd.DataFrame({
            'only_one': [1, 2, 3],
            'category': ['a', 'b', 'c'],
        })
        corr = calculate_correlation(df)
        assert corr.empty
    
    def test_method_parameter(self, sample_df):
        """测试 method 参数"""
        numeric_df = sample_df[['age', 'salary']]
        # Pearson 相关系数
        corr_pearson = calculate_correlation(numeric_df, method='pearson')
        # Kendall 或 Spearman 也可以测试，但需要确保数据适合
        assert not corr_pearson.empty
    
    def test_ignores_non_numeric(self):
        """忽略非数值列"""
        df = pd.DataFrame({
            'num1': [1, 2, 3],
            'num2': [4, 5, 6],
            'text': ['a', 'b', 'c'],
        })
        corr = calculate_correlation(df)
        # 只应包含数值列
        assert set(corr.columns) == {'num1', 'num2'}
