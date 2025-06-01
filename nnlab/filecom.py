from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import difflib
import os

class FileComparator:
    def __init__(self, model_name="codellama:latest", base_url="http://localhost:11434"):
        """初始化文件对比器"""
        self.llm = Ollama(
            model=model_name,
            base_url=base_url,
            temperature=0.1  # 降低随机性，获得更一致的分析
        )
        
        # 定义分析提示模板
        self.analysis_template = PromptTemplate(
            input_variables=["file1_name", "file2_name", "file1_content", "file2_content", "diff_content"],
            template="""
作为一个代码分析专家，请详细分析以下两个Python文件的差异：

文件1: {file1_name}
```python
{file1_content}
```

文件2: {file2_name}
```python
{file2_content}
```

差异信息：
```
{diff_content}
```

请从以下角度进行分析：

1. **主要变更内容**：列出具体的代码变更
2. **变更原因分析**：推测为什么要做这些改动
3. **功能影响评估**：这些变更对程序功能的影响
4. **代码质量改进**：在代码结构、性能、可维护性方面的改进
5. **潜在风险提醒**：可能需要注意的问题或风险点
6. **建议和最佳实践**：基于变更内容的改进建议

请用中文详细回答，使用markdown格式美化输出。
"""
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.analysis_template)
    
    def read_file(self, file_path):
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"文件未找到: {file_path}")
        except Exception as e:
            raise Exception(f"读取文件时出错: {e}")
    
    def generate_diff(self, content1, content2, file1_name, file2_name):
        """生成文件差异"""
        lines1 = content1.splitlines(keepends=True)
        lines2 = content2.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(
            lines1, lines2,
            fromfile=file1_name,
            tofile=file2_name,
            lineterm=''
        ))
        
        return ''.join(diff)
    
    def compare_files(self, file1_path, file2_path):
        """对比两个文件并生成分析报告"""
        print(f"正在读取文件: {file1_path} 和 {file2_path}")
        
        # 读取文件内容
        content1 = self.read_file(file1_path)
        content2 = self.read_file(file2_path)
        
        # 生成差异
        print("正在生成差异信息...")
        diff_content = self.generate_diff(content1, content2, file1_path, file2_path)
        
        if not diff_content.strip():
            return "两个文件内容完全相同，没有差异。"
        
        # 使用 LLM 分析
        print("正在调用 Ollama 进行分析...")
        try:
            analysis = self.chain.run(
                file1_name=file1_path,
                file2_name=file2_path,
                file1_content=content1,
                file2_content=content2,
                diff_content=diff_content
            )
            return analysis
        except Exception as e:
            return f"调用 Ollama 时出错: {e}"
    
    def batch_compare(self, file_pairs):
        """批量对比多对文件"""
        results = {}
        for file1, file2 in file_pairs:
            print(f"\n{'='*50}")
            print(f"对比 {file1} vs {file2}")
            print('='*50)
            results[f"{file1}_vs_{file2}"] = self.compare_files(file1, file2)
        return results

# 使用示例
def main():
    # 初始化对比器
    comparator = FileComparator(model_name="codellama:latest")
    
    # 单文件对比
    try:
        result = comparator.compare_files("/Users/heshuhua/lab/ailab/llmlab/nnlab/maindlg-01.py", "/Users/heshuhua/lab/ailab/llmlab/nnlab/maindlg.py")
        print("\n" + "="*60)
        print("文件对比分析结果")
        print("="*60)
        print(result)
        
        # 可选：保存结果到文件
        with open("file_comparison_report_codellama.md", "w", encoding="utf-8") as f:
            f.write(f"# 文件对比分析报告\n\n")
            f.write(f"对比文件: maindlg-01.py vs maindlg.py\n\n")
            f.write(result)
        print("\n分析报告已保存到 file_comparison_report.md")
        
    except Exception as e:
        print(f"分析过程中出错: {e}")

if __name__ == "__main__":
    main()