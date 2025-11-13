pipeline {
    agent any

    environment {
        SONARQUBE_ENV = 'sonarqube' // Name from Jenkins config
        PROJECT_KEY = 'python-app'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'master', url: 'https://github.com/argadepp/assignment-finjo.git'
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    sh '''
                    sonar-scanner \
                      -Dsonar.projectKey=${PROJECT_KEY} \
                      -Dsonar.sources=. \
                      -Dsonar.host.url=$SONAR_HOST_URL \
                      -Dsonar.login=$SONAR_AUTH_TOKEN
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Deploy (optional)') {
            when {
                expression { return params.DEPLOY_ENABLED == true }
            }
            steps {
                sh 'echo "Deploying application..."'
            }
        }

        stage('Cleanup') {
            steps {
                echo 'Cleaning up workspace and virtual environment...'
                sh '''
                deactivate || true
                rm -rf venv
                docker system prune -af || true
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed. Workspace cleanup...'
            cleanWs()
        }
    }
}
