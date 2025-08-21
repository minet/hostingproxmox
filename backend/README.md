# Proxmox API Backend

**Proxmox VPS provider API** - Backend service for the MiNET hosting platform

## Status
✅ **Fully functional** - All tests passing, Connexion 3.x migration completed  
- API version: 1.0.0
- Framework: Flask + Connexion 3.x + SQLAlchemy
- Test coverage: 38/38 unit tests + 5/5 integration tests ✅

## Recent Updates (August 2025)
- ✅ **Connexion 2.x → 3.x migration** completed
- ✅ **SQLAlchemy threading issues** fixed (VM creation no longer hangs)
- ✅ **ASGI/Starlette response handling** updated 
- ✅ **Test suite compatibility** restored

## Requirements
- Python 3.8+ (tested with 3.13)
- Flask with Connexion 3.x
- SQLAlchemy with Flask-SQLAlchemy
- Proxmox VE API access

## Installation & Usage

### Quick Start with uv (Recommended)
```bash
# Install uv if not already installed
pip install uv

# Install dependencies
uv sync

# Run the API server
uv run python -m proxmox_api

# Run tests
uv run pytest test/ -v
```

### Traditional pip install
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the API server
python -m proxmox_api
```

### Environment Configuration
Create a `.env` file with required environment variables:
```bash
export PROXMOX_HOST=<IP_PROXMOX_HOST>
export PROXMOX_API_KEY_NAME=<PROXMOX_API_KEY_NAME>
export PROXMOX_API_KEY=<PROXMOX_API_KEY>
export PROXMOX_BACK_DB=<PROXMOX_BACK_DB>
export ENVIRONMENT="DEV"  # or "PROD" or "TEST"
```

## Testing
The backend includes comprehensive test coverage:

```bash
# Unit tests (API endpoints)
uv run pytest test/test_default_controller.py -v

# Integration tests (VM lifecycle)
uv run pytest test/integration/ -v  

# All tests
uv run pytest test/ -v --tb=short
```

## API Architecture 
- **Framework**: Flask with Connexion 3.x (OpenAPI integration)
- **Database**: SQLAlchemy with SQLite (dev) / MySQL (prod)
- **Authentication**: OAuth2 with MiNET CAS
- **VM Management**: Proxmox VE API integration
- **DNS Management**: Integrated DNS server management

## Getting Started

### Development Server
1. Load environment variables: `source .env`
2. Start the development server: `uv run python -m proxmox_api`
3. API will be available at `http://localhost:8080`
4. OpenAPI documentation at `http://localhost:8080/ui/`

### Example API Usage
```python
import requests

# Get authentication token from MiNET CAS first
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# List all VMs
response = requests.get("http://localhost:8080/vm", headers=headers)
print(response.json())

# Get specific VM
vm_id = "123"
response = requests.get(f"http://localhost:8080/vm/{vm_id}", headers=headers)
print(response.json())

# Create VM
vm_data = {
    "type": "10G",
    "unsecure": False
}
response = requests.post("http://localhost:8080/vm", json=vm_data, headers=headers)
print(response.json())
```

### Database Management
```bash
# Initialize database (development)
uv run python -c "from proxmox_api.db.db_models import db; from proxmox_api import create_app; app = create_app(); app.app_context().push(); db.create_all()"

# Run database migrations (if applicable)
# Add your migration commands here
```

## Troubleshooting

### Common Issues

**VM Creation Hanging**: 
- ✅ Fixed in latest version via SQLAlchemy threading improvements
- Ensure `config_vm` function uses single app instance

**Connexion Import Errors**:
- ✅ Migrated to Connexion 3.x - use `FlaskApp` wrapper
- Update test clients to use `app.test_client()` instead of Flask's

**Response Format Issues**:
- ✅ Updated for Starlette responses - use `response.json()` not `response.json`

**Database Threading Issues**:
- ✅ Fixed SQLAlchemy app registration in background threads
- Use existing app context instead of creating new instances

## API Documentation

