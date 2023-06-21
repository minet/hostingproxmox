// This file can be replaced during build by using the `fileReplacements` array.
// `ng build --prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.
function getBackendURL(){
  const url = window.location.hostname;
  let backendURL = "https://api-hosting.minet.net";
    
    switch(url){
      case "hosting-dev.minet.net" : {
        backendURL = "https://api-hosting-dev.minet.net";
        break;
      }
      case "hosting-local.minet.net" :{
        backendURL = "http://localhost:8080";
         break;
      }
      default: {
        backendURL = "https://api-hosting.minet.net";
        break;
      } 
    }
    return backendURL;
}
export const environment = {
  production: false,
  
  backendURL: getBackendURL(),
  
};

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/dist/zone-error';  // Included with Angular CLI.
