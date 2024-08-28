#!/usr/bin/env groovy


def bob = "bob/bob -r \${WORKSPACE}/aws_credential_rotation/ruleset2.0.yaml"


def gerritReviewCommand = "ssh -p 29418 gerrit.ericsson.se gerrit review \${GIT_COMMIT}"
def verifications = [
        'Verified'  : -1,
]

pipeline {
    agent {
        label SLAVE
    }
    stages {
        stage('Prepare workspace') {
            steps {
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive'
            }
        }

        stage('Run Python') {
            steps {
                sh "${bob} docker:build-image"
                sh "${bob} docker:run"
            }
        }
    }
}

