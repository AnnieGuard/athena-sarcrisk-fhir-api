name: Build and Deploy to Azure Container Apps

on:
  push:
    branches:
      - main
  workflow_dispatch:

env:
  REGISTRY: sarcomaapiregistry.azurecr.io
  IMAGE_NAME: athena-sarcrisk-fhir-api
  RESOURCE_GROUP: sarcoma-api-rg
  CONTAINER_APP_NAME: athena-sarcrisk-fhir-api
  CONTAINER_APP_ENV: sarcoma-api-env

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to container registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.AZURE_CLIENT_ID }}
          password: ${{ secrets.AZURE_CLIENT_SECRET }}
      
      - name: Set build version
        id: version
        run: echo "build_version=$(date +'%Y%m%d').${{ github.run_number 
}}" >> $GITHUB_OUTPUT
      
      - name: Build and push container image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ 
steps.version.outputs.build_version }}, ${{ env.REGISTRY }}/${{ 
env.IMAGE_NAME }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Log in to Azure
        uses: azure/login@v1
        with:
          creds: |
            {
              "clientId": "${{ secrets.AZURE_CLIENT_ID }}",
              "clientSecret": "${{ secrets.AZURE_CLIENT_SECRET }}",
              "subscriptionId": "${{ secrets.AZURE_SUBSCRIPTION_ID }}",
              "tenantId": "${{ secrets.AZURE_TENANT_ID }}"
            }
      
      - name: Deploy to Azure Container Apps
        uses: azure/CLI@v1
        with:
          inlineScript: |
            az containerapp update \
              --name ${{ env.CONTAINER_APP_NAME }} \
              --resource-group ${{ env.RESOURCE_GROUP }} \
              --image ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ 
steps.version.outputs.build_version }} \
              --set-env-vars "ENVIRONMENT=production" \
              --query properties.configuration.ingress.fqdn
      
      - name: Add deployment summary
        run: |
          echo "### Deployment Status: ✅ Success!" >> 
$GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "Deployed version: ${{ steps.version.outputs.build_version 
}}" >> $GITHUB_STEP_SUMMARY
          echo "Container App URL: https://${{ env.CONTAINER_APP_NAME 
}}.ashystone-7ad37a18.eastus.azurecontainerapps.io" >> 
$GITHUB_STEP_SUMMARY

