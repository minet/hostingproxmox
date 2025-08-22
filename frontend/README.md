# ProxmoxDashboard Frontend

Angular frontend for the MiNET Hosting Proxmox platform. This provides the web interface for managing VMs and DNS entries through the Proxmox API backend.

## Project Info
- **Framework**: Angular 14 with Angular CLI
- **Backend API**: Connects to Proxmox API backend on port 8080
- **Authentication**: OAuth2 integration with MiNET CAS
- **Status**: ✅ Compatible with updated Connexion 3.x backend

## Prerequisites
- Node.js (version 14+ recommended)
- npm or yarn
- Angular CLI (`npm install -g @angular/cli`)

## Quick Start

### Installation
```bash
cd frontend/
npm install
```

### Development server
```bash
# For local development with backend running on localhost:8080
ng serve --host=127.0.0.1 --disable-host-check

# Navigate to http://hosting-local.minet.net:4200/
# Note: You MUST use hosting-local.minet.net domain for proper backend API routing
```

### Local Development Setup
The frontend determines the backend API URL based on the domain:
- `hosting-local.minet.net:*` → `http://localhost:8080` (local backend)
- `hosting-dev.minet.net:*` → Development backend
- `hosting.minet.net:*` → Production backend

**Important**: Add this to your `/etc/hosts` file for local development:
```bash
127.0.0.1 hosting-local.minet.net
```

### Available Scripts

#### Development
```bash
# Start dev server
ng serve --host=127.0.0.1 --disable-host-check

# Start dev server with specific port
ng serve --host=127.0.0.1 --disable-host-check --port 4200
```

#### Code Generation
```bash
# Generate component
ng generate component component-name

# Generate service  
ng generate service service-name

# Generate other artifacts
ng generate directive|pipe|service|class|guard|interface|enum|module
```

#### Build
```bash
# Development build
ng build

# Production build
ng build --prod
```
The build artifacts will be stored in the `dist/` directory.

#### Testing
```bash
# Unit tests via Karma
ng test

# End-to-end tests via Protractor  
ng e2e
```

## Project Structure
```
src/
├── app/                 # Main application components
├── assets/             # Static assets
├── environments/       # Environment configurations
├── index.html         # Main HTML file
└── styles.css         # Global styles
```

## API Integration
The frontend communicates with the Proxmox API backend using:
- **Authentication**: OAuth2 tokens from MiNET CAS
- **HTTP Client**: Angular HttpClient for API requests
- **Error Handling**: Comprehensive error handling for API responses
- **Real-time Updates**: Polling for VM status changes

## Troubleshooting

### Common Issues

**CORS Issues**:
- Ensure backend is running with proper CORS configuration
- Use the correct domain (`hosting-local.minet.net`) for local development

**Backend Connection**:
- Verify backend is running on `http://localhost:8080`
- Check network connectivity and firewall settings
- Ensure environment-based API URL routing is working

**Authentication Issues**:
- Verify MiNET CAS integration is configured
- Check OAuth2 token validity and refresh mechanisms

## Further Help
For more help on Angular CLI use `ng help` or check out the [Angular CLI Overview and Command Reference](https://angular.io/cli).
