from app.repositories.projects import ProjectRepository


class ProjectService:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repo = project_repository
