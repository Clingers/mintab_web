"""
单元测试 for plot_utils.py。
测试所有画图函数返回有效的 base64 编码 PNG 图片。
"""

import pytest
import base64
import io
import sys
import os
from typing import Dict, Any

# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from plot_utils import (
    setup_chinese_font,
    plot_scatter,
    plot_histogram,
    plot_boxplot,
    plot_heatmap,
)
import pandas as pd
import numpy as np


# Fixtures
@pytest.fixture
def sample_df():
    """创建一个样本 DataFrame 用于测试画图"""
    np.random.seed(42)  # 固定随机种子，测试可重复
    return pd.DataFrame({
        'x': np.random.randn(100),
        'y': np.random.randn(100),
        'value': np.random.uniform(0, 100, 100),
        'category': ['A'] * 50 + ['B'] * 50,
        'score': np.random.randint(1, 10, 100),
    })


@pytest.fixture
def numeric_series():
    """数值型 Series"""
    return pd.Series([1, 2, 3, 4, 5], name='test')


@pytest.fixture
def numeric_df():
    """包含多个数值列的 DataFrame"""
    return pd.DataFrame({
        'col1': [1, 2, 3, 4, 5],
        'col2': [5, 4, 3, 2, 1],
        'col3': [2, 3, 2, 3, 2],
    })


# ========== setup_chinese_font 测试 ==========

class TestSetupChineseFont:
    """测试 setup_chinese_font 函数"""
    
    def test_runs_without_error(self):
        """函数应该正常执行，不抛出异常"""
        setup_chinese_font()  # 如果抛出异常，测试会失败
        assert True
    
    def test_matplotlib_font_set(self):
        """应该设置 matplotlib 的字体参数"""
        setup_chinese_font()
        import matplotlib.pyplot as plt
        # 检查字体参数是否被设置
        assert 'font.sans-serif' in plt.rcParams
        assert plt.rcParams['axes.unicode_minus'] is False


# ========== 辅助函数测试 ==========

class TestHelperFunctions:
    """测试内部辅助函数（通过公共接口间接测试）"""
    
    def test_figure_to_base64_returns_string(self, numeric_series):
        """_figure_to_base64 应返回字符串（通过画图函数间接测试）"""
        # 我们无法直接导入 _figure_to_base64，但可以通过公开函数测试
        b64 = plot_histogram(numeric_series)
        assert isinstance(b64, str)


# ========== plot_scatter 测试 ==========

class TestPlotScatter:
    """测试 plot_scatter 函数"""
    
    def test_returns_base64_string(self, sample_df):
        """应返回 base64 字符串"""
        b64 = plot_scatter(sample_df, 'x', 'y')
        assert isinstance(b64, str)
        assert len(b64) > 0
    
    def test_valid_base64(self, sample_df):
        """返回的字符串应是有效的 base64"""
        b64 = plot_scatter(sample_df, 'x', 'y')
        # 尝试解码
        try:
            decoded = base64.b64decode(b64)
            assert isinstance(decoded, bytes)
        except Exception as e:
            pytest.fail(f"Invalid base64 string: {e}")
    
    def test_decodes_to_png(self, sample_df):
        """解码后应是有效的 PNG 图片"""
        b64 = plot_scatter(sample_df, 'x', 'y')
        decoded = base64.b64decode(b64)
        # PNG 文件头：\x89PNG\r\n\x1a\n
        assert decoded.startswith(b'\x89PNG\r\n\x1a\n'), "Not a valid PNG file"
    
    def test_with_title(self, sample_df):
        """提供标题参数应正常工作"""
        b64 = plot_scatter(sample_df, 'x', 'y', title='测试散点图')
        assert isinstance(b64, str)
        assert len(b64) > 0
    
    def test_missing_column_raises(self, sample_df):
        """列不存在时应抛出 ValueError"""
        with pytest.raises(ValueError, match="not found in DataFrame"):
            plot_scatter(sample_df, 'nonexistent', 'y')
    
    def test_no_valid_data_raises(self):
        """无有效数据时应抛出 ValueError"""
        df = pd.DataFrame({'x': [None, None], 'y': [1, 2]})
        with pytest.raises(ValueError, match="No valid data"):
            plot_scatter(df, 'x', 'y')


# ========== plot_histogram 测试 ==========

class TestPlotHistogram:
    """测试 plot_histogram 函数"""
    
    def test_returns_base64_string(self, numeric_series):
        """应返回 base64 字符串"""
        b64 = plot_histogram(numeric_series)
        assert isinstance(b64, str)
        assert len(b64) > 0
    
    def test_valid_base64(self, numeric_series):
        """应是有效的 base64"""
        b64 = plot_histogram(numeric_series)
        try:
            decoded = base64.b64decode(b64)
            assert isinstance(decoded, bytes)
        except Exception as e:
            pytest.fail(f"Invalid base64: {e}")
    
    def test_decodes_to_png(self, numeric_series):
        """解码后应是 PNG"""
        b64 = plot_histogram(numeric_series)
        decoded = base64.b64decode(b64)
        assert decoded.startswith(b'\x89PNG\r\n\x1a\n')
    
    def test_with_custom_bins(self, numeric_series):
        """自定义箱数应正常工作"""
        b64 = plot_histogram(numeric_series, bins=10)
        assert isinstance(b64, str)
    
    def test_with_title(self, numeric_series):
        """提供标题应正常工作"""
        b64 = plot_histogram(numeric_series, title='测试直方图')
        assert isinstance(b64, str)
    
    def test_no_valid_data_raises(self):
        """无有效数据时应抛出 ValueError"""
        series = pd.Series([None, None, None], name='test')
        with pytest.raises(ValueError, match="No valid numeric data"):
            plot_histogram(series)


