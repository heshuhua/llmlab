import git
import os

try:
    # 指定 Git 仓库路径
    repo_path = "/Users/heshuhua/lab/ailab/llmlab"
    repo = git.Repo(repo_path)

    # 获取当前分支
    current_branch = repo.active_branch
    print(f"当前分支: {current_branch.name}")

    # 获取最新 commit ID (HEAD)
    head_commit = repo.head.commit
    print(f"最新 Commit ID: {head_commit.hexsha}") # Commit ID (SHA-1 hash)
    print(f"Commit Message: {head_commit.message.strip()}")
    print(f"Author: {head_commit.author.name} <{head_commit.author.email}>")
    print(f"Commit Date: {head_commit.authored_datetime}")

    # 获取所有分支
    print("\n所有分支:")
    for branch in repo.branches:
        print(f"- {branch.name}")

except git.InvalidGitRepositoryError:
    print(f"'{repo_path}' 不是一个有效的 Git 仓库。")
except Exception as e:
    print(f"发生错误: {e}")