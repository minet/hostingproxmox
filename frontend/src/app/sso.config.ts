import { AuthConfig } from 'angular-oauth2-oidc';

export const authCodeFlowConfig: AuthConfig = {

  redirectUri: window.location.origin + '/',
  clientId: 'k8s',
  scope: 'openid profile offline_access roles',
  issuer: 'https://cas.minet.net/oidc',
  tokenEndpoint: 'https://cas.minet.net/oidc/accessToken',
  oidc: true,
  dummyClientSecret: 'thisisneededforApereoCAS',
  responseType: 'code',
  showDebugInformation: false,
};
