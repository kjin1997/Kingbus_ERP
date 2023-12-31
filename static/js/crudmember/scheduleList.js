const scheduleListCloseBtn = document.querySelector(".scheduleListCloseBtn")
const scheduleListTable = document.querySelector(".scheduleListForm tbody")
const checkboxAll = document.querySelector(".scheduleListForm thead input[type=checkbox]")
const createDate = document.querySelector(".scheduleCreateBox input[type=hidden]")
const scheduleContents = document.querySelector(".scheduleContents")


function openScheduleList() {
    popupAreaModules[2].style.display = "block"
    let targetSchedule = this.parentNode.parentNode.parentNode.children[0].children[0].innerText - 1
    let scheduleDate = ""
    if (targetSchedule + 1 < 10) {
        scheduleDate = `${dateTitle.innerText.split("년")[0]}-${dateTitle.innerText.split("년 ")[1].replace(/\월/g, "")}-0${targetSchedule + 1}`
    } else {
        scheduleDate = `${dateTitle.innerText.split("년")[0]}-${dateTitle.innerText.split("년 ")[1].replace(/\월/g, "")}-${targetSchedule + 1}`
    }
    createDate.value = scheduleDate
    
    
    for (i = 0; i < scheduleList[targetSchedule].length; i++) {
        const schedulTr = document.createElement("tr")
        schedulTr.setAttribute("class", "table-list_body-tr")
        scheduleListTable.appendChild(schedulTr)

        const scheduleCheckboxTd = document.createElement("td")
        scheduleCheckboxTd.setAttribute("class", "table-list_body-tr_td")
        schedulTr.appendChild(scheduleCheckboxTd)

        const scheduleCheckbox = document.createElement("input")
        scheduleCheckbox.setAttribute("type", "checkbox")
        scheduleCheckbox.setAttribute("name", "check")
        scheduleCheckbox.setAttribute("value", `${scheduleList[targetSchedule][i].id}`)
        scheduleCheckboxTd.appendChild(scheduleCheckbox)

        const scheduleNum = document.createElement("td")
        scheduleNum.setAttribute("class", "table-list_body-tr_td")
        scheduleNum.innerText = i + 1
        schedulTr.appendChild(scheduleNum)

        const scheduleContent = document.createElement("td")
        scheduleContent.setAttribute("class", "table-list_body-tr_td")
        scheduleContent.innerText = scheduleList[targetSchedule][i].content
        schedulTr.appendChild(scheduleContent)

        const scheduleCreator = document.createElement("td")
        scheduleCreator.setAttribute("class", "table-list_body-tr_td")
        scheduleCreator.innerText = scheduleList[targetSchedule][i].creator
        schedulTr.appendChild(scheduleCreator)

        const scheduleDate = document.createElement("td")
        scheduleDate.setAttribute("class", "table-list_body-tr_td")
        scheduleDate.innerText = scheduleList[targetSchedule][i].date
        schedulTr.appendChild(scheduleDate)
    };

    const checkbox = document.querySelectorAll("input[name=check]")

    checkboxAll.addEventListener("change", checkAll)

    function checkAll() {
        if (checkboxAll.checked) {
            for (i = 0; i < checkbox.length; i++) {
                checkbox[i].checked = true;
            };
        } else {
            for (i = 0; i < checkbox.length; i++) {
                checkbox[i].checked = false;
            };
        }
    }

    for (i = 0; i < checkbox.length; i++) {
        checkbox[i].addEventListener("change", checkOneToAll)
    };


    function checkOneToAll() {
        let checkCount = 0
        for (i = 0; i < checkbox.length; i++) {
            if (checkbox[i].checked) {
                checkCount++
            }
        }
        if (checkbox.length === checkCount) {
            checkboxAll.checked = true
        } else {
            checkboxAll.checked = false
        }
    }
}

popupBgModules[2].addEventListener("click", closeScheduleList)
SidemenuUseClose.addEventListener("click", closeScheduleList)
scheduleListCloseBtn.addEventListener("click", closeScheduleList)

function closeScheduleList() {
    popupAreaModules[2].style.display = "none"
    createDate.value = ""
    scheduleContents.value = ""
}

function createSchaduleList() {
    let parms = new URLSearchParams(location.search)
    let beforeDayCount = 0
    if (!parms.has("change")) {
        for (i = 0; i < calenderDateBox.length; i++) {
            if (!calenderDateBox[i].classList.contains("beforeMonth") && !calenderDateBox[i].classList.contains("afterMonth")) {

                const dataCellCalender = calenderDateBox[i].querySelector(".dataCellCalender")

                for (j = 0; j < scheduleList[i - beforeDayCount].length; j++) {
                    if (j <= 2) {
                        const createSchdule = document.createElement("div")
                        createSchdule.setAttribute("class", "calnderItem")
                        createSchdule.innerText = scheduleList[i - beforeDayCount][j].content
                        dataCellCalender.appendChild(createSchdule)
                    } else {
                        const createSchduleMore = document.createElement("div")
                        createSchduleMore.setAttribute("class", "moreCalender")
                        createSchduleMore.innerText = `+${Object.keys(scheduleList[i - beforeDayCount]).length - 3}`
                        dataCellCalender.appendChild(createSchduleMore)
                        return
                    }
                }

            } else if (calenderDateBox[i].classList.contains("beforeMonth")) {
                beforeDayCount++
            }
        };
    }
}

createSchaduleList()



scheduleContents.addEventListener("input", scheduleValidation)

function scheduleValidation() {
    if (this.value.length > 99) {
        alert("최대 입력 글자수를 초과하였습니다.(100자)")
        this.value = this.value.substr(0, 99);
    }
}