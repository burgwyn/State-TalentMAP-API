//FAKING BRANCH FOR TESTING
BRANCH_NAME = "dev"
/**
* Constants & Global Variables
*/
def GITHUB_URL = "https://github.com/18F/State-TalentMAP-API"

def AWS_REGION = "us-east-1"

def CLUSTER_NAME = "TalentMAP"
def TASK_FAMILY = "${CLUSTER_NAME}_${BRANCH_NAME}"
def SERVICE_NAME = "${TASK_FAMILY}_service"

def IMAGE_BUILD_TAG = "v_${BRANCH_NAME}_${env.BUILD_NUMBER}"
def DOCKER_REGISTRY = "https://346011101664.dkr.ecr.us-east-1.amazonaws.com"
def DOCKER_IMAGE_NAME = "talentmap/api"

def JOB = "${env.JOB_NAME}".split('/')[0]

def taskRevision, desiredCount

/**
* Core Pipeline
*/
node('talentmap_base') {
  try {
    stage ('Checkout'){
      git branch: "${BRANCH_NAME}", credentialsId: '7a1c5125-103d-4a1a-8b2f-6a99da04d499', url: "${GITHUB_URL}"
    }
    stage ('Build') {
      buildDockerImage("${DOCKER_IMAGE_NAME}")
    }
    stage ('Push') {
      def loginCmd = getECRLoginCmd()
      sh "${loginCmd}"
      pushDockerImage("${DOCKER_REGISTRY}", "${DOCKER_IMAGE_NAME}", "${IMAGE_BUILD_TAG}")
    }

    stage ("Deploy – Update Task Definition") {
      // Create a new task definition for this build
      updateTaskDefinition("${IMAGE_BUILD_TAG}", "${TASK_FAMILY}")
    }
    stage ("Deploy – Update Service") {
      // Update the service with the new task definition and desired count
      taskRevision = getTaskDefRevision("${TASK_FAMILY}")
      desiredCount = getEcsServiceDesiredCount("${SERVICE_NAME}")
      updateEcsService("${CLUSTER_NAME}", "${SERVICE_NAME}", "${TASK_FAMILY}", taskRevision, desiredCount)
    }

  } catch (Exception err) {
    currentBuild.result = 'FAILURE'
    println err
  }
}

if ("${BRANCH_NAME}".equals("test")) {
  node('talentmap_base') {
    try {
      stage ('Test – Checkout'){
        git branch: "${BRANCH_NAME}", credentialsId: '7a1c5125-103d-4a1a-8b2f-6a99da04d499', url: "${GITHUB_URL}"
      }
      stage ('Test – Bandit') {
        sh 'pip --no-cache-dir install bandit'
        sh 'bandit -r .'
      }
    } catch (Exception err) {
      currentBuild.result = 'FAILURE'
      println err
    }
  }
  node('owasp_zap') {
    try {
      stage ('Test – ZAP') {
        def testDeploymentUri = findUriForEcsService("${CLUSTER_NAME}", "${SERVICE_NAME}")
        sh "zap-cli quick-scan --self-contained --start-options '-config api.disablekey=true' ${testDeploymentUri}"
      }
    } catch (Exception err) {
      currentBuild.result = 'FAILURE'
      println err
    }
  }
  node('talentmap_base') {
    try {
      stage ('Test – Cleanup'){
        updateEcsService("${CLUSTER_NAME}", "${SERVICE_NAME}", "${TASK_FAMILY}", taskRevision, desiredCount)
      }
    } catch (Exception err) {
      currentBuild.result = 'FAILURE'
      println err
    }
  }
}

/**
* Docker Methods
*/
def pushDockerImage(String dockerRegistry, String dockerRepoName, String tag){
  docker.withRegistry("${dockerRegistry}") {
    docker.image("${dockerRepoName}").push("${tag}")
  }
}

def buildDockerImage(String dockerRepoName){
  docker.build("${dockerRepoName}")
}

/**
* EC2 Container Service (ECS) Methods
*/
def getECRLoginCmd() {
  def loginCmd
  stage ('Get ECR Login'){
    sh "aws ecr get-login --region us-east-1 > login.txt"
    loginCmd = readFile('login.txt')
    sh "rm -f login.txt"
  }
  return loginCmd
}

def updateTaskDefinition(String buildTag, String taskFamily) {
  def outputFileName = createTaskDefinitionJson(buildTag, taskFamily)
  registerTaskDefinition(outputFileName, taskFamily)
}

def createTaskDefinitionJson(String buildTag, String taskFamily){
  def outputFileName = "TD_${taskFamily}_${buildTag}.json"
  sh "aws ecs --region ${AWS_REGION}  describe-task-definition --task-definition ${taskFamily} | jq '.taskDefinition.containerDefinitions = (.taskDefinition.containerDefinitions | map( if .name == \"${JOB}\" then .image = \"${DOCKER_IMAGE_NAME}:${buildTag}\" else . end ))' > ${outputFileName}"
  return "${outputFileName}"
}

def registerTaskDefinition(String taskDefFileName, String taskFamily) {
  sh "aws --region ${AWS_REGION} ecs register-task-definition --family ${taskFamily} --cli-input-json file://${taskDefFileName}"
}

def getTaskDefRevision(String taskFamily) {
  def revision = sh "aws --region ${AWS_REGION} ecs describe-task-definition --task-definition ${taskFamily} | jq '.taskDefinition.revision'"
  return revision
}

def getEcsServiceDesiredCount(String clusterName, String serviceName) {
  def desiredCount = sh "aws --region ${AWS_REGION} ecs describe-services --cluster ${clusterName} --services ${SERVICE_NAME} | jq '.services[0].desiredCount'"
  if (desiredCount == 0) {
    desiredCount = 1
  }
  return desiredCount
}

def updateEcsService(String clusterName, String serviceName, String taskFamily, String taskRevision, String desiredCount) {
  sh "aws --region ${AWS_REGION} ecs update-service --cluster ${clusterName} --service ${serviceName} --task-definition ${taskFamily}:${taskRevision} --desired-count ${desiredCount}"
}

def findUriForEcsService(String clusterName, String serviceName) {
  //NOTE: Double-check line if multiple load balancer come into play
  def targetGroupArn = sh "aws --region ${AWS_REGION} ecs  describe-services --cluster ${clusterName} --service ${serviceName} | jq -r '.services[0].loadBalancers[0].targetGroupArn"
  def targetGroup = sh "aws --region ${AWS_REGION} elbv2 describe-target-groups --target-group-arns ${targetGroupArn}"
  def lbArn = sh "echo \"${targetGroup}\" | jq -r '.TargetGroups[0].LoadBalancerArns[0]'"
  def healthCheckPath = sh "echo \"${targetGroup}\" | jq -r '.TargetGroups[0].HealthCheckPath'"
  //NOTE: Assuming that the base URI of the container is the same as the healthCheckPath
  def lbDns = sh "aws --region ${AWS_REGION} elbv2 describe-load-balancers --load-balancer-arns ${lbArn} | jq -r '.LoadBalancers[0].DNSName'"
  return "${lbDns}${healthCheckPath}"
}