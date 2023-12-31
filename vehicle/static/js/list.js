const openCrete = document.querySelector(".addVehicle")
const popupAreaModules = document.querySelectorAll(".popupAreaModules")
const popupBgModules = document.querySelectorAll(".popupBgModules")
const SidemenuUseClose = document.querySelector(".Sidemenu")
const PopupCloseBtn = document.querySelectorAll(".PopupBtnBox div:nth-child(1)")
const openDetail = document.querySelectorAll(".tableBody td:nth-child(2)")
const editBtn = document.querySelector(".editBtn")
const saveBtn = document.querySelector(".saveBtn")
const PopupTitle = document.querySelectorAll(".PopupTitle")
const PopupDataAreaDetail = document.querySelector(".PopupDataAreaDetail")
const PopupDataAreaEdit = document.querySelector(".PopupDataAreaEdit")
const checkBox = document.querySelectorAll(".tableBody input")
const vehicleListForm = document.querySelector(".vehicleListForm")
const PopupData = document.querySelectorAll(".PopupData")
const vehicleNum1 = document.querySelector(".vehicleNum1")
const vehicleNum2 = document.querySelector(".vehicleNum2")
const driver_name = document.querySelectorAll(".driver_name option")
const use = document.querySelectorAll(".use option")
const maker = document.querySelector(".maker")
const vehicle_type = document.querySelector(".vehicle_type")
const vehicle_id = document.querySelector(".vehicle_id")
const model_year = document.querySelector(".model_year")
const release_date = document.querySelector(".release_date")
const passenger_num = document.querySelector(".passenger_num")
const motor_type = document.querySelector(".motor_type")
const rated_output = document.querySelector(".rated_output")
const inspection_duration = document.querySelector(".inspection_duration")
const check_duration = document.querySelector(".check_duration")
const fileBox = document.querySelector("#vehicleFile")
const fileBox2 = document.querySelector("#insuranceFile")
const fileNameBox = document.querySelectorAll(".fileNameBox")
const sendToHidden = document.querySelector(".sendToHidden")
const fileDeletBtn = document.querySelectorAll(".fileDeletBtn")


//등록팝업 열기
openCrete.addEventListener("click", openCreatePopup)

function openCreatePopup() {
    popupAreaModules[0].style.display = "block"
}



//팝업닫기
for (i = 0; i < popupAreaModules.length; i++) {
    popupBgModules[i].addEventListener("click", closePopup)
    PopupCloseBtn[i].addEventListener("click", closePopup)
}
SidemenuUseClose.addEventListener("click", closePopup)

function closePopup() {
    for (i = 0; i < popupAreaModules.length; i++) {
        popupAreaModules[i].style.display = "none"
    }
    PopupDataAreaDetail.style.display = "flex"
    PopupDataAreaEdit.style.display = "none"
    PopupTitle[1].innerText = "차량상세"
    editBtn.style.display = "flex";
    saveBtn.style.display = "none";
}



//상세팝업 열기
for (i = 0; i < openDetail.length; i++) {
    openDetail[i].addEventListener("click", openDetailPopup)
}

function openDetailPopup() {
    popupAreaModules[1].style.display = "block"
    PopupData[0].innerText = regDatas[this.className].vehicle_num0
    PopupData[1].innerText = regDatas[this.className].vehicle_num
    PopupData[2].innerText = regDatas[this.className].driver_name
    PopupData[3].innerText = regDatas[this.className].use
    PopupData[4].innerText = regDatas[this.className].maker
    PopupData[5].innerText = regDatas[this.className].vehicle_type
    PopupData[6].innerText = regDatas[this.className].vehicle_id
    PopupData[7].innerText = regDatas[this.className].model_year
    PopupData[8].innerText = regDatas[this.className].release_date
    PopupData[9].innerText = regDatas[this.className].passenger_num
    PopupData[10].innerText = regDatas[this.className].motor_type
    PopupData[11].innerText = regDatas[this.className].rated_output
    PopupData[12].innerText = regDatas[this.className].inspection_duration
    PopupData[13].innerText = regDatas[this.className].check_duration
    PopupData[14].innerText = regDatas[this.className].vehicle_registration
    PopupData[15].innerText = regDatas[this.className].insurance_receipt
    vehicleNum1.value = regDatas[this.className].vehicle_num0
    vehicleNum2.value = regDatas[this.className].vehicle_num
    for (i = 0; i < driver_name.length; i++) {
      if (driver_name[i].innerText == regDatas[this.className].driver_name) {
        driver_name[i].selected = true;
      }
    }
    for (i = 0; i < use.length; i++) {
      if (use[i].innerText == regDatas[this.className].use) {
        use[i].selected = true;
      }
    }
    maker.value = regDatas[this.className].maker
    vehicle_type.value = regDatas[this.className].vehicle_type
    vehicle_id.value = regDatas[this.className].vehicle_id
    model_year.value = regDatas[this.className].model_year
    release_date.value = regDatas[this.className].release_date
    passenger_num.value = regDatas[this.className].passenger_num
    motor_type.value = regDatas[this.className].motor_type
    rated_output.value = regDatas[this.className].rated_output
    inspection_duration.value = regDatas[this.className].inspection_duration
    check_duration.value = regDatas[this.className].check_duration
    fileNameBox[0].value = regDatas[this.className].vehicle_registration
    fileNameBox[1].value = regDatas[this.className].insurance_receipt
    sendToHidden.value = this.parentNode.className;
  }


//상세->수정
editBtn.addEventListener("click", changeEdit)

function changeEdit() {
    PopupDataAreaDetail.style.display = "none"
    PopupDataAreaEdit.style.display = "flex"
    PopupTitle[1].innerText = "차량수정"
    editBtn.style.display = "none";
    saveBtn.style.display = "flex";
}



//삭제알림
let checkCounte = false;

for (i = 0; i < checkBox.length; i++) {
  checkBox[i].addEventListener('change', checking)
}

function checking() {
  checkCounte = false
  for (i = 0; i < checkBox.length; i++) {
    if (checkBox[i].checked) {
      checkCounte = true
    }
  }
}


vehicleListForm.addEventListener('submit', deleteData)

function deleteData(e) {
  if (!checkCounte) {
    e.preventDefault()
    alert('삭제할 차량을 선택해 주세요.')
  }
}


//파일
fileBox.addEventListener("change", fileName)

function fileName(){
  fileNameBox[0].value = fileBox.files[0].name
}

fileBox2.addEventListener("change", fileName2)

function fileName2(){
  fileNameBox[1].value = fileBox2.files[0].name
}


  fileDeletBtn[0].addEventListener('click', deletFile1)
  fileDeletBtn[1].addEventListener('click', deletFile2)


function deletFile1() {
  fileNameBox[0].value = ""
}

function deletFile2() {
  fileNameBox[1].value = ""
}
