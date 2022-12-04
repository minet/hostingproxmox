# [Beta 3.0.0] 03-10-2022

## Added 
- [Handling of end cotisation](http://gitlabint.priv.minet.net/hosting/api/-/commit/27d6f82247a2eae0f55b3b147b7db978e6808c62) - *The frontend is now able to display to the user when its cotisation is expired and what to expect from it. It adapts according to the freeze status. The backend also handle this feature. Firstly to deal with this new user property and secondly to protect all endpoint. Fix #5. Fix #16.*

## Fixed 
- [All types of ssh keys are now supported](http://gitlabint.priv.minet.net/hosting/api/-/commit/9366bbbdd4aba06d5fc84441d7fa5593feaa8950) - *The regex in charge of checking ssh keys was blacklisting valid keys. Fix #32*

# [Beta 2.1.0] 01-10-2022

## Added 
- [Possibility to update the cloud init creds](http://gitlabint.priv.minet.net/hosting/api/-/commit/46ea63a013edec2d8f1ff7f98f64768c898d55e8) - *For now this feature is only available when restoring a VM after losing its data*

- [Add a information, warning and call to actions after the data lost of VMs](http://gitlabint.priv.minet.net/hosting/api/-/commit/7b66d7a7665d86af8490b407eedddea735a3dd64) - *For data lost from prod only*
# [Beta 2.0.1] 09-10-2022
## Added 

- [Search bar for admin](http://gitlabint.priv.minet.net/hosting/api/-/commit/9a33083ec78f53b2be5e2f1c70050c5ac650966a) - *Add a search field for admin in order to retrieve a vm from its name or owner. Fix #7*


# [Beta 2.0] 19-09-2022

## Added 

- [French translation](http://gitlabint.priv.minet.net/hosting/api/-/commit/e01fc085e4870f11ebdd4b9ace98ce090493105e) - *Add the whole french translation for the project.*

- [API endpoint to handle vm deletion when an error occured](http://gitlabint.priv.minet.net/hosting/api/-/commit/22e6a051b376e535d7349a770d5b4474a09ac8bb)

- [Frontend possibility to destroy a ghost VM](http://gitlabint.priv.minet.net/hosting/api/-/commit/f08bb4b4889441978ea8aacbe1f435b2f1fe6923) - *The user can now open it and it doesn't load forever in the VM list page*

- [Add a pop up to validate a VM deletion](http://gitlabint.priv.minet.net/hosting/api/-/commit/c23f28c24523cb1bf26db835a189ed7f56355725)

## Changed 
- [Upgrade angular to angular 14](http://gitlabint.priv.minet.net/hosting/api/-/commit/2a336475bed2c6fed987c0e175ec79e29b278070)

- [Complete re-definition of the deletion backend method](http://gitlabint.priv.minet.net/hosting/api/-/commit/e8ef687050a141040d2e522f8f818a7d221c3763) - *The deletion func is now devided in two func : delete_from_db and delete_from_proxmox. They are just deleting the VM from the two instances and are called internally or by default_controller depending of the type of deletion. A common deletion func in called in thread an handle the errors and the update of the vm state*.

- [Update the VM creation status to get vm state to be more clearer](http://gitlabint.priv.minet.net/hosting/api/-/commit/09e9f488966d04f2ac730bbd9cd9526b9597c01c) 

- [Better handle of http errors message in the fronted](http://gitlabint.priv.minet.net/hosting/api/-/commit/c23f28c24523cb1bf26db835a189ed7f56355725) - *Better handle errors message which directly embedd the http code, http code description and error description in the page. Add a pop up to force user to write down the VM id to validate the deletion*

## Fixed 
- [Fix the issue causing the impossibility to delete an existing VM when an error occured](http://gitlabint.priv.minet.net/hosting/api/-/issues/21) - *Fix issue #21. The VM deletion is 100% rewritten with a heavy and resilient process able to delete a VM when an error occured during its creation, delete a VM when the user wanted to do so (it was working before but without any feedback for the user)*

- [A user can now open and display an 'ghost VM'](http://gitlabint.priv.minet.net/hosting/api/-/commit/f08bb4b4889441978ea8aacbe1f435b2f1fe6923) - *A ghost VM is a VM created in the db but not on proxmox. The was causing a infinite loading in the VM list page and an error while trying to display information about it.*
# [Beta 1.2] 31-07-2022
## Fixed 

- [User can no longer create any DNS entry ](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/aca9c8ce893c374d1aefbdde68cba2e62c01df1f) -  *Issue #15. It must be a DNS entry with alphanumeric char. It is tested by both  backend and frontend.*

- [User can no longer create any DNS entry for an ip they don't own](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/aca9c8ce893c374d1aefbdde68cba2e62c01df1f) -  *Issue #19. It is tested by both  backend and frontend.*

- [Fix of ALL error message with a http error code clear and accurate and an error message explicit](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/aca9c8ce893c374d1aefbdde68cba2e62c01df1f) -  *Issue #18. All error messages have been rewritten and the error display pop up embed now new fields*.

- [Fix an issue causing the stop of all the ip attribution if one of them fail](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/92b6464dc37d388a0ae5a908d11ec451f8949d2c) - *The job updating the ip is now error-resiliant and doesn't fail for all when fails for one.*

## Added 
- [Add a util method able to translate an http code to a http message](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/cee3c93c36506f5818ed55839ea0860424456229)

- [The api endpoint /ips to retrieve the list of ips of a user.](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/aca9c8ce893c374d1aefbdde68cba2e62c01df1f) 

- [A json file to store the vm status](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/82189f7139cae0b56bea7941a81a60c2d84f01d2) - *Indeed, a global variable cannot be used threw the different gunicorn instances*

- [Force reinstall python packages](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/84fdc27f336e88c7f659dcd523d985c21c66e435) - *Some of the packages where deprecated and caused run time error*
## Changed

- [The job in charge of updating all the ips address is now executed each 2 min](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/cee3c93c36506f5818ed55839ea0860424456229) - *Instead of each 10s before. It doesn't fix the slow ip attribution issue.*

- [The vm creation processus is now more error-resiliant](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/92b6464dc37d388a0ae5a908d11ec451f8949d2c) - *When a vm is created, its state is saved in a json until an error or an success. When one of them happens, the backend waits for a call by the user, throw the final result and delete the json entry. This attributes is now displayed when /vm/vmid is called, instead of the frontend guess of the vm status (it also brings a very important feature : the display of very accurate error messages)*

- [README to stick with the new backend URL automatic calculation](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/f457f845e6b4a468425c487cb2c27e4e581990bf)
# [Beta 1.1] 24-06-2022
## Fixed 

- [Fix the VM creation crash when the VM user name was 'root'](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/3200b9323f27c1c0de7872c86b1260574d80fba4) *The user named 'root' is now prohibited ([frontend](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/3200b9323f27c1c0de7872c86b1260574d80fba4) and [backend](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/db84005dc5f9c448e3c8e607be405bdca1d2bab0)).*

- [Fix the VM init in the db but not created in proxmox if the user leaves hosting during the vm creation process](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/1269ff07cd2d68d688f4eb4c0c00c4471504981d) - *Issue #6. More info below.*


- [Fix the VM creation which always crash and progress bar which starts over and stops sometimes](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/1269ff07cd2d68d688f4eb4c0c00c4471504981d) - *Issue #9. More info below.*

- [While the backend is build, it checks if the env variables are well defined and exported](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/299c874e3456e99b22a3b1e4ee25d7bdee31a75d) - *It fixes runtime errors (with no link to this issue) when the backend was not able to retrieve the wanted variables. It's now crash on build with debug info (improved by this [commit](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/e51b6613c006613eb862451eee4d84ff7952a9fe)).*

- [Fix the favicon path which was dead](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/8c1713990b5417c0a57a90ac8459afdb74940e87) - *And a little [fix](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/3f669dabce4b6520ef6973dc26c7e170b75477cd) of this commit*



## Added 
- **[A password length checker](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/307fe3ad4285aefedcd31f8b393cc6f774301cf6)** - *User passwords have now to respect the CNIL's recommandations : at least 1 uppercase, 1 special char, 1 number and contain 12 characters. It's a frontend checker which not allows you to submit the creation form if these conditions are not respected.*

- [A patch for cloud init and sshd configurations](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/962c33729a894edb390e208208d22d46f60b5036) - *In order to upgrade the hosting's security policies, there are two patchs in shellbash that can be downloaded and executed on a VM. The cloud init patch change the sudoers configuration to force user using a password when entering in sudomod. The sshd patch force users to use a key for SSH connection.*

- [Security for the sshd conf patch](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/512a75d9a7d24dc927441eac9be60eb54b2bac36) -  *The patch script checks if the .ssh contains keys before patching.*

- [Force SSH key when create a VM and prohibit some VM user name ](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/3200b9323f27c1c0de7872c86b1260574d80fba4) - *A VALID SSH key is now mandatory when creating a VM. The user named 'root' is also now prohibited.*

- [Support of hosting-dev deployment](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/34f760be714029fcbd08d1fc1bce6f1eac2298f0) - *A new web app has been created : hosting-dev.minet.net, to test in production environnement the new versions of hosting. A special CI/CD is now dedicated to deploy hosting-dev when push are made on the development branch.*

- [Backend checks for user input when create a VM](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/db84005dc5f9c448e3c8e607be405bdca1d2bab0) - *The Backend now does a double check with the front on user information when creating a VM. It checks as many things as the fronted and throw an explicit error if the rules are not respected.*

- [User manual for SSH key creation](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/fec029436c116d7967507978b36c6f7776bc84b1) - *Add explanations in french and english for how to create a SSH key and how to use it.*

- [New link on the VM creation form to the SSH key manual](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/bcfebf36d77b1580e4b2e2399373e0503c8af6a5) - *Add a direct link to the manual page (about SSH key) in the VM creation form.*

- [Usage of font awesome for beautiful icons](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/e28deddeba2cc2ca365d9847d095c1b8a5de98ea) 

- [Backend checks the password strength, the ssh_key format, and the username](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/0cec6e387d62725e63481482b291b9234f6ef964) - *This is le last checks needed by the backend to fully test the user's info. Now frontend and backend are redundant and resilient*

- [Add the GNU v3 Licence to the project](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/506f5e52881308f8d200660a61331654b6e028d5) 

- [The new VM creation method (frontend) waits for multiple errors to throw them to the user](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/c1ce51d0691e70f62f4a109ab9cfb2b11591f4b7) - *After some tests, it appears thats the front needs to wait for several request error to return the error to the user. With the new async method to create vm, a request lost cannot be reliable. Now, the front must have 5 consecutive backend errors to trust them*

- [Different html 'title', according to the type of hosting running (prod, dev, local)](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/4b30a18eb7bd263eb301900e70ead62211a3cf66)

- [Add https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/a5c2dd1240d653f44dac966ab078d53d5a687495

## Changed


- [Swagger code changed to get ride of 'is using a ssh key' field](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/1fa1457935bb95a875d55348b66c74208746877a) - *When the rule to only use a SSH key, this field is deprecated. The code has been generated but not yet merge.*

- [Better error handling when create a VM](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/01c4997a5aa7a8655cd003488b9959c4b495635f) - *In case of error (client or server side) the fronted now displays the new explicit error message to the user and enables him to edit the VM creation form, instead of displaying a generic error and only one possibility : refresh the page and restart all over.*

- [Update of the package CommonJS](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/2c2e7ae67300ea2014be3611c0da912776586015) - *It envoles updates of code, especially when calling the dependency*

- [Usage of yarn to build the project](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/ec2b380fdacf17ca8fca3b4a643b1b53ba968bb8) - *Instead of a classic ng build.*

- [Totally new design of the VM creation method (backend)](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/1269ff07cd2d68d688f4eb4c0c00c4471504981d) - *The VM creation is now devided in two separated parts. The first one creates the VM by cloning the template and return a success code to the front. The second one **(executing async)** waits for the vm to be created to set up the vm (with user info). The VM deletion (called if there is an error while creating the VM) is corrected.*

- [Totally new design of the VM creation method (fronted)](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/24dc0fbb4dfe4f7fd659bbcec5f89210d615bcf8) - *In view of the VM new design of the VM creation method, the frontend now just inits the vm creation and then the frontend checks every 2s if the VM is created. If an error occured (backend), then the VM is deleted and the get request return 404. So the frontend knows it can display a VM error. Moreover, the VM creation isn't based anymore on a unique request which takes few minutes and timeout. + the frontend now handles very well all the errors + the vm page is show if the vm creation succeed + the progress bar is more smooth and realistic*

- [The project is now able to use the right backend and API urls (depends on the usage (dev, prod, local))](https://gitlab.minet.net/zastava/hosting-proxmox/-/commit/dce0af65054e4a96f381a59a89ec7e84e3694e47) - *It is no more expected to change the allowed URL for OAuth path and source url in auth service (it caused CI/CD errors). It is now adapted on the use of hosting.minet.net --> backprox.minet.net, hosting-dev.minet.net --> backprox-dev.minet.net and hosting-local.minet.net --> localhost:8080* **WARNING : a local DNS entry is now mandatory for hosting-local.minet.net** *or the prod backend will be used by default.*
