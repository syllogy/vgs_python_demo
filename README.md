# VGS ECommerce Demo - Python

**Coming soon! WIP:**
This demo is functional but will recieve some key updates in coming weeks.    

This demo app demonstrates a typical scenario for operating with sensetive data to showcase how a typical ecommerce shopping card checkout flow can be integrated with VGS to secure the sensitive data. The benefit is that we can remove the sensitive PCI footprint of data from our application and database. VGS is fully PCI-DSS compliant and allows you to build an application which has very limited or zero audit footprint.    

{flow diagram forthcoming}

## Use case

**There are 2 customer services**
1. **Order Service** (Shopping cart checkout flow) 
2. **Merchant Portal** - manage payments, disputes, etc..
and       
3. **3rd party Payment Service simulation.** << This represents whatever 3rd party processor integration you may have.    

Users can go to Order Service **(cart checkout screen)** and place order(s) with their payment's data (card number, billing address, etc). When user places an order the payment information is stored in customer's storage. It can be later processed in Merchant Portal.   

An authorized user of Merchant Portal can charge the payment - 
this action initiates call to an external Payment Service.    

- Order Service (http://localhost:8080)
- Merchant Portal (http://localhost:8080/merchant_admin/payments)
- Payment Service (http://localhost:8080/processor_admin/charges)

## Demo scenario

See how data is going through services without VGS proxy used:
- go to Order Service, fill payment data and place an order (you can use auto-generated values or find fake credit cards numbers here: http://www.getcreditcardnumbers.com/)
- go to Merchant Portal and verify the corresponding payment was created
- charge the payment on Merchant Portal
- go to the Payment Service and verify the payments data was received

Configure VGS Proxy to redact sensetive data sent to the Order Service and reveal data when sending payment's information to Payment System:
- go to https://dashboard.verygoodsecurity.com and configure VGS Proxy to redact the sensetive data on the way in (credit card number and CVV code)
- go to Order Service, fill payment data and place an order
- go to Merchant Portal and verify the payment's info does NOT contain a sensetive information
- go to https://dashboard.verygoodsecurity.com and configure VGS Proxy to reveal the sensetive data on the way out (when sent to Payment Service)
- go to the Payment Service and verify the payments data with the actual credit card number/CVV code was received

## Cart checkout form:    
![checkout](/docs/checkout-form.png)    

## Merchant's portal form:    
![checkout](/docs/merchant_portal.png)    

## Payment Processor Admin Form (Simulated):        
![checkout](/docs/processor_form.png)      


## Run Demo App
**We will use** [Docker](https://docker.com) to run the app.

### Build

```bash
docker build . -t python_demo
```

### Run

```bash
docker run -it \
   -p 3000:3000 -p 3001:3001 -p 8080:8080 \
   --rm --name python_demo -v $(pwd):/opt/app/src \
   python_demo
```
In order to use proxy for sending data to Payment Service `HTTPS_PROXY` environment variable needs to be set, i.e.:
```bash
docker run -it \
   -p 3000:3000 -p 3001:3001 -p 8080:8080 \
   --rm --name python_demo -v $(pwd):/opt/app/src \
   -e HTTPS_PROXY=https://user:pass@proxy.com:port \
   python_demo
```


### Expose to Internet

**For local development:**    
In order to integrate the app running on your local machine with VGS proxy you'll have to expose the app to the internet. This will allow us to 'insert' the VGS proxy between middle and backend components as you would via a live app on the Internet. 

Use [ngrok](https://ngrok.com/).  This handy tool and service lets you set up a secure tunnel to your localhost, which is a fancy way of saying it opens access to your local app from the internet.

#### Step 1: Download ngrok
Go to https://ngrok.com/ and download the version that corresponds to your platform. In our case, we'll be downloading the Mac OS X 64-bit version.

#### Step 2: Install ngrok
Installing ngrok really only consists of extracting the file. Depending on how you want to run the app, you need to pay attention to where you extract the file:

a) You can extract ngrok into the folder of your preference and run ngrok from there.

or

b) **(Recommended)** Extract ngrok on your system's $PATH directory. The advantage of going with this option is that you'll be able to run ngrok from any path on the command line.

To get your system's $PATH simply type from the Terminal:
```
echo $PATH
```
In most cases this is usually:
```
/usr/local/bin
```
#### Step 3: Tunnel your server
It's time to run ngrok and let the magic happen.

{Diagram forthcoming}

If you went for option A on Step 2, fire up a Terminal window, navigate to the directory where you unzipped ngrok and start it by telling it which port we want to expose to the public internet. To do this,type:
```bash
./ngrok http 8080
```
If ngrok is on your $PATH, you can simply type the following from any directory:
```bash
ngrok http 8080
```
If all goes well you should see the following:
```
ngrok running
```

#### Step 4: Route requests to Payment Service to go via ngrok
To be able to configure VGS proxy for requests going to Payment Service(`/charge` endpoint) your app should route these requests via ngrok, `VGS_PROCESSOR_ROOT_URL` environment variable should be set:
```bash
docker run -it \
   -p 3000:3000 -p 3001:3001 -p 8080:8080 \
   --rm --name python_demo -v $(pwd):/opt/app/src \
   -e HTTPS_PROXY=https://user:pass@proxy.com:port \
   -e VGS_PROCESSOR_ROOT_URL=https://<your id>.ngrok.io/charge \
   python_demo
```

## Set up proxy rules
Some quick tips on how to set up VGS proxies for use with this application.

### Reverse Proxy
(Reference: https://www.verygoodsecurity.com/docs/reverse-proxy).

* Use reverse proxy URL to access Order Service, e.g. `https://<your tenant id>.SANDBOX.verygoodproxy.com`
* Set upstream to ngrok address, e.g. `https://e907262d.ngrok.io`
* Filter condition should be PathInfo equals `/payment`
* Operation is to **REDACT** form fields:
    - `card-number`
    - `card-security-code`

### Forward Proxy
(Reference: https://www.verygoodsecurity.com/docs/forward-proxy).

* Set `HTTPS_PROXY` to forward proxy URL
* Set `VGS_PROCESSOR_ROOT_URL` to something like this: `https://e907262d.ngrok.io/charge`
* Set upstream to ngrok address, just like with the reverse proxy
* Filter condition should be PathInfo equals `/charge`
* Operation is to **REVEAL** JSON fields:
    - `$.card`
    - `$.card_security_code` 
    
## Example proxy rules:    
![VGS Proxy rules:](/docs/rules.png)     


## Used Technologies/Tools:

HTML, CSS, JS, scss, Gulp, NPM, Git, Python
