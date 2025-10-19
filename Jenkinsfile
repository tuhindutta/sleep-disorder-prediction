pipeline {
  agent any

  environment {
    VENV_DIR = '.venv'
    ARTIFACT_DIR = 'dist'
    PYPI = 'http://127.0.0.1:8081/'
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
        script {
          echo "Checked out branch: ${env.BRANCH_NAME}"
          echo "Workspace path: ${env.WORKSPACE}"
        }
      }
    }

    stage('Clean') {
        steps {
            script {
                bat '''
                    cd "%WORKSPACE%"
                    rmdir /S /Q artifacts
                    rmdir /S /Q data
                    rmdir /S /Q notebooks
                    del /Q .gitignore
                    del /Q create_project_dir.py
                    del /Q Jenkinsfile
                    echo ---- Contents ----
                    dir
                    '''
                }
            }
        }

    stage('Build') {
        steps {
            script {
                bat '''
                    echo Building....
                    set "FolderPath=D:/MyFiles/Projects/Deployment"
                    
                    if not exist "%FolderPath%" (
                        mkdir "%FolderPath%"
                        echo Folder "%folderPath%" created.
                    ) else (
                        del /f /s /q "%FolderPath%/*"
                        echo Folder contents cleared.
                    )
                    echo Creating virtual environment...
                    python -m venv %VENV_DIR%
                    call %VENV_DIR%\\Scripts\\activate
                    python -m pip install --upgrade pip
                    python -m pip install --upgrade build wheel setuptools
                    echo Building wheel...
                    python -m build
                    call deactivate
                    echo Build complete
                    '''
                }
            }
        }

    stage('Publish to Nexus') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'nexus-cred',
          usernameVariable: 'TWINE_USERNAME',
          passwordVariable: 'TWINE_PASSWORD'
        )]) {
          bat """
            echo Publicshing to Nexus....
            call %VENV%\\Scripts\\activate
            python -m pip install --upgrade twine
            python -m twine upload --%PYPI% %NEXUS_REPO_URL% %ARTIFACT_DIR%\\*
            call deactivate
            echo Published in Nexus.
          """
        }
      }
    }

    stage('Archive artifacts') {
      steps {
        script {
          archiveArtifacts artifacts: "${ARTIFACT_DIR}/*", fingerprint: true, onlyIfSuccessful: true
        }
      }
    }

  }
}
