pipeline {
  agent any

  environment {
    DEST = 'D:/MyFiles/Projects/Deployment'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        script {
          echo "Branch: ${env.BRANCH_NAME}"
          echo "Workspace: ${env.WORKSPACE}"
        }
      }
    }

    stage('Clean Workspace') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              echo "Cleaning workspace..."
              rm -rf artifacts data notebooks
              rm -f .gitignore create_project_dir.py README.md
              echo "---- After cleanup ----"
              ls -la
            '''
          } else {
            bat '''
              echo Cleaning workspace...
              rmdir /S /Q artifacts 2>nul
              rmdir /S /Q data 2>nul
              rmdir /S /Q notebooks 2>nul
              del /Q .gitignore 2>nul
              del /Q create_project_dir.py 2>nul
              del /Q README.md 2>nul
              echo ---- After cleanup ----
              dir
            '''
          }
        }
      }
    }

    stage('Build and Copy') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              echo "Cleaning destination and copying files..."

              DEST_PATH="/opt/deployment"   # <-- adjust to your Linux path
              echo "Destination: $DEST_PATH"

              # wipe destination before copying
              rm -rf "$DEST_PATH"
              mkdir -p "$DEST_PATH"

              # copy workspace content
              rsync -av --exclude='.git' --exclude='.venv' --exclude='dist' \
                    --exclude='Jenkinsfile' ./ "$DEST_PATH"/

              echo "Build complete."
            '''
          } else {
            bat bat """
              echo Cleaning destination and copying files...

              if exist "D:/MyFiles/Projects/Deployment" rmdir /S /Q "D:/MyFiles/Projects/Deployment"
              mkdir "D:/MyFiles/Projects/Deployment"

              robocopy "%WORKSPACE%" "D:/MyFiles/Projects/Deployment" *.* /S /E /COPY:DAT /R:2 /W:2 /NFL /NDL /NP /XO ^
                /XD ".git" ".venv" "dist" ^
                /XF "Jenkinsfile"

              set RC=%ERRORLEVEL%
              if %RC% GEQ 8 (
                echo Robocopy failed with code %RC%
                exit /b %RC%
              ) else (
                echo Robocopy success (code %RC%).
                exit /b 0
              )
            """
          }
        }
      }
    }
  }

  post {
    always {
      echo "Build finished: ${currentBuild.currentResult}"
    }
  }
}