# ========== plot_boxplot 测试 ==========

class TestPlotBoxplot:
    """测试 plot_boxplot 函数"""
    
    def test_returns_base64_string(self, sample_df):
        """应返回 base64 字符串"""
        b64 = plot_boxplot(sample_df)
        assert isinstance(b64, str)
        assert len(b64) > 0
    
    def test_valid_base64(self, sample_df):
        """应是有效的 base64"""
        b64 = plot_boxplot(sample_df)
        try:
            decoded = base64.b64decode(b64)
            assert isinstance(decoded, bytes)
        except Exception as e:
            pytest.fail(f"Invalid base64: {e}")
    
    def test_decodes_to_png(self, sample_df):
        """解码后应是 PNG"""
        b64 = plot_boxplot(sample_df)
        decoded = base64.b64decode(b64)
        assert decoded.startswith(b'\x89PNG\r\n\x1a\n')
    
    def test_with_column_list(self, sample_df):
        """指定列列表应正常工作"""
        b64 = plot_boxplot(sample_df, columns=['x', 'y', 'value'])
        assert isinstance(b64, str)
    
    def test_with_title(self, sample_df):
        """提供标题应正常工作"""
        b64 = plot_boxplot(sample_df, title='测试箱式图')
        assert isinstance(b64, str)
    
    def test_no_numeric_columns_raises(self):
        """无数值列时应抛出 ValueError"""
        df = pd.DataFrame({'cat': ['a', 'b', 'c']})
        with pytest.raises(ValueError, match="No numeric columns"):
            plot_boxplot(df)
    
    def test_invalid_column_raises(self, sample_df):
        """指定不存在的列时应抛出 ValueError"""
        with pytest.raises(ValueError, match="None of the specified columns"):
            plot_boxplot(sample_df, columns=['nonexistent'])


# ========== plot_heatmap 测试 ==========

class TestPlotHeatmap:
    """测试 plot_heatmap 函数"""
    
    def test_returns_base64_string(self, numeric_df):
        """应返回 base64 字符串"""
        b64 = plot_heatmap(numeric_df)
        assert isinstance(b64, str)
        assert len(b64) > 0
    
    def test_valid_base64(self, numeric_df):
        """应是有效的 base64"""
        b64 = plot_heatmap(numeric_df)
        try:
            decoded = base64.b64decode(b64)
            assert isinstance(decoded, bytes)
        except Exception as e:
            pytest.fail(f"Invalid base64: {e}")
    
    def test_decodes_to_png(self, numeric_df):
        """解码后应是 PNG"""
        b64 = plot_heatmap(numeric_df)
        decoded = base64.b64decode(b64)
        assert decoded.startswith(b'\x89PNG\r\n\x1a\n')
    
    def test_with_title(self, numeric_df):
        """提供标题应正常工作"""
        b64 = plot_heatmap(numeric_df, title='测试热力图')
        assert isinstance(b64, str)
    
    def test_different_methods(self, numeric_df):
        """不同相关系数方法应正常工作"""
        for method in ['pearson', 'kendall', 'spearman']:
            b64 = plot_heatmap(numeric_df, method=method)
            assert isinstance(b64, str)
    
    def test_insufficient_numeric_columns_raises(self):
        """数值列不足 2 个时应抛出 ValueError"""
        df = pd.DataFrame({'only_one': [1, 2, 3]})
        with pytest.raises(ValueError, match="Need at least 2 numeric columns"):
            plot_heatmap(df)


# ========== 集成测试 ==========

class TestIntegration:
    """集成测试：验证所有函数可以协同工作"""
    
    def test_all_plot_functions_with_sample_data(self, sample_df):
        """所有画图函数应能处理同一样本数据"""
        results = {}
        
        # 散点图
        results['scatter'] = plot_scatter(sample_df, 'x', 'y')
        # 直方图
        results['histogram'] = plot_histogram(sample_df['value'])
        # 箱式图
        results['boxplot'] = plot_boxplot(sample_df)
        # 热力图
        numeric_df = sample_df.select_dtypes(include=['float64', 'int64'])
        results['heatmap'] = plot_heatmap(numeric_df)
        
        # 验证所有结果都是有效的 base64 PNG
        for plot_type, b64 in results.items():
            decoded = base64.b64decode(b64)
            assert decoded.startswith(b'\x89PNG\r\n\x1a\n'), f"{plot_type} did not produce valid PNG"
    
    def test_base64_strings_are_different(self, sample_df):
        """不同图表应产生不同的 base64 字符串"""
        b64_scatter = plot_scatter(sample_df, 'x', 'y')
        b64_hist = plot_histogram(sample_df['x'])
        
        assert b64_scatter != b64_hist, "Different plots should produce different base64 strings"
