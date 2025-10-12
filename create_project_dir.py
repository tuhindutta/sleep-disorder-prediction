import os


class ProjectDir:

    def __init__(self):
        self.required = {
            "dirs": ["./src", "./notebooks", "./models", "./config", "./tests",
                     "./data/raw", "./data/processed" , "./data/external"],

            "files": {
                ".gitignore": "" ,
                "Dockerfile": "",
                "README.md": "",
                "requirements.txt": ""
            }
        }

    def create_dirs(self, path:str):
        for directory in self.required.get('dirs'):
            path_to_create = os.path.join(path, directory)
            os.makedirs(path_to_create, exist_ok=True)

    def create_files(self, path:str):
        for file, content in self.required.get('files').items():
            path_to_create = os.path.join(path, file)
            with open(path_to_create, "w") as f:
                f.write(content)

    def create(self, path:str = './'):
        self.create_dirs(path)
        self.create_files(path)


if __name__ == "__main__":
    dir = ProjectDir()
    dir.create()

