# 数据分析助手 (AI-Powered)

![数据分析助手](https://img.freepik.com/free-vector/data-inform-illustration-concept_114360-864.jpg)

## 项目简介

数据分析助手是一个基于Streamlit和大型语言模型的交互式数据分析工具，它能够帮助用户快速分析CSV或Excel数据文件，生成可视化图表，并提供详细的分析报告。无需编写代码，只需通过自然语言对话即可完成复杂的数据分析任务。

## 主要功能

- **数据上传与预览**：支持CSV和Excel文件上传，自动预览数据内容
- **自然语言交互**：通过聊天界面用自然语言提问，AI自动生成分析代码
- **代码生成与执行**：自动生成Python分析代码并执行，展示分析结果
- **数据可视化**：生成交互式图表，直观展示数据分析结果
- **多模型支持**：支持多种AI大模型，包括DeepSeek、Claude、Qwen和Gemini等
- **API密钥管理**：用户可以设置自己的API密钥，保障数据安全

## 技术栈

- **前端框架**：Streamlit
- **数据处理**：Pandas
- **可视化**：Plotly
- **AI模型**：通过aider库集成多种大型语言模型

## 安装与使用

### 环境要求

- Python 3.12+
- 相关Python包（见requirements.txt）

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/aiderDA.git
cd aiderDA