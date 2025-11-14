pipeline {
    agent any

    environment {
        SONARQUBE_ENV = 'sonarqube'
        PROJECT_KEY = 'python-app'
        IMAGE_NAME = 'ghcr.io/argadepp/fastapi-csv-app'
    }

    parameters {
        booleanParam(
            name: 'DEPLOY_ENABLED',
            defaultValue: false,
            description: 'Enable deployment?'
        )
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'master', url: 'https://github.com/argadepp/assignment-finjo.git'
            }
        }

        // stage('SonarQube Analysis') {
        //     steps {
        //         withSonarQubeEnv("${SONARQUBE_ENV}") {
        //             sh '''
        //             export PATH="$PATH:/opt/sonar-scanner/bin"
        //             sonar-scanner \
        //               -Dsonar.projectKey=${PROJECT_KEY} \
        //               -Dsonar.sources=. \
        //               -Dsonar.host.url=$SONAR_HOST_URL \
        //               -Dsonar.login=$SONAR_AUTH_TOKEN
        //             '''
        //         }
        //     }
        // }

        // stage('Quality Gate') {
        //     steps {
        //         timeout(time: 10, unit: 'MINUTES') {
        //             waitForQualityGate abortPipeline: true
        //         }
        //     }
        // }

        stage('Build Docker Image') {
            steps {
                sh '''
                echo "Building Docker image..."
                docker build -t ${IMAGE_NAME}:latest .
                docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Push to GHCR') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'GHCR_CREDENTIALS',
                                                  usernameVariable: 'GH_USER',
                                                  passwordVariable: 'GH_TOKEN')]) {

                    sh '''
                    echo "Logging into GHCR..."
                    echo $GH_TOKEN | docker login ghcr.io -u $GH_USER --password-stdin
                    
                    echo "Pushing image to GHCR..."
                    docker push ${IMAGE_NAME}:latest
                    docker push ${IMAGE_NAME}:${BUILD_NUMBER}
                    '''
                }
            }
        }

        stage('Remove Local Docker Images') {
            steps {
                sh '''
                echo "Cleaning local Docker images..."
                docker rmi ${IMAGE_NAME}:latest || true
                docker rmi ${IMAGE_NAME}:${BUILD_NUMBER} || true
                '''
            }
        }

        stage('Generate Manifest') {
            steps {
                sh '''
                echo "Generating Kubernetes manifest file..."
                mkdir -p k8s

                cat > k8s/deployment.yaml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: fastapi-container
        image: ${IMAGE_NAME}:${BUILD_NUMBER}
        ports:
        - containerPort: 8000
EOF
                '''
            }
        }

        stage('Deploy (optional)') {
            when {
                expression { return params.DEPLOY_ENABLED == true }
            }
            steps {
                sh '''
                echo "Deploying application..."
                kubectl apply -f k8s/deployment.yaml
                '''
            }
        }

        stage('Cleanup') {
            steps {
                echo 'Cleaning workspace...'
                sh '''
                docker system prune -af || true
                '''
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
