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
    stae('Build') {
        steps {
            script {
                if (isUnix()) {
                    sh '''
                    cd "${WORKSPACE}"
                    echo "---- Contents ----"
                    ls -la
                    '''
                } else {
                    bat '''
                    cd "%WORKSPACE%"
                    echo ---- Contents ----
                    dir
                    '''
                }
            }
        }
    }
  }
}
