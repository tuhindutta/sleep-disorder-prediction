pipeline {
  agent any
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
                if (isUnix()) {
                    sh '''
                    cd "${WORKSPACE}"
                    rm -rf artifacts data notebooks .gitignore create_project_dir.py Jenkinsfile README.md
                    echo "---- Contents ----"
                    ls -la
                    '''
                } else {
                    bat '''
                    cd "%WORKSPACE%"
                    rmdir /S /Q artifacts
                    rmdir /S /Q data
                    rmdir /S /Q notebooks
                    del /Q .gitignore
                    del /Q create_project_dir.py
                    del /Q Jenkinsfile
                    del /Q README.md
                    echo ---- Contents ----
                    dir
                    '''
                }
            }
        }
    }
    stage('Build') {
        steps {
            script {
                if (isUnix()) {
                    sh '''
                    echo "Building...."
                    '''
                } else {
                    bat '''
                    echo Building....
                    '''
                }
            }
        }
    }
  }
}
