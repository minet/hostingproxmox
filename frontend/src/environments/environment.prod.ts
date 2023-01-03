

function getBackendURL(){
  const url = window.location.hostname;
  let backendURL = "https://backprox.minet.net";
    
    switch(url){
      case "hosting-dev.minet.net" : {
        backendURL = "https://backprox-dev.minet.net";
        break;
      }
      case "hosting-local.minet.net" :{
        backendURL = "http://localhost:8080";
         break;
      }
      default: {
        backendURL = "https://backprox.minet.net";
        break;
      } 
    }
    return backendURL;
}export const environment = {
  production: true,
  backendURL: getBackendURL(),
};
