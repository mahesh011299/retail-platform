pipeline {
    agent any

    parameters {
        choice(name: 'DEPLOYMENT_ACTION', choices: ['DEPLOY', 'ROLLBACK'], description: 'Deployment Action')
        choice(name: 'ENVIRONMENT', choices: ['UAT', 'PRODUCTION'], description: 'Target Environment')
        string(name: 'VERSION', defaultValue: '4.2.2', description: 'Version Tag')
        choice(name: 'CONFIRM_PROD', choices: ['NO', 'YES'], description: 'Confirm Production')
    }

    environment {
        APP_NAME = "retail-app"
        CANDIDATE_NAME = "retail-app-candidate"
        NETWORK = "retail-network"
        PORT = "8081"
        PREV_IMAGE = "retail-app:4.2.1"
    }

    stages {
        stage('Validate Production') {
            steps {
                script {
                    if (params.ENVIRONMENT == 'PRODUCTION' && params.CONFIRM_PROD != 'YES') {
                        error("PRODUCTION deployment rejected: CONFIRM_PROD must be 'YES'.")
                    }
                }
            }
        }

        stage('Validate Git Tag') {
            steps {
                bat """
                    git fetch --tags
                    git rev-parse refs/tags/v${params.VERSION}
                """
            }
        }

        stage('Docker Build') {
            steps {
                bat "docker build -t ${APP_NAME}:${params.VERSION} ."
            }
        }

        stage('Deploy & Automated Rollback') {
            steps {
                script {
                    try {
                        echo "Starting candidate container..."
                        bat "docker rm -f ${CANDIDATE_NAME} 2>NUL || exit /b 0"

                        // Simulate failure when version is 4.2.2
                        def simHealth = (params.VERSION == '4.2.2') ? 'unhealthy' : 'healthy'

                        bat """
                            docker run -d --name ${CANDIDATE_NAME} ^
                                --network ${NETWORK} ^
                                -p 8085:8081 ^
                                -e APP_VERSION=${params.VERSION} ^
                                -e ENVIRONMENT=${params.ENVIRONMENT} ^
                                -e PAYMENT_STATUS=fixed ^
                                -e HEALTH_STATUS=${simHealth} ^
                                ${APP_NAME}:${params.VERSION}
                        """

                        echo "Checking candidate health on port 8085..."
                        sleep time: 10, unit: 'SECONDS'
                        bat "curl --fail http://localhost:8085/health"

                        echo "Candidate passed! Promoting to active production container..."
                        bat "docker rm -f ${CANDIDATE_NAME}"
                        bat "docker rm -f ${APP_NAME} 2>NUL || exit /b 0"
                        bat """
                            docker run -d --name ${APP_NAME} ^
                                --network ${NETWORK} ^
                                -p ${PORT}:8081 ^
                                -e APP_VERSION=${params.VERSION} ^
                                -e ENVIRONMENT=${params.ENVIRONMENT} ^
                                -e PAYMENT_STATUS=fixed ^
                                -e HEALTH_STATUS=${simHealth} ^
                                ${APP_NAME}:${params.VERSION}
                        """
                    } catch (Exception e) {
                        echo "======================================================="
                        echo "HEALTH CHECK FAILED FOR ${params.VERSION}! INITIATING ROLLBACK."
                        echo "Restoring previous production image: ${env.PREV_IMAGE}"
                        echo "======================================================="

                        // Clean up failed candidate container
                        bat "docker rm -f ${CANDIDATE_NAME} 2>NUL || exit /b 0"

                        // Restore previous working production container
                        bat "docker rm -f ${APP_NAME} 2>NUL || exit /b 0"
                        bat """
                            docker run -d --name ${APP_NAME} ^
                                --network ${NETWORK} ^
                                -p ${PORT}:8081 ^
                                ${env.PREV_IMAGE}
                        """

                        sleep time: 8, unit: 'SECONDS'
                        bat "curl --fail http://localhost:${PORT}/health"
                        echo "Rollback successfully restored ${env.PREV_IMAGE} on port ${PORT}."

                        currentBuild.result = 'FAILURE'
                        error("Deployment failed; automatic rollback was executed successfully.")
                    }
                }
            }
        }
    }
}