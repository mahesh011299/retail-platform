pipeline {

    agent any

    parameters {

        choice(
            name: 'DEPLOYMENT_ACTION',
            choices: ['DEPLOY', 'ROLLBACK'],
            description: 'Select deployment action'
        )

        choice(
            name: 'ENVIRONMENT',
            choices: ['UAT', 'PRODUCTION'],
            description: 'Select deployment environment'
        )

        string(
            name: 'VERSION',
            defaultValue: '4.2.1',
            description: 'Application version'
        )

        choice(
            name: 'CONFIRM_PROD',
            choices: ['NO', 'YES'],
            description: 'Required for production deployment'
        )
    }

    stages {

        stage('Display Parameters') {

            steps {

                echo "================================="
                echo "DEPLOYMENT ACTION = ${params.DEPLOYMENT_ACTION}"
                echo "ENVIRONMENT       = ${params.ENVIRONMENT}"
                echo "VERSION           = ${params.VERSION}"
                echo "CONFIRM PROD      = ${params.CONFIRM_PROD}"
                echo "================================="
            }
        }

        stage('Validate Production') {

            steps {

                script {

                    if (
                        params.ENVIRONMENT == 'PRODUCTION' &&
                        params.CONFIRM_PROD != 'YES'
                    ) {

                        error(
                            "Production deployment requires CONFIRM_PROD=YES"
                        )
                    }
                }
            }
        }

        stage('Checkout') {

            steps {

                checkout scm

                bat '''
                    git rev-parse HEAD
                '''
            }
        }

        stage('Validate Git Tag') {

            steps {

                bat '''
                    git fetch --tags
                    git rev-parse v%VERSION%
                '''
            }
        }

        stage('Docker Build') {

            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    docker build -t retail-app:%VERSION% .
                '''
            }
        }

        stage('Docker Images') {

            steps {

                bat '''
                    docker images retail-app
                '''
            }
        }

        stage('Deploy') {

            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    docker rm -f retail-app 2>NUL || exit /b 0

                    docker run -d ^
                      --name retail-app ^
                      --network retail-network ^
                      -p 8081:8081 ^
                      -e APP_VERSION=%VERSION% ^
                      -e ENVIRONMENT=%ENVIRONMENT% ^
                      -e PAYMENT_STATUS=fixed ^
                      -e HEALTH_STATUS=healthy ^
                      retail-app:%VERSION%
                '''
            }
        }

        stage('Health Check') {

            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    timeout /t 10 /nobreak

                    curl --fail http://localhost:8081/health
                '''
            }
        }

        stage('Deployment Verification') {

            steps {

                bat '''
                    docker ps
                    docker inspect retail-app
                '''
            }
        }
    }

    post {

        success {

            echo "================================="
            echo "DEPLOYMENT SUCCESSFUL"
            echo "VERSION = ${params.VERSION}"
            echo "================================="
        }

        failure {

            echo "================================="
            echo "DEPLOYMENT FAILED"
            echo "================================="
        }
    }
}