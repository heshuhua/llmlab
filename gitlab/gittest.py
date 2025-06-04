import git
import sys
import os

def compare_branch_with_tag(repo_path, branch_name, tag_name):
    """
    比较指定分支的 HEAD 提交与指定标签所指向的提交。

    Args:
        repo_path (str): Git 仓库的路径。
        branch_name (str): 要比较的分支的名称。
        tag_name (str): 用于比较的标签的名称。

    Returns:
        str: 描述比较结果的字符串，如果出错则返回错误信息。
    """
    try:
        repo = git.Repo(repo_path)

        # 1. 获取分支对应的提交对象
        try:
            branch_commit = repo.commit(branch_name)
            print(f"分支 '{branch_name}' 指向的提交: {branch_commit.hexsha[:7]}")
        except git.BadObject:
            return f"错误: 找不到分支 '{branch_name}' 或它没有提交历史。"
        except Exception as e:
            return f"获取分支 '{branch_name}' 提交时出错: {e}"

        # 2. 获取标签对应的提交对象
        try:
            # repo.tags 是一个字典，可以通过标签名直接访问
            tag_ref = repo.tags[tag_name]
            tag_commit = tag_ref.commit
            print(f"标签 '{tag_name}' 指向的提交: {tag_commit.hexsha[:7]}")
        except KeyError:
            return f"错误: 找不到标签 '{tag_name}'。"
        except Exception as e:
            return f"获取标签 '{tag_name}' 提交时出错: {e}"

        # 3. 比较祖先关系
        # is_ancestor(ancestor, descendant) 检查 ancestor 是否是 descendant 的祖先
        is_branch_ancestor_of_tag = repo.is_ancestor(branch_commit, tag_commit)
        is_tag_ancestor_of_branch = repo.is_ancestor(tag_commit, branch_commit)

        if branch_commit == tag_commit:
            return f"分支 '{branch_name}' 和标签 '{tag_name}' 指向同一个提交。"
        elif is_branch_ancestor_of_tag:
            return f"分支 '{branch_name}' 在标签 '{tag_name}' **之前** (是其祖先)。"
        elif is_tag_ancestor_of_branch:
            return f"分支 '{branch_name}' 在标签 '{tag_name}' **之后** (标签是其祖先)。"
        else:
            return f"分支 '{branch_name}' 和标签 '{tag_name}' 没有直接的祖先/后代关系（可能在不同的历史线上或已分叉）。"

    except git.InvalidGitRepositoryError:
        return f"错误: '{repo_path}' 不是一个有效的 Git 仓库。"
    except Exception as e:
        return f"发生未知错误: {e}"

if __name__ == "__main__":
    # 检查命令行参数数量
    if len(sys.argv) < 3:
        print("用法: python your_script_name.py <分支名称> <标签名称> [仓库路径]")
        print("例如: python compare_git_history.py main v1.0")
        print("或者: python compare_git_history.py develop release-2023 /path/to/my/repo")
        sys.exit(1)

    branch_to_compare = sys.argv[1]
    tag_to_compare = sys.argv[2]
    # 尝试获取可选的仓库路径，如果未提供则默认为当前目录
    repo_path = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()

    print(f"正在比较分支 '{branch_to_compare}' 和标签 '{tag_to_compare}'...")
    print(f"仓库路径: {repo_path}")

    result = compare_branch_with_tag(repo_path, branch_to_compare, tag_to_compare)
    print("\n--- 比较结果 ---")
    print(result)