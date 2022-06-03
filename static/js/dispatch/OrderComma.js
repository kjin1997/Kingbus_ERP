const commaContractAmount = document.querySelector("#contractAmount");
const commaDriverPay = document.querySelector("#driverPay");
const btn = document.querySelector("#dispatchOrderCreateButton");

commaContractAmount.addEventListener("focusout", getCommaValueContractAmount);
commaContractAmount.addEventListener("focusin", returnCommaValueContractAmount);
commaDriverPay.addEventListener("focusout", getCommaValueDriverPay);
commaDriverPay.addEventListener("focusin", returnCommaValueDriverPay);

console.log(btn, commaDriverPay)


function getCommaValueContractAmount() {
  const commaValue = commaContractAmount.value;
  const newValue = commaValue.toString()
    .replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",");
    commaContractAmount.value = newValue;
}

function returnCommaValueContractAmount(){
  const commaValue = commaContractAmount.value;
  const newValue = commaValue.replace(/,/g, "");
  commaContractAmount.value = newValue;  
}

// input에는 submit이벤트가 적용 안됨
//btn.addEventListener("submit", removeComma)

function removeComma(event){
  const commaValue = commaContractAmount.value;
  const newValue = commaValue.replace(/,/g, "");
  commaContractAmount.value = newValue;

  const commaDriverValue = commaDriverPay.value;
  const newDriverValue = commaDriverValue.replace(/,/g, "");
  commaDriverPay.value = newDriverValue;
  
}




function getCommaValueDriverPay() {
  const commaValue = commaDriverPay.value;
  const newValue = commaValue.toString()
    .replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",");
    commaDriverPay.value = newValue;
}

function returnCommaValueDriverPay(){
  const commaValue = commaDriverPay.value;
  const newValue = commaValue.replace(/,/g, "");
  commaDriverPay.value = newValue;  
}

// btn.addEventListener("submit", removeComma)







const contractAmount = document.querySelector("#contractAmount");
const driverPay = document.querySelector("#driverPay");
const vehicleNumber = document.querySelector("#vehicleNumber");


contractAmount.addEventListener("input", canNotTextContractAmount)
driverPay.addEventListener("input", canNotTextDriverPay)
vehicleNumber.addEventListener("input", canNotTextVehicleNumber)
vehicleNumber.addEventListener("focusout", canNotNumber0VehicleNumber)

function canNotTextContractAmount() {
  contractAmount.value = contractAmount.value.replace(/[^0-9.]/g, '').replace(/(\..*)\./g, '$1');
}
function canNotTextDriverPay() {
  driverPay.value = driverPay.value.replace(/[^0-9.]/g, '').replace(/(\..*)\./g, '$1');
}
function canNotTextVehicleNumber() {
  vehicleNumber.value = vehicleNumber.value.replace(/[^0-9.]/g, '').replace(/(\..*)\./g, '$1');
}

function canNotNumber0VehicleNumber(){
  if(vehicleNumber.value == 0){
    alert("1이상의 숫자를 입력해 주세요");
  vehicleNumber.value = "";
  }
}