All URIs are relative to *http://localhost:8080* (development) or *https://api-hosting.minet.net/2.0* (production)

# Configure OAuth2 access token for authorization: OAuth2
## API Documentation

All URIs are relative to *http://localhost:8080* (development) or *https://api-hosting.minet.net/2.0* (production)

### Endpoints

| Method | HTTP Request | Description |
|--------|-------------|-------------|
| **POST** /dns | Create DNS entry |
| **GET** /dns | Get all user's DNS entries |
| **GET** /dns/{dnsid} | Get DNS entry by id |
| **DELETE** /dns/{dnsid} | Delete DNS entry by id |
| **POST** /vm | Create VM |
| **GET** /vm | Get all user VMs |
| **GET** /vm/{vmid} | Get VM by id |
| **PATCH** /vm/{vmid} | Update VM (start/stop/reboot) |
| **DELETE** /vm/{vmid} | Delete VM by id |
| **GET** /history/{vmid} | Get IP history of a VM |
| **GET** /historyall | Get IP history of all VMs |
| **GET** /account_state/{user} | Get account state |
| **GET** /cotisation | Check if cotisation is up to date |
| **GET** /expired | List expired accounts |

### Models
- **DnsEntryItem**: DNS entry data model
- **DnsItem**: DNS creation request model  
- **VmItem**: VM data model
- **VmIdItem**: VM identifier model
- **HistoryIdItem**: IP history data model

## Documentation for API Endpoints

All URIs are relative to *https://api-hosting.minet.net/2.0*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*DefaultApi* | [**create_dns**](docs/DefaultApi.md#create_dns) | **POST** /dns | create dns entry
*DefaultApi* | [**create_vm**](docs/DefaultApi.md#create_vm) | **POST** /vm | create vm
*DefaultApi* | [**delete_dns_id**](docs/DefaultApi.md#delete_dns_id) | **DELETE** /dns/{dnsid} | delete dns entry by id
*DefaultApi* | [**delete_vm_id**](docs/DefaultApi.md#delete_vm_id) | **DELETE** /vm/{vmid} | delete vm by id
*DefaultApi* | [**get_dns**](docs/DefaultApi.md#get_dns) | **GET** /dns | get all user&#x27;s dns entries
*DefaultApi* | [**get_dns_id**](docs/DefaultApi.md#get_dns_id) | **GET** /dns/{dnsid} | get a dns entry by id
*DefaultApi* | [**get_historyip**](docs/DefaultApi.md#get_historyip) | **GET** /history/{vmid} | get the ip history of a vm
*DefaultApi* | [**get_historyipall**](docs/DefaultApi.md#get_historyipall) | **GET** /historyall | get the ip history of all the vm
*DefaultApi* | [**get_vm**](docs/DefaultApi.md#get_vm) | **GET** /vm | get all user vms
*DefaultApi* | [**get_vm_id**](docs/DefaultApi.md#get_vm_id) | **GET** /vm/{vmid} | get a vm by id
*DefaultApi* | [**is_cotisation_uptodate**](docs/DefaultApi.md#is_cotisation_uptodate) | **GET** /cotisation | check is the cotisation is up to date for a user
*DefaultApi* | [**patch_vm**](docs/DefaultApi.md#patch_vm) | **PATCH** /vm/{vmid} | update a vm

## Documentation For Models

 - [DnsEntryItem](docs/DnsEntryItem.md)
 - [DnsItem](docs/DnsItem.md)
 - [HistoryIdItem](docs/HistoryIdItem.md)
 - [VmIdItem](docs/VmIdItem.md)
 - [VmItem](docs/VmItem.md)

## Documentation For Authorization


## OAuth2

- **Type**: OAuth
- **Flow**: implicit
- **Authorization URL**: https://cas.minet.net/oidc/authorize
- **Scopes**: 
 - **profile**: The user&#x27;s basic information, including groups they are a part of
 - **admin**: Scope for admin users


## Author

webmaster@listes.minet.net
