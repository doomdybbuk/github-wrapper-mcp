from github import Github

class GitHubClient:
    def __init__(self, token: str):
        self.gh = Github(token)
        self.user = self.gh.get_user()

    def create_repo(self, name: str, private: bool = True, description: str = ""):
        return self.user.create_repo(name=name, private=private, description=description)

    def get_clone_url(self, repo_name: str):
        repo = self.user.get_repo(repo_name)
        return repo.clone_url

    def add_collaborator(self, repo_name: str, collaborator: str, permission: str = "push"):
        repo = self.user.get_repo(repo_name)
        return repo.add_to_collaborators(collaborator, permission)

    def add_workflow_file(self, repo_name: str, path: str, content: str, message: str = "Add workflow"):
        repo = self.user.get_repo(repo_name)
        try:
            file = repo.get_contents(path)
            repo.update_file(path, message, content, file.sha)
        except Exception:
            repo.create_file(path, message, content)