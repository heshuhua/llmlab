import git
import os

try:
    # 指定 Git 仓库路径
    repo_path = "/Users/heshuhua/lab/ailab/llmlab"
    repo = git.Repo(repo_path)
    