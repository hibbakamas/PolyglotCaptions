# Definition of Done – Sprint 3


## Backend
- [ ] Router structure implemented for `/caption` and future endpoints
- [ ] Azure Translator service integration completed
- [ ] Azure SQL database schema designed and deployed
- [ ] Caption and translation logging to Azure SQL implemented
- [ ] Error handling for Azure services (Translator, SQL)
- [ ] Environment variables configured for Azure credentials
- [ ] Automated tests updated for new router structure
- [ ] Integration tests for Azure Translator service
- [ ] Tests run successfully locally and via pipeline


## Frontend
- [ ] Frontend connected to backend `/caption` endpoint
- [ ] Real-time display of Azure Translator results
- [ ] Error handling for backend connection failures
- [ ] Loading states during translation processing
- [ ] UI feedback for successful caption logging


## DevOps
- [ ] Azure resources provisioned (Translator, SQL Database)
- [ ] Connection strings and secrets stored in Azure Key Vault or GitHub Secrets
- [ ] Pipeline updated to run integration tests against Azure services
- [ ] Pipeline triggers on commit/PR
- [ ] Tests executed automatically
- [ ] Failures stop build


## Documentation
- [ ] README updated with Azure setup instructions
- [ ] ARCHITECTURE updated with Azure Translator and SQL integration
- [ ] Environment variables documented in README
- [ ] Database schema documented
- [ ] DOD.md updated